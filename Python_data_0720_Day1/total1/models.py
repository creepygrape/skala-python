# models.py
from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float = Field(gt=0)  # ★ 음수 가격 거부

    @field_validator("category")
    @classmethod
    def lower_category(cls, v):
        return v.strip().lower()  # ★ 소문자화
