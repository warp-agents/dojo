from pydantic import BaseModel 
from typing import List, Optional

class FileData(BaseModel):
    name: str
    content: str  # base64 encoded content
    type: str

class ProcessRequest(BaseModel):
    prompt: str
    model: str
    files: Optional[List[FileData]] = []
    
class GenerateRequest(BaseModel):
    system_prompt: str
    prompt: str
    model: str

class GenerateLiteRequest(BaseModel):
    system_prompt: str
    prompt: str

class SearchRequest(BaseModel):
    prompt: str

class HealthResponse(BaseModel):
    status: str
    message: str