
import whisper

# 1. Whisper 모델 로드
model = whisper.load_model("large-v3")

# 2. 음성 파일 변환 실행 (너의 mock 파일)
AUDIO_FILE = "wav.file/10월 29일 회의록.wav"
result = model.transcribe(AUDIO_FILE, language="ko")

# 3. 변환된 텍스트 확인
print(result["text"])   # 👈 여기가 whisper_result 값이야

# 4. CER 계산
from jiwer import cer

ground_truth = """철우: 네, 모두 수고 많았습니다. 오늘은 10월 28일, 모델 성능 평가와 통합 테스트 결과를 공유하겠습니다.  

윤성: 새로운 데이터셋으로 학습한 결과, 정확도가 93.1%까지 올랐습니다. 감정 분류 안정성도 좋아졌어요. 다만 테스트 세트에 중복 문장이 일부 있어서 금요일까지 다시 정제하겠습니다.  

정우: 라벨 불일치 12건 수정했습니다. 인코딩 문제였어요. 오늘 중으로 수정본을 푸시하고 깃헙에 업로드하겠습니다.  

창용: 배포 자동화는 완성됐습니다. push 이벤트마다 Docker 컨테이너가 재시작돼요. 평균 배포 시간도 40초로 단축됐습니다. 내일까지 로그 시각화 기능을 추가하겠습니다.  

소라: UI 렌더링 속도가 조금 느렸는데, DOM 구조를 정리해서 개선 중이에요. 이번 금요일까지 최종 수정 버전 올리겠습니다.  

용재: SSL 인증서 자동 갱신 테스트 완료했습니다. cron 스케줄이 조금 불안정해서 내일까지 주기 재설정하고 결과 보고드리겠습니다.  

철우: 좋네요. 윤성은 데이터셋 정제 금요일까지, 정우는 라벨 수정 오늘 안에, 창용은 로그 시각화 내일까지, 소라는 UI 수정 금요일까지, 용재는 스케줄 재설정 내일까지 마무리해주세요. 내일은 요약 자동화 쪽 테스트 중심으로 회의 진행하겠습니다.
"""

whisper_result = result["text"]
score = cer(ground_truth, whisper_result)
print(result["text"][:500])
print("CER:", round(score*100, 2), "%")
