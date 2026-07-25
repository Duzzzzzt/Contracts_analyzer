from pydantic import BaseModel
from typing import List
from datetime import datetime, date


class DocumentCreate(BaseModel):
    number: str
    date: datetime.date
    amount: float
    parties: List[str]
    description: str = ""
    additional_data: dict = {}



class DocumentResponse(BaseModel):
    id: int
    number: str
    date: datetime.date
    amount: float
    parties: List[str]
    description: str
    created_at: datetime
    

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int

    
    