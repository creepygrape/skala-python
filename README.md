# 🚀 Python Data Processing & Asynchronous ETL Pipeline

이 프로젝트는 대용량 로그 처리부터 Pydantic 검증, asyncio 비동기 수집기, 그리고 비동기 ETL 파이프라인 구축 및 단위 테스트 실습 내용을 담고 있습니다.

---

## 🛠️ 목차
1. [실습 1. 대용량 로그 스트리밍 집계](#실습-1-대용량-로그-스트리밍-집계)
2. [실습 2. Pydantic v2 중첩 스키마 검증](#실습-2-pydantic-v2-중첩-스키마-검증)
3. [실습 3. asyncio 기반 비동기 수집기](#실습-3-asyncio-기반-비동기-수집기)
4. [종합 실습 1. 비동기 ETL 파이프라인](#종합-실습-1-비동기-etl-파이프라인)
5. [추가 과제](#추가-과제)

---

## 실습 1. 대용량 로그 스트리밍 집계

### STEP 0. 데이터 형태 확인
<p align="left">
    <img src="exec/0001.jpg" width="80%" alt="1-1">
</p>

### STEP 1. 파일 -> 딕셔너리 제너레이터
<p align="left">
    <img src="exec/0002.jpg" width="80%" alt="1-2">
</p>

### STEP 2 + 3. 집계 코드 작성
<p align="left">
    <img src="exec/0003.jpg" width="80%" alt="1-3">
</p>

### STEP 4. 5xx 비율 계산
<p align="left">
    <img src="exec/0004.jpg" width="80%" alt="1-4">
</p>

### STEP 5. fold 패턴
<p align="left">
    <img src="exec/0005.jpg" width="80%" alt="1-5">
</p>

### STEP 6. 리포트 및 상위 IP 출력
<p align="left">
    <img src="exec/0006.jpg" width="80%" alt="1-6">
</p>

---

## 실습 2. Pydantic v2 중첩 스키마 검증

### STEP 0 · 오염 데이터 확인
<p align="left">
    <img src="exec/0007.jpg" width="80%" alt="2-1">
</p>

- **7번 유저** : 나이가 음수값(-5)로 설정됨
- **13번 유저** : 이메일 값이 "not-an-email"으로 형식을 벗어남
- **21번 유저** : 이메일 태그 없음
- **29번 유저** : score가 150.0으로 100점 초과

### STEP 1 ~ 4. 모델 생성 및 규약 설정
<p align="left">
    <img src="exec/0027.jpg" width="80%" alt="2-2">
</p>

### STEP 5 · 40건을 돌리며 유효/무효로 나누기
<p align="left">
    <img src="exec/0008.jpg" width="80%" alt="2-3">
</p>

### STEP 6 · 탈락 사유를 표로 출력 (확장 과제)
<p align="left">
    <img src="exec/0009.jpg" width="80%" alt="2-4">
</p>

---

## 실습 3. asyncio 기반 비동기 수집기

### STEP 0. 동기 버전
<p align="left">
    <img src="exec/0010.jpg" width="80%" alt="3-1">
</p>

### STEP 1. async/await 비동기
<p align="left">
    <img src="exec/0011.jpg" width="80%" alt="3-2">
</p>

### STEP 2. gather로 60개 동시에 던지기
<p align="left">
    <img src="exec/0012.jpg" width="80%" alt="3-3">
</p>

### STEP 3. 백프레셔 — Semaphore 로 동시 요청 수 제한
<p align="left">
    <img src="exec/0013.jpg" width="80%" alt="3-4">
</p>

### STEP 4. 타임아웃 — 무한정 기다리지 않기
<p align="left">
    <img src="exec/0014.jpg" width="80%" alt="3-5">
</p>

### STEP 5. 재시도 — 지수 백오프(exponential backoff)
<p align="left">
    <img src="exec/0015.jpg" width="80%" alt="3-5">
</p>

### STEP 6. 예외 격리 — 하나 실패해도 전체는 살리기
<p align="left">
    <img src="exec/0026.jpg" width="80%" alt="3-6">
</p>

---

## 종합 실습 1. 비동기 ETL 파이프라인

### STEP 0 ~ 2. 테스트 점진적 접근(폴더 구조 > Transform > 테스트 코드)
<p align="left">
    <img src="exec/0016.jpg" width="80%" alt="종합 1-1">
</p>

### STEP 3 ~ 6. Extract, Load, Parquet 라운드 트립 + 테스트 코드
<p align="left">
    <img src="exec/0028.jpg" width="80%" alt="종합 1-2"><br>
    <img src="exec/0029.jpg" width="80%" alt="종합 1-3"><br>
    <img src="exec/0030.jpg" width="80%" alt="종합 1-4"><br>
    <img src="exec/0031.jpg" width="80%" alt="종합 1-5"><br>
    <img src="exec/0032.jpg" width="80%" alt="종합 1-6"><br>
    <img src="exec/0033.jpg" width="80%" alt="종합 1-7"><br>
    <img src="exec/0017.jpg" width="80%" alt="종합 1-8"><br>
    <img src="exec/0022.jpg" width="80%" alt="종합 1-9">
</p>

- `extract()` 위한 `mock_fetch` 추가
- `load()` : 데이터 csv, parquet 저장
- `save_dead_letters` : dead_letters 격리 및 기록

### STEP 7. Ruff 로 마무리
<p align="left">
    <img src="exec/0018.jpg" width="80%" alt="종합 1-10"><br>
    <img src="exec/0019.jpg" width="80%" alt="종합 1-11"><br>
    <img src="exec/0020.jpg" width="80%" alt="종합 1-12"><br>
    <img src="exec/0021.jpg" width="80%" alt="종합 1-13"><br>
    <img src="exec/0023.jpg" width="80%" alt="종합 1-14">
</p>

- 'True', 'False'로 바꿔야 ruff passed이나 잘못된 결과 나오므로 무시

---

## 추가 과제

### 1. tracemalloc
<p align="left">
    <img src="exec/0024.jpg" width="80%" alt="추가 1-1">
</p>

- readlines와 제너레이터 메모리 비교

### 2. dead_letters
<p align="left">
    <img src="exec/0025.jpg" width="80%" alt="추가 1-2">
</p>

- 실패 데이터 격리 및 json 기록
