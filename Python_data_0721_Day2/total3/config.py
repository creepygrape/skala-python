from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
file_path = DATA_DIR / "sales_raw.csv"

@dataclass(frozen=True)          # ★ frozen = 수정 불가
class Config:
    data_path: Path = file_path
    output_dir: Path = BASE_DIR / 'output'
    template_dir: Path = BASE_DIR / 'templates'
    title: str = '일일 매출 리포트'
    top_n: int = 10

CONFIG = Config()

# 시도해보기 → FrozenInstanceError 발생! (의도된 동작)
# CONFIG.title = '바꿔보기'   
