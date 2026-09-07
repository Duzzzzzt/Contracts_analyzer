from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from datetime import date as datet



class DocumentCreate(BaseModel):
    filename: str


class DocumentAttributes(BaseModel):
    number: str
    date: datet
    amount: float
    parties: List[str]
    additional_data: dict = {}

class DocumentResponse(BaseModel):
    id: int
    filename: str
    attributes: DocumentAttributes
    description: str
    created_at: datetime
    status: str

class DocumentListResponse(BaseModel):
    number: int
    items: List[DocumentResponse]
    

    
    