import csv
from collections import Counter
from functools import reduce
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
file_path = DATA_DIR / "web_logs.csv"


def load_only_five(path):
    with open(path) as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 4:  # 5줄만 보고 멈춤
                break


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row  # 한 번에 읽기


def fold(acc, row):
    acc["total"] += 1
    acc["status"][row["status"]] += 1

    return acc


def print_header(str):
    print("\n")
    print("=" * 40)
    print(str)
    print("=" * 40)


if __name__ == "__main__":
    # STEP 0. 데이터 형태 확인
    print_header("STEP 0. 데이터 형태 확인")
    load_only_five(file_path)

    total = 0
    by_status = Counter()
    by_path = Counter()
    by_hour = Counter()
    by_ip = Counter()

    # STEP 1. 파일 -> 레코드 제너레이터 (3줄 확인)
    print_header("STEP 1. 파일 -> 레코드 제너레이터")
    gen = load_csv(file_path)
    for _ in range(3):
        print(next(gen))

    # STEP 2 + 3. 파일 읽기(yield) + Counter
    print_header("STEP 2 + 3. 파일 읽기(yield) + Counter")
    for row in load_csv(file_path):
        total += 1
        by_status[row["status"]] += 1
        by_path[row["path"]] += 1
        by_ip[row["ip"]] += 1

        hour = row["timestamp"][11:13]
        by_hour[hour] += 1

    print(f"by_status 5개 : {by_status.most_common(5)}")
    print(f"by_path 5개 : {by_path.most_common(5)}")
    print(f"by_hour 5개 : {by_hour.most_common(5)}")
    print(f"by_ip 5개 : {by_ip.most_common(5)}")

    # STEP 4. 5xx 비율 계산
    print_header("STEP 4. 5xx 비율 계산")
    err_5xx = sum(
        c for s, c in by_status.items() if str(s).startswith("5")
    )  # 앞자리가 5면 +1
    ratio = err_5xx / total * 100
    print(f"5xx: {err_5xx}건 ({ratio:.1f}%)")

    # STEP 5. fold 패턴 - functools.reduce
    print_header("STEP 5. fold 패턴 - functools.reduce 활용")
    init = {"total": 0, "status": Counter()}
    result = reduce(fold, load_csv(file_path), init)
    print(result["total"])
    print(result["status"])

    # SETP 6. 리포트 및 상위 IP
    print_header("리포트 및 상위 IP")
    print(f"\n총 요청 수 : {total:,}")
    print(f"5xx 오류율 : {ratio:.1f}%")
    print("\n-- 인기 경로 TOP 5 --")
    for path, cnt in by_path.most_common(5):
        print(f"  {path:<20} {cnt:>7,}")
    print("\n-- 인기 접속 시간 TOP 5 --")
    for hour, cnt in by_hour.most_common(5):
        print(f"  {hour:<20} {cnt:>7,}")
    print("\n-- 접속 상위 IP TOP 5 --")
    for ip, cnt in by_ip.most_common(5):
        print(f"  {ip:<20} {cnt:>7,}")
