from langchain.prompts import PromptTemplate

# ===========================================
# 🎯 회의 요약 Few-shot Prompt (중괄호 이스케이프 버전)
# ===========================================
meeting_summary_prompt = PromptTemplate.from_template("""
당신은 'AI 회의 요약 비서'입니다.
다음 회의록 대화를 분석하여 **아래 JSON 형식**으로만 출력하세요.
다음 회의 대화 내용을 보고 회의가 실제로 열린 날짜를 추정하세요.
단, 반드시 **현재 연도({{current_year}})** 기준으로 작성하세요.

출력 예시:
{{ "meeting_date": "2025-10-27" }}

요구사항:
- "topic_summary": 회의의 핵심 주제를 한 문장으로 요약
- "content_summary": 회의 전반의 진행 내용, 논의 흐름, 이유 등을 5줄 이내로 정리
- "decisions": 회의 중 실제로 합의된 사항만을 항목별로 정리 (액션아이템과 중복 금지)
- "action_items": 각 참가자별 해야 할 일과 마감 기한을 정리
  - name: 사람 이름 (없으면 "담당자 미상")
  - task: 해야 할 일
  - due: 날짜 또는 "미정"

출력 예시:
{{
  "topic_summary": "UI 개선 및 모델 성능 향상 논의",
  "content_summary": " 모델 정확도 향상 방향 논의\\ Whisper 속도 개선 검토\\ UI 접근성 피드백 반영\\ 보안 로그 처리 점검\\ 차주 일정 확정",
  "decisions": [
    "Faster-Whisper 적용으로 속도 개선",
    "UI 시안은 수요일까지 공유",
    "암호화 기능 추가"
  ],
  "action_items": [
    {{"name": "소라",
    "task": "UI 시안 정리",
    "due": "2025-10-28"}},
    {{"name": "윤성",
    "task": "폰트 기능 추가",
    "due": "2025-10-29"}},
    {{"name": "정우",
    "task": "사용자 로그 분석",
    "due": "2025-10-30"}}
  ]
}}

회의록:
{text}
""")
