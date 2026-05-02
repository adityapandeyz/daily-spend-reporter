from pydantic import BaseModel

class SpendCreate(BaseModel):
    amount: float
    category: str
    description: str