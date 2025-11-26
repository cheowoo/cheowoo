# 📝 AI 기반 회의록 요약 시스템

Whisper Large v3로 음성 데이터를 텍스트로 변환하고  
GPT 모델을 활용해 요약·의사결정 정리·액션아이템 추출까지 수행하는  
**AI 회의록 자동화 시스템**입니다.

최종 결과는 JSON 형태로 DB에 저장되며 회의록을 쉽게 찾아 볼수 있게 docx 생성과
FastAPI 기반으로 API 서버를 구축하여 외부 서비스와 연동했습니다.

---

## 🚀 프로젝트 구조

📂 project  
 ├── static/  
 │    ├── css  
 │    ├── data
 │    ├── docs
 │    ├── js
 ├── src/                  
 │    ├── cer.py         # 문자단위 검증  
 │    ├── generate_mock_meeting.py   # 목데이터 생성  
 │    ├── main.py        # fastapi 서버  
 │    └── meeting_api.py # stt + llm 으로 회의요약
 ├── notebooks/  
 └── README.md

---

## 🔧 기술 스택

### 🎙 Speech-to-Text
- **OpenAI Whisper Large v3**
- 한국어 회의 음성을 고정밀 텍스트로 변환

### 🤖 NLP 모델링
- GPT 모델 활용
  - 회의 요약
  - 주요 결정사항 추출
  - Action Item 분리
  - 발언자별 요약

### 🗃 데이터 저장 구조
최종 요약은 아래 JSON 구조로 DB에 저장됩니다:

```json
{
  "meeting_title": "프로젝트 킥오프",
  "summary": "...",
  "decisions": ["..."],
  "action_items": [
    { "task": "...", "owner": "...", "due": "..." }
  ],
  "speakers_summary": {
    "speaker1": "...",
    "speaker2": "..."
  }
}
