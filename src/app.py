from fastapi import FastAPI, Body, Query, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import DocumentCreate, DocumentListResponse, DocumentResponse, DocumentAttributes
from .db import Database
from pathlib import Path
from datetime import datetime
import shutil
from ml_module.text_extractor import extract_text
from ml_module.field_extractor import extract_fields_regex, validate_against_text
from ml_module import extract_fields

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
    
@app.post('/upload')
async def get_text(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    print(type(file_path))
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    text = extract_text(str(file_path))
    
    print(type(text))
    
    return {'raw_text': text}
        
    
    

# @app.post('/upload', response_model=DocumentResponse)
# async def upload(file: UploadFile = File(...)):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     safe_filename = f"{timestamp}_{file.filename}"
#     file_path = UPLOAD_DIR / safe_filename

#     print(type(file_path))
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    

#     fields = extract_fields(str(file_path))
    
#     doc_id = db.add_doc(file.filename, 'admin')
    
#     print(doc_id)
    
#     db.save_attributes(doc_id, fields)
    
#     print(fields)
    
#     return DocumentResponse(
#         id=doc_id,
#         filename=file.filename,
#         attributes=DocumentAttributes(
#             number=fields.get("number"),
#             date=fields.get("date"),
#             amount=fields.get("amount"),
#             parties=fields.get("parties",[]),
#             additional_data={}
#         ),
#         description="",
#         created_at=datetime.now()
#     )


@app.get('/documents', response_model=DocumentListResponse)
async def get_docs():
    # docs = db.get_docs_by_user('admin')
    docs = db.get_all_docs()
    
    docs_list = []
    
    for i in docs:
        attr = db.get_attributes(i[0])
        docs_list.append(DocumentResponse(
            id=i[0],
            filename=i[1],
            attributes=attr,
            description="",
            created_at=i[2]
        ))
        
        return DocumentListResponse(
            number=len(docs_list),
            items=docs_list
        )
        
@app.get('/documents/{doc_id}', response_model=DocumentResponse)
async def get_doc(doc_id: int):
    doc = db.get_doc(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    attr = db.get_attributes(doc_id)
    
    return DocumentResponse(
        id=doc[0],
        filename=doc[1],
        attributes=attr,
        description="",
        created_at=doc[2]
    )
    

        
    
    
    
