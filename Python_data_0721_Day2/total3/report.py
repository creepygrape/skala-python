from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from pathlib import Path
from config import CONFIG
import pandas as pd

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """sales_raw 전용 데이터 정제 함수"""
    cleaned = df.copy()

    # 1. 중복 제거
    cleaned = cleaned.drop_duplicates()

    # 2. order_date 문자열 -> datetime 변환 (변환 불가한 값은 NaT 처리 후 제거)
    cleaned['order_date'] = pd.to_datetime(
        cleaned['order_date'], errors='coerce'
    )
    cleaned = cleaned.dropna(subset=['order_date'])

    # 3. region 결측치 처리 (Missing -> 'Unknown')
    cleaned['region'] = cleaned['region'].fillna('Unknown').astype(str).str.strip()
    cleaned['category'] = (
        cleaned['category'].fillna('Unknown').astype(str).str.strip()
    )

    # 4. unit_price 결측치 제거 & 음수(-299,111원 등) 이상치 제거
    cleaned['unit_price'] = pd.to_numeric(
        cleaned['unit_price'], errors='coerce'
    )
    cleaned = cleaned.dropna(subset=['unit_price'])
    cleaned = cleaned[cleaned['unit_price'] > 0]  # 양수 가격만 유지

    # 5. quantity 유효성 검증 (양수만)
    cleaned['quantity'] = pd.to_numeric(cleaned['quantity'], errors='coerce')
    cleaned = cleaned[cleaned['quantity'] > 0]

    # 6. discount 범위 보정 (0.0 ~ 1.0)
    cleaned['discount'] = pd.to_numeric(
        cleaned['discount'], errors='coerce'
    ).fillna(0.0)
    cleaned['discount'] = cleaned['discount'].clip(lower=0.0, upper=1.0)

    # 7. 파생변수: total_amount (실제 결제 금액)
    # 공식: 수량 * 단가 * (1 - 할인율)
    cleaned['total_amount'] = (
        cleaned['quantity'] * cleaned['unit_price'] * (1 - cleaned['discount'])
    ).round(0)

    # 인덱스 초기화 후 반환
    return cleaned.reset_index(drop=True)

def aggregate(df: pd.DataFrame, top_n: int = 10) -> dict:
    """카테고리별 상세 집계 로직"""
    total_sales = df['total_amount'].sum()
    total_orders = len(df)

    if total_sales == 0 or total_orders == 0:
        return {
            'kpi': {'총매출': 0, '주문수': 0, '평균주문액': 0},
            'by_category': [],
        }

    # 카테고리별 매출액 및 주문 건수 그룹화
    cat_summary = (
        df.groupby('category', observed=False)
        .agg(
            total_amount=('total_amount', 'sum'),
            order_count=('total_amount', 'count'),
        )
        .reset_index()
        .sort_values(by='total_amount', ascending=False)
        .head(top_n)
    )

    # 상세 데이터 딕셔너리 생성 (순위, 건당 평균가, 비중 계산)
    by_category_list = []
    for rank, (_, row) in enumerate(cat_summary.iterrows(), start=1):
        amount = int(row['total_amount'])
        count = int(row['order_count'])
        avg_price = round(amount / count) if count > 0 else 0
        share = round((amount / total_sales) * 100, 1)

        by_category_list.append({
            'rank': rank,
            'category': row['category'],
            'amount': amount,
            'count': count,
            'avg_price': avg_price,
            'share': share,  # 매출 비중 (%)
        })

    return {
        'kpi': {
            '총매출': int(total_sales),
            '주문수': int(total_orders),
            '평균주문액': round(float(df['total_amount'].mean()), 1),
        },
        'by_category': by_category_list,
    }

def render(data: dict, cfg) -> Path:
    env = Environment(loader=FileSystemLoader(CONFIG.template_dir))
    tpl = env.get_template('report.html')

    html = tpl.render(
        title=cfg.title,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        **data,
    )

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    # ★ 타임스탬프를 파일명에 → 이전 리포트가 안 지워짐
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = cfg.output_dir / f'report_{stamp}.html'
    out.write_text(html, encoding='utf-8')
    return out

# 세 가지 방식 모두 결국 같은 함수 하나를 부르게 만드세요
def run_once():
    df = pd.read_csv(CONFIG.data_path) # 로딩
    df = clean_sales_data(df) # 정제
    data = aggregate(df, CONFIG.top_n) # 집계
    path = render(data, CONFIG) # 렌더링
    print(f'리포트 생성: {path}') # 리포트

# ★ 루프 · schedule · cron 이 전부 run_once() 만 호출
#   → 실행 방식이 달라도 결과는 반드시 동일 (일관성)
