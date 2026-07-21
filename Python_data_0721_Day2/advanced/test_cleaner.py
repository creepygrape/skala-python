import pandas as pd
import numpy as np
import pytest
from cleaner import clean_price, fill_missing, remove_outliers

# 💡 테스트에 공통으로 쓰일 샘플 데이터 생성 (Fixture)
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'category': ['A', 'A', 'A', 'B', 'B', 'B'],
        'unit_price': [100.0, -50.0, np.nan, 200.0, 300.0, 10000.0]  # 음수, 결측치, 이상치 포함
    })


def test_clean_price(sample_df):
    """음수 가격이 NaN으로 잘 변환되는지 테스트"""
    cleaned = clean_price(sample_df)
    # index 1번(-50.0)이 NaN이 되었는지 확인
    assert pd.isna(cleaned.loc[1, 'unit_price'])


def test_fill_missing(sample_df):
    """그룹별 중앙값으로 결측치가 잘 채워지는지 테스트"""
    # 먼저 음수값을 NaN으로 만든 후 채우기 테스트 진행
    cleaned = clean_price(sample_df) 
    filled = fill_missing(cleaned)
    
    # 'A' 카테고리의 정상 가격은 100.0 하나뿐이므로 median은 100.0
    # index 1, 2의 NaN 값이 100.0으로 채워졌는지 확인
    assert filled.loc[1, 'unit_price'] == 100.0
    assert filled.loc[2, 'unit_price'] == 100.0
    assert filled['unit_price'].isna().sum() == 0  # 결측치가 0개여야 함


def test_remove_outliers(sample_df):
    """IQR 기준 극단적 이상치가 잘 제거되는지 테스트"""
    # 이상치(10000.0)가 제거되는지 확인
    normal_df = pd.DataFrame({
        'category': ['B', 'B', 'B', 'B', 'B'],
        'unit_price': [200.0, 210.0, 205.0, 195.0, 10000.0] # 10000은 이상치
    })
    
    filtered = remove_outliers(normal_df)
    
    # 10000.0 데이터(1개)가 제거되어 총 4개 행만 남아야 함
    assert len(filtered) == 4
    assert 10000.0 not in filtered['unit_price'].values