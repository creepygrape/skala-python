import csv
import pandas as pd

file_path = 'data/sales_raw.csv'

df = pd.read_csv(file_path)
 
print(df.shape)              # (5000, N) — 행/열 개수
print(df.info())             # ★ 각 컬럼의 타입과 결측 개수
print(df.describe())         # 수치형 요약 (min/max에서 이상치 냄새)
print(df.isna().sum())       # ★ 컬럼별 결측 개수
print(df.head())             # 실제 값 눈으로 확인

print("=" * 40)
# 여기서 확인할 것:
#  - price 가 object(문자열)로 잡혀 있진 않은가?  → 타입 불일치
#  - max 값이 비정상적으로 크지 않은가?          → 이상치
#  - 어느 컬럼에 결측이 몇 개인가?                → 결측

# 문자열 → 숫자 (실패한 값은 NaN 으로)
df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
 
# 문자열 → 날짜
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
 
# 범주형은 category 타입으로 (메모리 절약 + 속도)
df['category'] = df['category'].astype('category')

### 추가 : 음수 가격 결측치로 변경
df.loc[df['unit_price'] < 0, 'unit_price'] = None
 
print(df.dtypes)             # 의도한 타입으로 바뀌었는지 확인
print("=" * 40)

# ✅ 그룹별 중앙값으로 채우기
df['unit_price'] = df.groupby('category', observed=True)['unit_price'] \
                .transform(lambda s: s.fillna(s.median()))

print(df['unit_price'].isna().sum())      # 0 이 되어야 함
print("=" * 40)

def winsorize(s, k=1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    return s.clip(lower=low, upper=high)   # ★ 삭제가 아니라 '끌어당기기'
 
print('처리 전 max unit_price:', df['unit_price'].max())
print('처리 전 max quantity:', df['quantity'].max())
df['unit_price'] = winsorize(df['unit_price'])
df['quantity'] = winsorize(df['quantity'])
print('처리 후 max unit_price:', df['unit_price'].max())   # 상한선까지 눌린 것을 확인
print('처리 후 max quantity:', df['quantity'].max())   # 상한선까지 눌린 것을 확인
print("=" * 40)

summary = df.groupby('category', observed=True).agg(
    건수=('unit_price', 'count'),
    평균가=('unit_price', 'mean'),
    중앙값=('unit_price', 'median'),
    총매출=('unit_price', 'sum'),
).round(1)
print(summary)
print("=" * 40)

pivot = df.pivot_table(
    index='category',       # 세로축
    columns='region',       # 가로축
    values='unit_price',
    aggfunc='sum',
    fill_value=0,           # 빈 칸은 0으로
)
print(pivot)
print("=" * 40)

# how 를 잘못 고르면 데이터가 조용히 사라집니다
merged = df.merge(df, on='order_id', how='left')
 
#  how='inner' : 양쪽 다 있는 것만        (행이 줄 수 있음 ⚠️)
#  how='left'  : 왼쪽 전부 유지 (기본 권장)
#  how='outer' : 양쪽 전부 유지
 
# ★ merge 후에는 반드시 행 수 확인!
print(len(df), '→', len(merged))
print("=" * 40)

# pd.options.mode.copy_on_write = True   # Pandas 2.x 권장 설정
 
# ✅ .loc 으로 한 번에 지정
df.loc[df['unit_price'] > 100, 'flag'] = 1





