from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
file_path = DATA_DIR / "sales_raw.csv"

def print_header(str):
  print("\n")
  print("=" * 40)
  print(str)
  print("=" * 40)

def func0(df):
  print(df.shape)              # (5000, N) — 행/열 개수
  print(df.info())             # ★ 각 컬럼의 타입과 결측 개수
  print(df.describe())         # 수치형 요약 (min/max에서 이상치 냄새)
  print(df.isna().sum())       # ★ 컬럼별 결측 개수
  print(df.head())             # 실제 값 눈으로 확인

  # 여기서 확인할 것:
  #  - price 가 object(문자열)로 잡혀 있진 않은가?  → 타입 불일치
  #  - max 값이 비정상적으로 크지 않은가?          → 이상치
  #  - 어느 컬럼에 결측이 몇 개인가?                → 결측

def func1(df):
  # 문자열 → 숫자 (실패한 값은 NaN 으로)
  df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
  df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

  # 문자열 → 날짜
  df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

  # 범주형은 category 타입으로 (메모리 절약 + 속도)
  df['category'] = df['category'].astype('category')

  print(df.dtypes)             # 의도한 타입으로 바뀌었는지 확인

def func2(df):
  # ✅ 그룹별 중앙값으로 채우기
  df['unit_price'] = df.groupby('category', observed=True)['unit_price'] \
                  .transform(lambda s: s.fillna(s.median()))

  print(df['unit_price'].isna().sum())      # 0 이 되어야 함

def winsorize(s, k=1.5):
  q1, q3 = s.quantile(0.25), s.quantile(0.75) # 이상치 경계값
  iqr = q3 - q1
  low, high = q1 - k * iqr, q3 + k * iqr
  return s.clip(lower=low, upper=high)   # ★ 삭제가 아니라 '끌어당기기'

def func4(df):
  summary = df.groupby('category', observed=True).agg(
    건수=('unit_price', 'count'),
    평균가=('unit_price', 'mean'),
    중앙값=('unit_price', 'median'),
    총매출=('unit_price', 'sum'),
  ).round(1)
  print(summary)

def func5(df):
  pivot = df.pivot_table(
    index='category',       # 세로축
    columns='region',       # 가로축
    values='unit_price',
    aggfunc='sum',
    fill_value=0,           # 빈 칸은 0으로
  )

  print(pivot)

def func6(df):
  # 행이 줄어드는 걸 확인하기 위한 임시 other_df 생성
  other_df = pd.DataFrame({
    'order_id': ['ORD-000000', 'ORD-000001', 'ORD-000002'],
    'customer_name': ['김철수', '이영희', '박민수'],
    'payment_method': ['신용카드', '카카오페이', '계좌이체']
  })

  # how 를 잘못 고르면 데이터가 조용히 사라집니다
  merged = df.merge(other_df, on='order_id', how='left')
  
  #  how='inner' : 양쪽 다 있는 것만        (행이 줄 수 있음 ⚠️)
  #  how='left'  : 왼쪽 전부 유지 (기본 권장)
  #  how='outer' : 양쪽 전부 유지
  
  # ★ merge 후에는 반드시 행 수 확인!
  merged_left = df.merge(other_df, on='order_id', how='left')
  print(f"[how='left'] 원래 행 수: {len(df)} → 병합 후 행 수: {len(merged_left)}")
  
  merged_inner = df.merge(other_df, on='order_id', how='inner')
  print(f"[how='inner'] 원래 행 수: {len(df)} → 병합 후 행 수: {len(merged_inner)}")

def func7(df):
  # python 3.0 이상 버전부터 기본 활성화라 주석 처리
  # pd.options.mode.copy_on_write = True 
  
  # ✅ .loc 으로 한 번에 지정
  df.loc[df['unit_price'] > 100, 'flag'] = 1  
  
if(__name__) == "__main__":
  df = pd.read_csv(file_path)

  print_header("STEP 0. 데이터 파악")
  func0(df)
  
  print_header("STEP 1. 타입 정규화")
  func1(df)

  print_header("STEP 2. 결측 처리 - 그룹별 중앙값 대치")
  func2(df)

  print_header("STEP 3. 이상치 처리 - IQR 윈저라이징")
  print('처리 전 max:', df['unit_price'].max())
  df['unit_price'] = winsorize(df['unit_price'])
  print('처리 후 max:', df['unit_price'].max())   # 상한선까지 눌린 것을 확인

  print_header("STEP 4. 집계(1) groupby.agg - 그룹별 요약")
  func4(df)

  print_header("STEP 5. 집계(2) pivot_table - 교차표")
  func5(df)

  print_header("STEP 6. 집계(3) merge - 다른 표와 결합")
  func6(df)

  print_header("STEP 7. Copy-on-Write 이해하기")
  func7(df)