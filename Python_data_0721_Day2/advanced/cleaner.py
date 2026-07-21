import pandas as pd
import numpy as np

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    price 컬럼의 음수값을 NaN으로 변경하고, 타입 및 이상치를 정제
    """
    df = df.copy()
    if 'unit_price' in df.columns:
        # 음수 가격은 잘못된 데이터이므로 NaN 처리
        df.loc[df['unit_price'] < 0, 'unit_price'] = np.nan
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    category별 price의 중앙값(median)으로 결측치를 채움
    """
    df = df.copy()
    if 'unit_price' in df.columns and 'category' in df.columns:
        df['unit_price'] = df.groupby('category', observed=True)['unit_price'].transform(
            lambda s: s.fillna(s.median())
        )
    return df


def remove_outliers(df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
    """
    IQR(Interquartile Range) 방식을 이용하여 price의 이상치를 제거
    """
    df = df.copy()
    if 'unit_price' in df.columns and not df['unit_price'].dropna().empty:
        q1 = df['unit_price'].quantile(0.25)
        q3 = df['unit_price'].quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - (factor * iqr)
        upper_bound = q3 + (factor * iqr)
        
        # 범위 내 데이터만 필터링
        df = df[(df['unit_price'] >= lower_bound) & (df['unit_price'] <= upper_bound)]
    return df