import pandas as pd
import polars as pl
import duckdb as duck
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# 파일 경로 (실제 파일 경로 구조에 맞춰 조율)
DATA_DIR = BASE_DIR.parent.parent / "data"
file_path = DATA_DIR / "events_large.csv"


def pandas_load():
    start = time.perf_counter()
    df = pd.read_csv(file_path)

    # status 필터 제거 및 value -> amount로 변경
    res_pandas = (df.groupby('event_type')
                    .agg(cnt=('amount', 'count'), avg=('amount', 'mean'))
                    .sort_values('cnt', ascending=False)
                    .reset_index())
    
    t_pandas = (time.perf_counter() - start) * 1000
    print(f'Pandas: {t_pandas:.0f} ms')
    return res_pandas, t_pandas


def polars_load():
    start = time.perf_counter()
    # scan_csv를 통한 지연 평가(Lazy Execution)
    res_polars = (pl.scan_csv(file_path)
                    .group_by('event_type')
                    .agg([
                        pl.len().alias('cnt'),
                        pl.col('amount').mean().alias('avg'),
                    ])
                    .sort('cnt', descending=True)
                    .collect())  # 실제 연산 수행
    
    t_polars = (time.perf_counter() - start) * 1000
    print(f'Polars: {t_polars:.0f} ms')
    return res_polars, t_polars


def duckDB():
    start = time.perf_counter()
    # duckdb -> duck 모듈명 통일
    res_duck = duck.sql(f"""
        SELECT event_type,
            COUNT(amount) AS cnt,
            AVG(amount)   AS avg
        FROM '{file_path}'
        GROUP BY event_type
        ORDER BY cnt DESC
    """).df()
    
    t_duck = (time.perf_counter() - start) * 1000
    print(f'DuckDB: {t_duck:.0f} ms')
    return res_duck, t_duck


def result_validation(res_pandas, res_polars, res_duck):
    # 정렬 및 인덱스 초기화로 비교 기준 통일
    a = res_pandas.sort_values('event_type').reset_index(drop=True)
    b = res_polars.to_pandas().sort_values('event_type').reset_index(drop=True)
    c = res_duck.sort_values('event_type').reset_index(drop=True)
    
    # 허용 오차(atol) 내에서 엔진 간 결과 데이터 동일 여부 검증
    pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=1e-6)
    pd.testing.assert_frame_equal(a, c, check_dtype=False, atol=1e-6)
    print('✅ 세 엔진 결과 완전히 일치!\n')

    # atol=1e-6 : 부동소수점은 미세한 오차가 정상이므로 허용 오차를 줍니다


if __name__ == "__main__":
    # 각 엔진 실행 및 결과/시간 반환
    res_pandas, t_pandas = pandas_load()
    res_polars, t_polars = polars_load()
    res_duck, t_duck = duckDB()

    # 결과 검증 (res_duck 인자 정상 전달)
    result_validation(res_pandas, res_polars, res_duck)

    # 성능 비교 벤치마크 리포트 출력
    results = [
        ('Polars', t_polars),
        ('DuckDB', t_duck),
        ('Pandas', t_pandas),
    ]
    base = t_pandas
    
    print("=" * 35)
    print(f"{'엔진':<10}{'시간(ms)':>12}{'배속':>10}")
    print("-" * 35)
    for name, t in sorted(results, key=lambda x: x[1]):
        print(f'{name:<10}{t:>10.0f} ms{base / t:>9.1f}x')
    print("=" * 35)