from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from datetime import date as datet



class DocumentCreate(BaseModel):
    filename: str


class DocumentAttributes(BaseModel):
    number: Optional[str] = None
    date: Optional[datet] = None
    amount: Optional[float] = None
    parties: Optional[List[str]] = None
    additional_data: Optional[dict] = None

class DocumentResponse(BaseModel):
    id: Optional[int] = int
    filename: Optional[str] = None
    attributes: Optional[DocumentAttributes] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None

class DocumentListResponse(BaseModel):
    number: int
    items: List[DocumentResponse]
    

    
    