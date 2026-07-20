import time
import asyncio

# [기본 설정] 문제 조건에 따라 인터넷 없이 모의 실행합니다.
USE_REAL_HTTP = False

# [모의 네트워크 함수] 
async def do_request_mock(item_id):
    await asyncio.sleep(0.1)  # 건당 0.1초 응답 시간
    return {'id': item_id, 'ok': True}
 
def fetch_sync(item_id):
    time.sleep(0.1)              # 네트워크 대기를 흉내
    return {'id': item_id, 'ok': True}

async def fetch(item_id):             # ① async def
    await asyncio.sleep(0.1)          # ② await (time.sleep 아님!)
    return {'id': item_id, 'ok': True}
 

 
async def fetch_limited(item_id, sem):
    async with sem:                       # ★ 입장권 받기 (없으면 대기)
        await asyncio.sleep(0.1)
        return {'id': item_id, 'ok': True}
    # with 블록을 나가면 입장권 자동 반납

async def fetch_with_timeout(item_id, sem):
    async with sem:
        try:
            async with asyncio.timeout(3.0):     # 3초 넘으면 포기
                await asyncio.sleep(0.1)
                return {'id': item_id, 'ok': True}
        except TimeoutError:
            return {'id': item_id, 'ok': False, 'reason': 'timeout'}

# [핵심 수집기] 세마포어(제한) + 타임아웃 + 재시도 로직 탑재
async def fetch_retry(item_id, sem, max_retries=3):
    for attempt in range(max_retries):
        try:
            # 1. 동시에 최대 10개까지만 진입 허용 (백프레셔 제어)
            async with sem:
                # 2. 파이썬 3.12 최신 문법으로 개별 요청당 3초 타임아웃 제한
                async with asyncio.timeout(3.0):
                    return await do_request_mock(item_id)
                    
        except (Exception, asyncio.TimeoutError) as e:
            # 마지막 시도마저 실패하면 에러 결과 반환하며 포기
            if attempt == max_retries - 1:
                return {'id': item_id, 'ok': False, 'error': str(e)}
            
            # 실패 시 잠시 대기 후 재시도 (Exponential Backoff: 0.1초 -> 0.2초 -> 0.4초)
            wait = 0.1 * (2 ** attempt)
            print(f"[경고] ID {item_id} 요청 실패 ({str(e)}). {wait:.1f}초 후 재시도 합니다. (시도 {attempt + 1}/{max_retries})")
            await asyncio.sleep(wait)
 
async def main():
    MAX_CONCURRENT = 10
    # 💡 이벤트 루프 안에서 안전하게 세마포어(입장권 10장) 생성
    sem = asyncio.Semaphore(MAX_CONCURRENT)   
    
    # 60개의 태스크 생성
    tasks = [fetch_retry(i, sem) for i in range(60)]
    
    print(f"🚀 [시작] 총 60건의 데이터 수집을 시작합니다. (동시 요청 제한: {MAX_CONCURRENT}개)")
    
    # 60개 태스크를 동시에 던지기 (동시 요청은 10개로 제한됨)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 결과 통계 분류
    ok   = [r for r in results if isinstance(r, dict) and r.get('ok') == True]
    fail = [r for r in results if isinstance(r, dict) and r.get('ok') == False]
    
    print("\n========================================")
    print(f"📊 [결과 요약] 수집 완료!")
    print(f"✅ 성공: {len(ok)} 건")
    print(f"❌ 최종 실패: {len(fail)} 건")
    print("========================================")
    
    return results


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    
    elapsed_time = time.perf_counter() - start
    print(f"⏱️ 총 소요 시간: {elapsed_time:.2f}초")
