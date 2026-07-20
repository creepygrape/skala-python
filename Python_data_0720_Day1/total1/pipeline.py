import asyncio
import json
from pathlib import Path
import pandas as pd
from pydantic import ValidationError
from models import Product

# ==========================================
# 1. 경로 기본 설정 (현재 파일 기준)
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# ==========================================
# 2. 모의 실행 설정 및 HTTP 요청 함수
# ==========================================
USE_REAL_HTTP = False  # 모의 실행 모드
TOTAL_TASKS = 60
CONCURRENCY_LIMIT = 10
MAX_RETRIES = 3

# 상태 기록 집합
failed_items = set()
FAIL_TARGETS = {16, 25, 36, 49}
DEAD_TARGETS = {1, 4, 9}


async def mock_fetch(item_id: int):
    """
    - 기본 0.05초 소요
    - DEAD_TARGETS: 영구적 오류 발생 (모든 재시도 실패)
    - FAIL_TARGETS: 첫 번째 시도에서만 실패, 재시도 시 성공
    """
    await asyncio.sleep(0.05)

    # 1. 영구 실패 대상
    if item_id in DEAD_TARGETS:
        raise Exception(f"500 Internal Server Error (ID: {item_id})")

    # 2. 일시적 실패 대상
    if item_id in FAIL_TARGETS and item_id not in failed_items:
        failed_items.add(item_id)
        raise Exception(f"503 Service Unavailable (ID: {item_id} 첫 시도 실패)")

    # 3. 정상 데이터 반환
    return {
        "id": item_id,
        "name": f"Product_{item_id}",
        "category": " ELECTRONICS " if item_id % 2 == 0 else " FOOD ",
        "price": 100.0 * item_id,
    }


# ==========================================
# 3. ETL 파이프라인 함수
# ==========================================
async def extract(ids: list[int], max_concurrent: int = 10) -> tuple[list[dict], list[dict]]:
    sem = asyncio.Semaphore(max_concurrent)

    async def one(i):
        async with sem:
            for attempt in range(3):
                try:
                    return await mock_fetch(i)
                except Exception as e:
                    if attempt == 2:
                        return {
                            "id": i,
                            "error": str(e),
                            "failed_at_attempt": attempt + 1,
                        }
                    await asyncio.sleep(0.1 * (2**attempt))

    results = await asyncio.gather(*[one(i) for i in ids], return_exceptions=True)

    success = [r for r in results if isinstance(r, dict) and "error" not in r]
    dead_letters = [r for r in results if isinstance(r, dict) and "error" in r]

    return success, dead_letters


def transform(raw: list[dict]) -> tuple[list[Product], list[dict]]:
    valid, invalid = [], []
    for row in raw:
        try:
            valid.append(Product(**row))
        except ValidationError as e:
            invalid.append({"data": row, "errors": e.errors()})
    return valid, invalid


def load(valid: list[Product], out_dir=OUTPUT_DIR) -> pd.DataFrame:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)  # 

    df = pd.DataFrame([v.model_dump() for v in valid])
    df.to_csv(target_dir / "products.csv", index=False)      # 
    df.to_parquet(target_dir / "products.parquet", index=False)  # 
    return df


def save_dead_letters(dead_letters: list[dict], out_dir=OUTPUT_DIR):
    if not dead_letters:
        return

    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)  # 
    file_path = target_dir / "dead_letter.json"     # 

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dead_letters, f, ensure_ascii=False, indent=4)


# ==========================================
# 4. 파이프라인 실행
# ==========================================
async def run(ids: list[int]) -> dict:
    raw, dead_letters = await extract(ids)  # E
    valid, invalid = transform(raw)        # T
    df = load(valid)                       # L

    save_dead_letters(dead_letters)

    return {
        "requested_total": len(ids),
        "extracted": len(raw),
        "dead_letters": len(dead_letters),
        "valid": len(valid),
        "invalid": len(invalid),
        "rows_saved": len(df),
    }


if __name__ == "__main__":
    summary = asyncio.run(run(list(range(60))))

    print("=" * 40)
    print("비동기 ETL 파이프라인 실행 결과")
    print("=" * 40)
    print(f"요청 총 건수 : {summary['requested_total']}건")
    print(f"추출 데이터 : {summary['extracted']}건")
    print(f"유효 데이터 : {summary['valid']}건")
    print(f"오염 데이터 : {summary['invalid']}건")
    print(f"저장 데이터 : {summary['rows_saved']}건")
    print(f"실패 데이터 : {summary['dead_letters']}건")