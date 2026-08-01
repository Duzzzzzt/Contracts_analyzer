import fitz         
from docx import Document 

def extract_text(file_path: str) -> str:
    """
    Принимает путь к файлу (.pdf или .docx).
    Возвращает весь текст документа одной строкой.
    """
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        return text

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Неподдерживаемый формат: {file_path}")
