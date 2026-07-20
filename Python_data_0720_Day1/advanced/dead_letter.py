import time
import asyncio
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# [기본 설정] 문제 조건에 따라 인터넷 없이 모의 실행합니다.
USE_REAL_HTTP = False  # 모의 실행 모드
TOTAL_TASKS = 60
CONCURRENCY_LIMIT = 10
MAX_RETRIES = 3

# 한번이라도 실패했던 항목의 ID를 기록하는 집합
failed_items = set()
FAIL_TARGETS = {16, 25, 36, 49}
DEAD_TARGETS = {1, 4, 9}


# ==========================================
# 모의 HTTP 요청 함수
# ==========================================
async def mock_fetch(item_id: int):
    """
    - 기본 0.15초 소요
    - DEAD_TARGETS: 영구적 오류 발생 (모든 재시도 실패)
    - FAIL_TARGETS: 첫 번째 시도에서만 실패, 재시도 시 성공
    """
    await asyncio.sleep(0.15)

    # 영구 실패 대상
    if item_id in DEAD_TARGETS:
        raise Exception("500 Internal Server Error (영구적 서버 오류)")

    # 일시 실패 대상 (첫 번째 시도만 실패)
    if item_id in FAIL_TARGETS and item_id not in failed_items:
        failed_items.add(item_id)
        raise Exception("503 Service Unavailable (첫 번째 요청 실패)")

    return {"id": item_id, "ok": True, "data": f"Data_{item_id}"}

async def fetch_retry(item_id, sem, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with sem:
                return await mock_fetch(item_id)
        except Exception as e:
            if attempt == max_retries - 1:
                # 마지막 시도까지 모두 실패했으면 실패 결과 반환
                return {
                    "id": item_id,
                    "ok": False,
                    "error": str(e),
                    "failed_attempts": max_retries,
                }
            wait = 0.15 * 2**attempt
            print(f"{item_id} 실패, {wait}초 후 재시도")
            await asyncio.sleep(wait)

async def main():
    failed_items.clear()

    MAX_CONCURRENT = 10
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = [fetch_retry(i, sem) for i in range(60)]

    print(
        f"🚀 [시작] 총 60건의 데이터 수집을 시작합니다. (동시 요청 제한: {MAX_CONCURRENT}개)"
    )

    # 60개 태스크를 동시에 던지기 (동시 요청은 10개로 제한됨)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 결과 통계 분류
    ok = [r for r in results if isinstance(r, dict) and r.get("ok") == True]
    fail = [r for r in results if isinstance(r, dict) and r.get("ok") == False]

    # 📁 최종 실패 건을 버리지 않고 dead_letter.json 파일로 기록
    with open(BASE_DIR / 'dead_letter.json', "w", encoding="utf-8") as f:
        json.dump(fail, f, ensure_ascii=False, indent=2)

    print("\n========================================")
    print("📊 [결과 요약] 수집 완료!")
    print(f"✅ 성공: {len(ok)} 건")
    print(f"❌ 최종 실패: {len(fail)} 건")
    print("========================================")

    return results

def print_header(str):
    print("\n")
    print("=" * 40)
    print(str)
    print("=" * 40)

if __name__ == "__main__":
    print_header("한 걸음 더. dead_letter 격리")
    start = time.perf_counter()
    asyncio.run(main())
    print(f"⏱️ 총 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 1.5초
