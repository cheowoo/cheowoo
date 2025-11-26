#  AI 기반 회의록 요약 시스템

Whisper Large v3로 음성 데이터를 텍스트로 변환하고 GPT 모델을 활용해 요약·의사결정 정리·액션아이템 추출까지 수행하는  **AI 회의록 자동화 시스템**입니다.
최종 결과는 JSON 형태로 DB에 저장되며 회의록을 쉽게 찾아 볼수 있게 docx 생성과 FastAPI 기반으로 API 서버를 구축하여 외부 서비스와 연동했습니다.

---
# 프로젝트를 하게 된 배경 
여전히 많은 회사는 회의록을 수작업으로 많이 작성하고주요 결정사항과 할 일은 잊혀지기 쉽다는 관점
AI 기술을 활용한 스마트 회의 시스템으로 이러한 문제점들을 근본적으로 개선
```
프로젝트 구조
project/
├── static/
│ ├── css/ # 스타일 파일
│ ├── data/ # JSON 등 데이터 파일
│ ├── docs/ # 문서, 참고 자료
│ └── js/ # 프론트엔드 스크립트
│
├── src/
│ ├── cer.py # CER 계산 및 문자 단위 검증
│ ├── generate_mock_meeting.py # 회의 Mock 데이터 생성 스크립트
│ ├── main.py # FastAPI 서버 실행 진입점
│ └── meeting_api.py # STT + LLM 기반 회의요약 처리 로직
│
└── README.md
```

---

##  기술 스택

###  Speech-to-Text
- **OpenAI Whisper Large v3**
- 한국어 회의 음성을 고정밀 텍스트로 변환

###  NLP 모델링
- GPT 모델 활용
  - 회의 요약
  - 주요 결정사항 추출
  - Action Item 분리
  - 발언자별 요약

###  데이터 저장 구조
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

```


### 웹페이지 화면
<img width="1051" height="453" alt="스크린샷 2025-11-27 005641" src="https://github.com/user-attachments/assets/ae5f2c7a-4629-4951-9970-81f312ac0ad4" />

### DB
<img width="1749" height="572" alt="스크린샷 2025-11-25 105603" src="https://github.com/user-attachments/assets/baef93ce-1b9a-412a-abb2-49a11e6f684b" />

### docx 회의록
<img width="633" height="782" alt="image" src="https://github.com/user-attachments/assets/8250c684-c163-496b-bca3-785e1c56f7d1" />


