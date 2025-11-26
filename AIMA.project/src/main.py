from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from meeting_api import run_meeting_pipeline
import pymysql, json
import uvicorn


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/wav_list")
def get_wav_list():
    files = [f for f in os.listdir("wav.file") if f.endswith(".wav")]
    return {"files": files}

@app.post("/analyze_meeting")
async def analyze_meeting(request: Request):
    data = await request.json()
    filename = data.get("filename")
    audio_path = os.path.join("wav.file", filename)
    if not os.path.exists(audio_path):
        return JSONResponse({"error": "파일을 찾을 수 없습니다."}, status_code=404)

    result = run_meeting_pipeline(audio_path)
    return JSONResponse(result)

# ✅ 담당자/기한 수정 반영용 엔드포인트
@app.post("/api/update_action_item")
async def update_action_item(request: Request):
    item = await request.json()
    try:
        conn = pymysql.connect(
            host="112.175.29.231",
            user="cheolwoo",
            password="1234",
            database="meeting_summary2",
            port=33067,
            charset="utf8mb4"
        )
        cur = conn.cursor()
        cur.execute("""
        UPDATE meeting_summary
        SET action_items = %s
        WHERE meeting_file = %s
        """, (
            json.dumps(item.get("updated_items"), ensure_ascii=False),
            item.get("meeting_file")
        ))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5883, reload=True)
