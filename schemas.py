from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class SpendCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Spending amount (must be positive)")
    category: str = Field(..., min_length=1, max_length=50, description="Spending category")
    description: str = Field(..., min_length=1, max_length=255, description="Description of spending")
    
    @validator('category')
    def category_must_be_alphanumeric(cls, v):
        if not v.replace(' ', '').replace('_', '').isalnum():
            raise ValueError('Category must be alphanumeric')
        return v.strip()
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        return v.strip()


class SpendResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryTotal(BaseModel):
    category: str
    total: float


class CategoryTotalsResponse(BaseModel):
    category_totals_today: list[CategoryTotal]


class TotalSpendResponse(BaseModel):
    total_spend: float