import os, re, json, torch, whisper, dateparser
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from pprint import pprint

# ===================== 1. 모델 및 환경 준비 =====================

# ⚠️ GPT 모델 사용을 위한 API 키는 필요합니다.
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


AUDIO_FILE = "wav.file/10월 26일 회의록.wav"

torch.cuda.empty_cache()
print("✅ 환경 준비 완료")

# ===================== 2. 데이터 구조 정의 (액션 아이템만) =====================

class ActionItem(BaseModel):
    name: str = Field(..., description="담당자 이름")
    task: str = Field(..., description="할 일")
    due: Optional[str] = Field(None, description="YYYY-MM-DD 또는 null")

# ===================== 3. Whisper STT (음성 인식) =====================

# 🎙️ Whisper 모델은 여전히 필요합니다.
model = whisper.load_model("large-v3")
print("🎙️ Whisper 변환 중...")

if not os.path.exists(AUDIO_FILE):
    raise FileNotFoundError(f"❌ 파일 없음: {AUDIO_FILE}")

result = model.transcribe(AUDIO_FILE, language="ko")
full_text = result["text"].strip()
print("✅ 변환 완료. 텍스트 미리보기:\n", full_text[:300])


# ===================== 4. 기본 함수 정의 (Ollama 지원 및 JSON 처리) =====================

def safe_llm_json(llm, prompt_text, retries=2):
    """LLM이 JSON을 깨뜨리면 자동 재시도"""
    for i in range(retries + 1):
        resp = llm.invoke(prompt_text)
        text = resp.content.strip()
        # JSON 본문만 추출
        json_part = re.search(r'\{[\s\S]*\}', text)
        if not json_part:
            print(f"⚠️ JSON 본문 미검출 ({i+1}/{retries+1}) → 재시도")
            continue
        try:
            return json.loads(json_part.group(0))
        except json.JSONDecodeError:
            print(f"⚠️ JSON 파싱 실패 ({i+1}/{retries+1}) → 재시도")
            # 프롬프트에 JSON만 출력하도록 재요청
            prompt_text += "\n\nJSON 외 문장은 절대 출력하지 말고 유효한 JSON만 응답하세요."
    raise ValueError("❌ LLM이 유효한 JSON을 생성하지 못했습니다.")


def normalize_due(due_text: Optional[str], base_dt: datetime) -> Optional[str]:
    """상대 날짜를 YYYY-MM-DD로 정규화."""
    if not due_text: return None

    s = str(due_text).strip()
    current_year = base_dt.year

    # YYYY-MM-DD 형식 이미 충족 시
    if re.match(r"\d{4}-\d{2}-\d{2}", s):
        try: return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError: return None

    if s in {"미정", "불명", "null", "없음", ""}: return None
    if s in {"오늘", "오늘 중"}: return base_dt.strftime("%Y-%m-%d")
    if s == "내일": return (base_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    # dateparser를 사용하여 날짜 파싱
    parsed = dateparser.parse(
        s,
        languages=["ko"],
        settings={"RELATIVE_BASE": base_dt, "PREFER_DATES_FROM": "past"},
    )
    
    if any(word in s for word in ["내일", "다음", "이번 주", "이번주", "까지"]):
        parsed_future = dateparser.parse(
            s,
            languages=["ko"],
            settings={"RELATIVE_BASE": base_dt, "PREFER_DATES_FROM": "future"},
        )
        if parsed_future: parsed = parsed_future

    if parsed:
        if parsed.year < current_year and parsed.date() < base_dt.date():
            parsed = parsed.replace(year=current_year + 1)
        elif parsed.year < current_year:
            parsed = parsed.replace(year=current_year)
            
        return parsed.strftime("%Y-%MM-%d")

    return None


def extract_actions_and_normalize(llm_model_name: str, action_candidates: List[str], base_dt: datetime):
    """특정 LLM 모델을 사용하여 액션 아이템을 추출하고 날짜를 정규화하는 함수"""
    print(f"\n--- 🧠 {llm_model_name} 모델로 액션 아이템 추출 시작 ---")
    
    # 🌟 모델 계열에 따라 Chat 클래스 선택
    if "gpt" in llm_model_name:
        llm = ChatOpenAI(model_name=llm_model_name, temperature=0)
    elif "ollama" in llm_model_name:
        # 'ollama-' 접두사를 제거하고 Ollama 모델 이름으로 ChatOllama 인스턴스 생성
        ollama_model = llm_model_name.replace("ollama-", "")
        llm = ChatOllama(model=ollama_model, temperature=0)
    else:
        print(f"❌ 지원되지 않는 모델 계열: {llm_model_name}. ChatOpenAI로 대체합니다.")
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # Ollama 모델에 적합한 JSON 추출 프롬프트 (JSON만 출력하도록 강조)
    fallback_prompt = f"""
    너는 회의 중 액션아이템을 추출하는 역할을 합니다.
    **다른 설명이나 문장 없이, 오직 유효한 JSON 형식으로만 응답해야 합니다.**
    아래 문장들에서 담당자(name), 할 일(task), 기한(due)을 추출하여 JSON 배열로 만드세요.
    기한이 없으면 'null'로 둡니다. 'due'는 상대적인 날짜 표현을 그대로 유지하세요.
    
    출력 형식:
    {{
      "action_items": [
        {{"name": "담당자", "task": "할 일", "due": "기한 텍스트 or null"}}
      ]
    }}
    
    문장:
    {json.dumps(action_candidates, ensure_ascii=False, indent=2)}
    """
    
    try:
        # 여기서 LLM 호출
        fallback_json = safe_llm_json(llm, fallback_prompt)
    except ValueError as e:
        print(f"❌ {llm_model_name} 액션 아이템 추출 실패: {e}")
        return []

    action_items = fallback_json.get("action_items", [])
    
    # 날짜 정규화
    for item in action_items:
        due_raw = item.get("due")
        if due_raw:
            clean_due = re.sub(r'(까지|중|부터)', '', str(due_raw))
            clean_due = re.sub(r'(다음주)([월화수목금토일])', r'\1 \2', clean_due)
            item["due"] = normalize_due(clean_due, base_dt)
            
    print(f"✅ {llm_model_name} 액션 아이템 {len(action_items)}개 추출 완료")
    return action_items


# ===================== 5. 액션아이템 후보 탐지 =====================

action_candidates = []
for line in full_text.split("\n"):
    # 액션 아이템이 될 가능성이 있는 문장만 필터링
    if any(k in line for k in ["까지", "해야", "결정", "완료", "진행", "작성", "검토"]):
        action_candidates.append(line.strip())

print(f"\n📋 액션 문장 후보 {len(action_candidates)}개 탐지됨")

# ===================== 6. 모델별 액션 아이템 추출 및 비교 =====================

base_dt = datetime.now()

# 🧪 모델 A: gpt-4o-mini (클라우드/유료 비교군)
MODEL_A = "gpt-4o-mini"
action_items_A = extract_actions_and_normalize(MODEL_A, action_candidates, base_dt)

# 🧪 모델 B: Ollama (로컬/무료 비교군)
# 🌟 사용자님의 Ollama list 결과에 맞춰 태그 변경: exaone3.5:7.8b
MODEL_B = "ollama-exaone3.5:7.8b" 
action_items_B = extract_actions_and_normalize(MODEL_B, action_candidates, base_dt)


# ===================== 7. 최종 결과 비교 및 밸리데이션 =====================

# gpt-4o-mini 결과를 최종으로 선택하고, Ollama 결과와 비교 출력
final_action_items = action_items_A

print("\n" + "="*50)
print("🎯 액션 아이템 추출 결과 비교")
print("="*50)

print(f"\n[모델 A: {MODEL_A} - {len(action_items_A)}개]")
pprint(action_items_A, indent=4)

print(f"\n[모델 B: {MODEL_B} - {len(action_items_B)}개]")
pprint(action_items_B, indent=4)
print("\n" + "="*50)

try:
    # ActionItem 클래스를 사용하여 데이터 구조 밸리데이션 (모델 A 기준)
    validated_items = [ActionItem(**item) for item in final_action_items]
    print(f"\n✅ 밸리데이션 통과 (최종 사용 모델: {MODEL_A}) - 추출된 액션 아이템 {len(validated_items)}개")
except ValidationError as e:
    print("❌ 밸리데이션 실패:", e)
    raise

print("\n--- 최종 결과 JSON (gpt-4o-mini 기준) ---")
print(json.dumps([item.model_dump() for item in validated_items], indent=4, ensure_ascii=False))
