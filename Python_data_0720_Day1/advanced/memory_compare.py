import csv
import tracemalloc
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR.parent / "data" / "web_logs.csv"

# ==========================================
# 1. readlines() 방식 (메모리에 파일 전체 로드)
# ==========================================
def test_readlines(path):
    with open(path, "r", encoding="utf-8") as f:
        # 파일 전체 줄을 메모리 리스트로 올림
        lines = f.readlines()

    header = lines[0].strip().split(",")
    total = 0
    for line in lines[1:]:
        row = dict(zip(header, line.strip().split(",")))
        total += 1
    return total


# ==========================================
# 2. Generator 방식 (한 줄씩 스트리밍 로드)
# ==========================================
def load_csv_gen(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def test_generator(path):
    total = 0
    for _ in load_csv_gen(path):
        total += 1
    return total


# ==========================================
# 메모리 측정 함수
# ==========================================
def measure_memory(target_fn, path, label):
    tracemalloc.start()

    # 대상 함수 실행
    total_count = target_fn(path)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024 * 1024)
    peak_kb = peak / 1024

    print(f"[{label}]")
    print(f"  - 처리된 레코드 수: {total_count:,} 개")
    print(f"  - Peak 메모리 사용량: {peak_mb:.2f} MB ({peak_kb:.2f} KB)\n")


if __name__ == "__main__":
    print("=" * 50)
    print("📊 [메모리 사용량 비교 측정 시작]")
    print("=" * 50 + "\n")

    # 1. readlines() 측정
    measure_memory(test_readlines, FILE_PATH, "방식 1: readlines() - 전체 로드")

    # 2. Generator 측정
    measure_memory(test_generator, FILE_PATH, "방식 2: Generator - 한 줄씩 스트리밍")