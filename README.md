실습1. 대용량 로그 스트리밍 집계
STEP 0. 데이터 형태 확인
<p align="left">
    <img src="exec/0001.jpg" width="49%" alt="1-1">
</p>

STEP 1. 파일 -> 딕셔너리 제너레이터
<p align="left">
    <img src="exec/0002.jpg" width="49%" alt="1-2">
</p>

STEP 2 + 3. 집계 코드 작성
<p align="left">
    <img src="exec/0003.jpg" width="49%" alt="1-3">
</p>

STEP 4. 5xx 비율 계산
<p align="left">
    <img src="exec/0004.jpg" width="49%" alt="1-4">
</p>

STEP 5. fold 패턴
<p align="left">
    <img src="exec/0005.jpg" width="49%" alt="1-5">
</p>

STEP 6. 리포트 및 상위 IP 출력
<p align="left">
    <img src="exec/0006.jpg" width="49%" alt="1-6">
</p>

---

실습2 . Pydantic v2 중첩 스키마 검증
STEP 0  ·  오염 데이터 확인
<p align="left">
    <img src="exec/0007.jpg" width="49%" alt="2-1">
</p>
- 7번 유저 : 나이가 음수값(-5)로 설정됨
- 13번 유저 : 이메일 값이 "not-an-email"으로 형식을 벗어남
- 21번 유저 : 이메일 태그 없음
- 29번 유저 : score가 150.0으로 100점 초과

STEP 1  ·  가장 단순한 모델 하나 만들기 (필드 2개만)
STEP 2  ·  범위·제약 조건 추가 — Field()
STEP 3  ·  커스텀 규칙 — field_validator
STEP 4  ·  중첩 구조 — 모델 안에 모델
STEP 5  ·  40건을 돌리며 유효/무효로 나누기 — 이 실습의 목적지
STEP 6  ·  탈락 사유를 표로 출력 (확장 과제)
