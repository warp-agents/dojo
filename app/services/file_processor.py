import io
import base64
import pandas as pd
import xml.etree.ElementTree as ET
from docx import Document as DocxDocument
from PyPDF2 import PdfReader

from ..api.v1.schemas import FileData

def process_file_content(file_data: FileData) -> str:
    """Decodes and extracts text content from various file types."""
    try:
        content = base64.b64decode(file_data.content)
        file_type = file_data.type

        if file_type.startswith('text/'):
            return content.decode('utf-8')
        elif file_type == 'application/pdf':
            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() for page in reader.pages)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = DocxDocument(io.BytesIO(content))
            return "\n".join(para.text for para in doc.paragraphs)
        elif file_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            return pd.read_excel(io.BytesIO(content)).to_string()
        elif file_type == 'text/csv':
            return pd.read_csv(io.StringIO(content.decode('utf-8'))).to_string()
        elif 'xml' in file_type:
            root = ET.fromstring(content.decode('utf-8'))
            return ET.tostring(root, encoding='unicode')
        else:
            return f"Unsupported file type: {file_type}"
    except Exception as e:
        return f"Error processing file {file_data.name}: {e}"