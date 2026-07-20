import time
import asyncio

# [기본 설정] 문제 조건에 따라 인터넷 없이 모의 실행합니다.
USE_REAL_HTTP = False  # 모의 실행 모드
TOTAL_TASKS = 60
CONCURRENCY_LIMIT = 10
MAX_RETRIES = 3

# 한번이라도 실패했던 항목의 ID를 기록하는 집합
failed_items = set()
FAIL_TARGETS = {16, 25, 36, 49}

# ==========================================
# 모의 HTTP 요청 함수
# ==========================================
async def mock_fetch(item_id: int):
    """
    - 기본 0.25초 소요
    - DEAD_TARGETS: 영구적 오류 발생 (모든 재시도 실패)
    """
    await asyncio.sleep(0.25)

    # 일시 실패 대상 (첫 번째 시도만 실패)
    if item_id in FAIL_TARGETS and item_id not in failed_items:
        failed_items.add(item_id)
        raise Exception("503 Service Unavailable (첫 번째 요청 실패)")

    return {"id": item_id, "ok": True, "data": f"Data_{item_id}"}


def fetch_sync(item_id):
    time.sleep(0.1)  # 네트워크 대기를 흉내
    return {"id": item_id, "ok": True}


async def fetch(item_id):  # ① async def
    await asyncio.sleep(0.1)  # ② await (time.sleep 아님!)
    return {"id": item_id, "ok": True}


async def fetch_limited(item_id, sem):
    async with sem:  # ★ 입장권 받기 (없으면 대기)
        await asyncio.sleep(0.1)
        return {"id": item_id, "ok": True}
    # with 블록을 나가면 입장권 자동 반납


async def fetch_with_timeout(item_id, sem):
    async with sem:
        try:
            async with asyncio.timeout(2.0):  # 2초 넘으면 포기
                await asyncio.sleep(0.1)
                return {"id": item_id, "ok": True}
        except TimeoutError:
            return {"id": item_id, "ok": False, "reason": "timeout"}


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


async def main1():
    r = await fetch(1)
    print(r)


async def main2():
    tasks = [fetch(i) for i in range(60)]  # 아직 실행 안 됨 (예약만)
    results = await asyncio.gather(*tasks)  # ★ 여기서 한꺼번에 실행
    print(len(results))  # 60


async def main3():
    MAX_CONCURRENT = 10
    sem = asyncio.Semaphore(MAX_CONCURRENT)  # 입장권 10장

    results = await asyncio.gather(*[fetch_limited(i, sem) for i in range(60)])
    return results


async def main4():
    MAX_CONCURRENT = 10
    sem = asyncio.Semaphore(MAX_CONCURRENT)  # 입장권 10장

    results = await asyncio.gather(*[fetch_with_timeout(i, sem) for i in range(60)])
    return results


async def main5():
    MAX_CONCURRENT = 10
    sem = asyncio.Semaphore(MAX_CONCURRENT)  # 입장권 10장

    await asyncio.gather(*[fetch_retry(i, sem) for i in range(60)])


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
    print_header("STEP 0. fetch_sync : 동기")
    start = time.perf_counter()
    results = [fetch_sync(i) for i in range(60)]
    print(f"동기 처리 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 6초

    print_header("STEP 1. fetch : 비동기 단건")
    start = time.perf_counter()
    asyncio.run(main1())
    print(f"비동기 단건 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 0.1초

    print_header("STEP 2. fetch + gather : 무제한 비동기")
    start = time.perf_counter()
    asyncio.run(main2())
    print(f"무제한 비동기 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 0.1초

    print_header("STEP 3. fetch_limited : 백프레셔")
    start = time.perf_counter()
    asyncio.run(main3())
    print(f"백프레셔 비동기 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 0.6초

    print_header("STEP 4. fetch_with_timeout : 타임아웃")
    start = time.perf_counter()
    asyncio.run(main4())
    print(f"타임아웃 비동기 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 0.6초

    print_header("STEP 5. fetch_retry : 재시도")
    start = time.perf_counter()
    asyncio.run(main5())
    print(f"재시도 비동기 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 3초

    print_header("STEP 6. 예외 격리 및 완성 수집기")
    start = time.perf_counter()
    asyncio.run(main())
    print(f"⏱️ 총 소요 시간: {time.perf_counter() - start:.2f}초")  # 약 1.5초
