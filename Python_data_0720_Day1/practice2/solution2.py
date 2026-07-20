import json
import re
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Annotated, List

file_path = 'data/api_response.json'
class UserProfile(BaseModel):
    country: str = Field(..., min_length=1)
    tier: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=100) # 29번 유저 차단: 최소 0점, 최대 100점
 
class User(BaseModel):
    id: int
    username: str = Field(..., min_length=1)
    
    # 💡 21번 유저 차단: 기본값(default)을 주지 않아 필드가 없으면 ValidationError를 던짐
    email: str 
    
    # 💡 7번 유저 차단: 나이는 무조건 0보다 커야 함 (gt=0)
    age: int = Field(..., gt=0)
    
    is_active: bool
    signup_date: str
    profile: UserProfile
    tags: List[str] = []

    # 💡 13번 유저 차단: 이메일 필드에 최소한 @와 .이 들어간 정상 형식인지 정규식 검증
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, v):
            raise ValueError("올바르지 않은 이메일 형식입니다.")
        return v
    

if __name__ == "__main__":
    data = json.load(open(file_path, encoding='utf-8'))
    
    # 💡 최상위 data에서 실제 리스트인 results를 안전하게 꺼내둡니다.
    user_list = data.get('results', [])
    
    print('전체 건수:', len(user_list))       # 40
    print(json.dumps(user_list[0], indent=2, ensure_ascii=False))   # 정상 샘플 1건
    
    # 어떤 키들이 있는지, 값 타입이 뭔지 훑어보기
    for i, row in enumerate(user_list[:3]):
        print(i, {k: type(v).__name__ for k, v in row.items()})

    valid, invalid = [], []
 
    # 💡 data 대신 user_list(진짜 리스트 덩어리)를 돌려야 row에 딕셔너리가 들어옵니다!
    for i, row in enumerate(user_list):
        try:
            valid.append(User(**row))          # 통과!
        except ValidationError as e:
            invalid.append({                      # 탈락 — 이유까지 저장
                'index': i,
                'data': row,
                'errors': e.errors(),             # 어떤 필드가 왜 틀렸는지
            })
    
    # 💡 len(data) 대신 len(user_list)로 변경하여 전체 40건 기준으로 출력되게 합니다.
    print(f'전체 {len(user_list)}건 → 유효 {len(valid)} / 오염 {len(invalid)}')
    # 40건 → 유효 36 / 오염 4  가 나오야 성공!

    print(f"{'행':<4}{'필드':<12}{'사유'}")
    for item in invalid:
        for err in item['errors']:
            field = '.'.join(str(x) for x in err['loc'])   # 중첩 경로 표시
            print(f"{item['index']:<4}{field:<12}{err['msg']}")
