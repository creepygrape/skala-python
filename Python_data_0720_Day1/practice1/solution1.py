import csv
from collections import Counter
from functools import reduce

file_path = 'data/web_logs.csv'
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)   
        for row in reader:
            yield row # 한 번에 읽기         
 
def fold(acc, row):
    acc['total'] += 1
    acc['status'][row['status']] += 1
    
    return acc


if __name__ == "__main__":
    total = 0
    by_status = Counter()
    by_path = Counter()
    by_hour = Counter()
    by_ip = Counter()

    # 파일 읽기(yield) + Counter
    for row in load_csv(file_path):
        total += 1
        by_status[row['status']] += 1
        by_path[row['path']] += 1
        by_ip[row['ip']] += 1

        hour = row['timestamp'][11:13]
        by_hour[hour] += 1

    # 5xx 비율 계산
    err_5xx = sum(c for s, c in by_status.items() if str(s).startswith('5')) # 앞자리가 5면 +1
    ratio = err_5xx / total * 100
    print(f'5xx: {err_5xx}건 ({ratio:.1f}%)')

    # fold 패턴 - functools.reduce 
    init = {'total': 0, 'status': Counter()}
    result = reduce(fold, load_csv(file_path), init)
    print(result['total'])
    print(result['status'])

    print('=' * 40)
    print(f'\n총 요청 수 : {total:,}')
    print(f'5xx 오류율 : {ratio:.1f}%')
    print('\n-- 인기 경로 TOP 5 --')
    for path, cnt in by_path.most_common(5):
        print(f'  {path:<20} {cnt:>7,}')
    print('\n-- 인기 접속 시간 TOP 5 --')
    for hour, cnt in by_hour.most_common(5):
        print(f'  {hour:<20} {cnt:>7,}')
    print('\n-- 접속 상위 IP TOP 5 --')
    for ip, cnt in by_ip.most_common(5):
        print(f'  {ip:<20} {cnt:>7,}')
