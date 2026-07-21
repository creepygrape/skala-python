import argparse
import time
import schedule
from report import run_once


def run_loop(interval: int):
    """방식 ①: while + sleep 경량 루프 (외부 라이브러리 미사용)"""
    print(f"⏱️ 경량 루프 스케줄러 시작 ({interval}초 주기) - 종료: Ctrl+C")
    try:
        while True:
            run_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n스케줄러 동작 중지")


def run_schedule_at(cron_time: str):
    """방식 ②-1: schedule 라이브러리 (매일 특정 시각 지정)"""
    schedule.every().day.at(cron_time).do(run_once)
    print(f"📅 schedule 스케줄러 시작 (매일 {cron_time} 실행) - 종료: Ctrl+C")
    print("등록된 스케줄:")
    for job in schedule.get_jobs():
        print(f" - {job}")

    _start_schedule_loop()


def run_schedule_interval(seconds: int):
    """방식 ②-2: schedule 라이브러리 (N초 주기 반복)"""
    schedule.every(seconds).seconds.do(run_once)
    print(
        f"⏱️ schedule 스케줄러 시작 ({seconds}초 간격 반복) - 종료: Ctrl+C"
    )
    print("등록된 스케줄:")
    for job in schedule.get_jobs():
        print(f" - {job}")

    _start_schedule_loop()


def _start_schedule_loop():
    """schedule 대기 이벤트 루프 공통 함수"""
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n스케줄러 동작 중지")


def main():
    parser = argparse.ArgumentParser(description="리포트 자동 생성 스케줄러")
    parser.add_argument(
        '--interval',
        type=int,
        default=0,
        help='while+sleep 경량 루프 주기 (초)',
    )
    parser.add_argument(
        '--at',
        type=str,
        default=None,
        help='매일 실행할 시각 (HH:MM 형식, 예: 09:00)',
    )
    parser.add_argument(
        '--seconds',
        type=int,
        default=0,
        help='schedule 라이브러리 기반 반복 주기 (초)',
    )
    args = parser.parse_args()

    # 옵션 조건별 실행 방식 분기
    if args.interval > 0:
        # 방식 ①: 경량 루프
        run_loop(args.interval)
    elif args.at:
        # 방식 ②-1: schedule (매일 정해진 시각)
        run_schedule_at(args.at)
    elif args.seconds > 0:
        # 방식 ②-2: schedule (N초 주기 반복)
        run_schedule_interval(args.seconds)
    else:
        # 방식 ③: OS cron 또는 1회 단발성 실행
        print("⚡ 1회 실행 모드 (OS cron 연동용)")
        run_once()

if __name__ == '__main__':
    main()