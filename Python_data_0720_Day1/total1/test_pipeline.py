# test_pipeline.py
from pipeline import transform, extract, load, save_dead_letters
import pandas as pd
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

# 카테고리 소문자화
def test_category_lowercase():
    valid, _ = transform([{"id": 1, "name": "A", "category": " FOOD ", "price": 10}])
    assert valid[0].category == "food"


# 음수 가격 거부
def test_negative_price_rejected():
    valid, invalid = transform(
        [{"id": 1, "name": "A", "category": "food", "price": -5}]
    )
    assert len(valid) == 0
    assert len(invalid) == 1


# 전체 = 유효 + 무효 건수 체크
def test_valid_invalid_count():
    # ★ 테스트용 데이터 직접 정의
    정상1 = {"id": 1, "name": "A", "category": "food", "price": 10}
    정상2 = {"id": 2, "name": "B", "category": "electronics", "price": 200}
    오염1 = {"id": 3, "name": "C", "category": "book", "price": -10}  # 음수 가격 오류

    rows = [정상1, 정상2, 오염1]
    valid, invalid = transform(rows)
    assert len(valid) + len(invalid) == len(rows)  # ★ 하나도 안 새는지


# Parquet 라운드트립 테스트 (재로딩 동일)
def test_parquet_round_trip(tmp_path):  # tmp_path = pytest 임시 폴더
    df = pd.DataFrame({"id": [1, 2], "price": [10.5, 20.0]})
    p = tmp_path / "test.parquet"
    df.to_parquet(p, index=False)
    back = pd.read_parquet(p)
    pd.testing.assert_frame_equal(df, back)  # ★ 완전히 같아야 통과


# extract() 비동기 수집 & 백프레셔/재시도 테스트
@pytest.mark.asyncio
async def test_extract_success_and_retry_behavior():
    # 16번은 FAIL_TARGETS (첫 시도 실패 -> 재시도 성공)
    # 1번은 DEAD_TARGETS (3회 재시도 모두 실패)
    # 2번은 정상 대상
    target_ids = [1, 2, 16]

    raw, dead_letters = await extract(target_ids)

    # 추출 성공 데이터 검증 (2, 16번)
    extracted_ids = [r["id"] for r in raw]
    assert set(extracted_ids) == {2, 16}

    # Dead Letter 데이터 검증 (1번)
    assert len(dead_letters) == 1
    assert dead_letters[0]["id"] == 1
    assert dead_letters[0]["failed_at_attempt"] == 3


# load() 데이터 저장 및 포맷 변환 테스트
def test_load_creates_csv_and_parquet(tmp_path):
    from models import Product

    # Mock Valid Product 객체 생성
    valid_products = [
        Product(id=10, name="TestA", category="FOOD", price=50.0),
        Product(id=20, name="TestB", category="ELECTRONICS", price=150.0),
    ]

    # tmp_path(pytest 제공 임시 디렉토리)에 저장 실행
    out_dir = str(tmp_path / "test_output")
    df = load(valid_products, out_dir=out_dir)

    # 1. 반환된 DataFrame 행 개수 확인
    assert len(df) == 2

    # 2. 파일 생성 여부 확인
    csv_file = tmp_path / "test_output" / "products.csv"
    parquet_file = tmp_path / "test_output" / "products.parquet"

    assert csv_file.exists()
    assert parquet_file.exists()

    # 3. CSV 저장 내용 검증 (category 소문자 처리 확인)
    loaded_df = pd.read_csv(csv_file)
    assert loaded_df.iloc[0]["category"] == "food"


# 3. save_dead_letters() JSON 저장 테스트
def test_save_dead_letters_writes_json(tmp_path):
    mock_dead_letters = [
        {"id": 1, "error": "500 Error", "failed_at_attempt": 3},
        {"id": 4, "error": "500 Error", "failed_at_attempt": 3},
    ]

    out_dir = str(tmp_path / "test_output")
    save_dead_letters(mock_dead_letters, out_dir=out_dir)

    json_file = tmp_path / "test_output" / "dead_letter.json"

    # 1. JSON 파일 생성 여부 확인
    assert json_file.exists()

    # 2. 저장된 JSON 데이터 내용 검증
    with open(json_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert len(saved_data) == 2
    assert saved_data[0]["id"] == 1
    assert saved_data[1]["id"] == 4
