from pydantic import BaseModel
from typing import List
from datetime import datetime, date



class DocumentCreate(BaseModel):
    filename: str


class DocumentAttributes(BaseModel):
    number: str
    date: date
    amount: float
    parties: List[str]
    additional_data: dict = {}

class DocumentResponse(BaseModel):
    id: int
    filename: str
    attributes: DocumentAttributes
    description: str
    created_at: datetime

class DocumentListResponse(BaseModel):
    number: int
    items: List[DocumentResponse]
    

    
    