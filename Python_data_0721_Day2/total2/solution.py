from pathlib import Path
import polars as pl
import pandas as pd
import plotly.express as px
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
file_path = DATA_DIR / "telco_churn.csv"

def print_header(str):
  print("\n")
  print("=" * 40)
  print(str)
  print("=" * 40)

df = pl.read_csv(file_path)

print_header("STEP 0. EDA")
print(df.shape)                       # (7000, N)
print(df.columns)
print(df.head())
print(df.describe())                  # 수치형 요약

# ★ 타깃(이탈 여부)의 비율 확인 — 가장 먼저 볼 것!
print(df.group_by('churn').len())
# 이탈 26% / 잔류 74% 같은 '불균형'이면 정확도(accuracy)는 못 씁니다
# → 그래서 이 과제는 ROC-AUC 를 지표로 씁니다

print_header("STEP 1. 이탈 그룹 vs 잔류 그룹(가설 세우기)")
# 이탈 여부별로 평균 요금 비교
print(df.group_by('churn').agg([
    pl.col('monthly_charges').mean().alias('평균요금'),
    pl.col('tenure_months').mean().alias('평균가입기간'),
    pl.len().alias('인원'),
]))

# → "이탈 고객의 요금이 더 높아 보이는데... 진짜일까?"
#    이 의문을 STEP 3의 통계 검정으로 확인합니다.

print_header("STEP 2. Plotly로 시각화 -> HTML 리포트")
pdf = df.to_pandas()          # Plotly 는 pandas 를 받습니다
fig = px.box(pdf, x='churn', y='monthly_charges',
            title='이탈 여부별 월 요금 분포')

# output 디렉터리가 없으면 자동 생성 (parents=True, exist_ok=True)
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

#  HTML 파일 저장
fig.write_html(output_dir / "churn_charges.html")
print("✅ 성공적으로 저장되었습니다: output/churn_charges.html")

# 박스플롯을 쓰는 이유: 평균만 보면 놓치는 '분포의 모양'과
#                      이상치를 한눈에 볼 수 있습니다.

print_header("STEP 3. 통계 검정")
# ① t-검정 : 숫자(요금)를 두 그룹 간 비교
churn_yes = pdf[pdf['churn'] == 1]['monthly_charges']
churn_no  = pdf[pdf['churn'] == 0]['monthly_charges']
t, p = stats.ttest_ind(churn_yes, churn_no, equal_var=False)
print(f't-검정 p = {p:.2e}')       # ≈ 1.2e-20 → 유의!

# ② 카이제곱 : 범주(계약유형) vs 범주(이탈)
table = pd.crosstab(pdf['contract'], pdf['churn'])
chi2, p, dof, expected = stats.chi2_contingency(table)
print(f'카이제곱 p = {p:.2e}')      # ≈ 1.3e-70 → 유의!

# 해석: 요금과 계약 유형이 이탈과 '통계적으로 유의한 연관'이 있다

print_header("STEP 4. 가공 - 결측 처리, 인코딩")
# ❌ 위험한 인코딩: Month-to-month=0, One year=1, Two year=2
#    → 모델이 '2년 계약은 1년 계약의 2배다' 라고 오해합니다!

# ✅ One-Hot 인코딩: 각 범주를 독립된 0/1 컬럼으로
#    Contract_Month  Contract_One  Contract_Two
#         1               0             0
#         0               1             0
#    → 순서/크기 관계가 생기지 않습니다

print_header("STEP 5. ColumnTransformer - 컬럼별 전처리")
num_cols = ['tenure_months', 'monthly_charges', 'total_charges']
cat_cols = ['contract', 'payment_method', 'num_services']

preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imp', SimpleImputer(strategy='median')),   # 결측 → 중앙값
        ('sc',  StandardScaler()),                   # 스케일 통일
    ]), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
])
# handle_unknown='ignore' : 실전에서 못 보던 범주가 와도 안 터짐

print_header("STEP 6. 모델 학습 - pipeline으로 묶어서 학습")
X = pdf.drop(columns=['churn'])
y = (pdf['churn'] == 1).astype(int)

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42,
    stratify=y,          # ★ 이탈 비율을 train/test에 동일하게 유지
)

pipe = Pipeline([
    ('prep', preprocessor),
    ('model', RandomForestClassifier(n_estimators=200, max_depth=8, class_weight='balanced', random_state=42)),
])
pipe.fit(X_tr, y_tr)     # ★ 전처리+모델이 한 번에 학습 (누수 없음)

print_header("STEP 7. 평가 - 왜 정확도가 아닌 ROC-AUC")
proba = pipe.predict_proba(X_te)[:, 1]     # ★ 확률을 씁니다 (0/1 아님)
auc = roc_auc_score(y_te, proba)
print(f'ROC-AUC = {auc:.3f}')              # ≈ 0.66
print(classification_report(y_te, pipe.predict(X_te)))

joblib.dump(pipe, 'output/churn_model.joblib')   # ★ 전처리까지 통째로 저장
# 나중에: pipe = joblib.load('output/churn_model.joblib')
#         pipe.predict(새데이터)   ← 전처리가 같이 딸려오므로 바로 예측 가능