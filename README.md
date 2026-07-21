# 🚀 Python Data Processing & Asynchronous ETL Pipeline

이 프로젝트는 대용량 로그 처리부터 Pydantic 검증, asyncio 비동기 수집기, 그리고 비동기 ETL 파이프라인 구축 및 단위 테스트 실습 내용을 담고 있습니다.

---

## 🛠️ 목차
1. [실습 1. 대용량 로그 스트리밍 집계](#실습-1-대용량-로그-스트리밍-집계)
2. [실습 2. Pydantic v2 중첩 스키마 검증](#실습-2-pydantic-v2-중첩-스키마-검증)
3. [실습 3. asyncio 기반 비동기 수집기](#실습-3-asyncio-기반-비동기-수집기)
4. [실습 4. Pandas 2.x 데이터 정제]
5. [실습 5. Polars, DuckDB 성능 비교]
6. [종합 실습 1. 비동기 ETL 파이프라인](#종합-실습-1-비동기-etl-파이프라인)
7. [종합 실습 2. EDA + 통계 + ML 파이프라인]
8. [종합 실습 3. 분석 자동화 · 리포트 생성]
9. [추가 과제](#추가-과제)

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

## 실습 4. Pandas 2.x 데이터 정제
### STEP 0. 데이터 진단
<p align="left">
    <img src="exec/0034.jpg" width="80%" alt="4-1">
</p>
### STEP 1 ~ 5. 데이터 타입 정규화, 결측/이상치 처리, groupby.agg 집계, pivot_table
<p align="left">
    <img src="exec/0035.jpg" width="80%" alt="4-2">
</p>
### STEP 6. 집계 3) merge — 다른 표와 결합
<p align="left">
    <img src="exec/0036.jpg" width="80%" alt="4-3">
</p>

---

## 실습 5. Polars, DuckDB 성능 비
### STEP 0. 비교할 '질의' 하나 선정
- 세 엔진이 똑같은 일을 해야 비교 성립

### STEP 1. 기준선 만들기 - Pandas
<p align="left">
    <img src="exec/0045.jpg" width="80%" alt="5-1">
</p>

### STEP 2. 기준선 만들기 - Polars Lazy - scan_csv + collect
<p align="left">
    <img src="exec/0046.jpg" width="80%" alt="5-1">
</p>
### STEP 3. DuckDB 버전 — SQL로 파일 직접 조회
<p align="left">
    <img src="exec/0047.jpg" width="80%" alt="5-1">
</p>
### STEP 4 ~ 5. ★ 결과 일치 검증 ★ +  벤치마크 표로 정리
<p align="left">
    <img src="exec/0036.jpg" width="80%" alt="5-1">
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

## 종합 실습 2. EDA + 통계 + ML 파이프라인
### STEP 0. EDA
<p align="left">
    <img src="exec/0039.jpg" width="80%" alt="종합 2-1">
</p>

### STEP 1 ~ 3. 이탈 그룹 vs 잔류 그룹 비교 (가설 세우기), Plotly 로 시각화 → HTML 리포트, 통계 검정
<p align="left">
    <img src="exec/0040.jpg" width="80%" alt="종합 2-2">
</p>
- t-검정 p = 1.23e - 20
- 카이제곱 p = 1.32e - 70

### STEP 7. 평가 — 왜 정확도가 아니라 ROC-AUC 인가
<p align="left">
    <img src="exec/0041.jpg" width="80%" alt="종합 2-3">
</p>
- ROC-AUC = 0.667

---

## 종합 실습 3. 분석 자동화 · 리포트 생성
### STEP 0. config.py
<p align="left">
    <img src="exec/0042.jpg" width="80%" alt="종합 3-1">
</p>

### STEP 3. 렌더링 — 데이터를 템플릿에 부어넣기
<p align="left">
    <img src="exec/0043.jpg" width="80%" alt="종합 3-2">
</p>

### STEP 4. 실행 방식 1) 경량 루프 (의존성 0)
<p align="left">
    <img src="exec/0044.jpg" width="80%" alt="종합 3-3">
</p>

### STEP 5. 실행 방식 2) schedule 라이브러리 (선언적)
<p align="left">
    <img src="exec/0048.jpg" width="80%" alt="종합 3-4">
</p>

### STEP 6. 실행 방식 3) OS cron (운영 환경 · 무인 실행)
- cron 없어서 패스

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

### 3. 실습 4 확장 과제 — 정제 규칙을 함수로 만들고 테스트 붙이기
<p align="left">
    <img src="exec/0038.jpg" width="80%" alt="추가 1-3">
</p>
- advanced/cleaner.py
- advanced/test_cleaner.py

