from fastapi import APIRouter, HTTPException, BackgroundTasks
from firecrawl import FirecrawlApp
import json
import logging

from .schemas import ProcessRequest, GenerateRequest, GenerateLiteRequest, SearchRequest
from ...services import file_processor, routing_service, llm_service
from ...prompts.templates import prompt_templates, url_extraction_system_prompt, content_extraction_system_prompt
from ...core.config import settings

router = APIRouter()
firecrawl_client = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)

@router.post("/process")
async def process_files_and_prompt(request: ProcessRequest, background_tasks: BackgroundTasks):
    try:
        # Note: File processing can be slow. For a real app, you'd use background tasks
        # and a notification system (e.g., websockets, webhooks)
        # file_contents = [
        #     f"--- START FILE: {file.name} ---\n{file_processor.process_file_content(file)}\n--- END FILE: {file.name} ---"
        #     for file in request.files
        # ]
        
        # context = "\n\n".join(file_contents)
        context = ""
        contextualized_prompt = f"Context from uploaded files:\n{context}\n\nUser's request: {request.prompt}"
        
        prediction, _ = routing_service.route_prompt(request.prompt)
        system_prompt = prompt_templates[prediction]["prompt"]
        
        response_content = llm_service.call_model(prompt=contextualized_prompt, system_prompt=system_prompt)
        
        return {"response": response_content, "prediction": prediction}
    except Exception as e:
        logging.error(f"Error in /process endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        response_content = llm_service.call_model(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            model=request.model
        )
        return {"response": response_content}
    except Exception as e:
        logging.error(f"Error in /generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-lite")
async def generate_text_lite(request: GenerateLiteRequest):
    try:
        model = llm_service.get_google_genai_model()
        if not model:
            raise HTTPException(status_code=503, detail="Google GenAI service unavailable")

        full_prompt = f"{request.system_prompt}\n\nPlease answer concisely.\n\n{request.prompt}"
        response = model.generate_content(full_prompt)
        
        return {"response": response.text.strip()}
    except Exception as e:
        logging.error(f"Error in /generate-lite endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_and_summarize(request: SearchRequest):
    try:
        # 1. Extract URL
        url_text = llm_service.call_model(
            prompt=request.prompt,
            system_prompt=url_extraction_system_prompt,
            model="mixtral-8x7b-instruct",
            temperature=0
        )
        if "no url found" in url_text.lower():
            raise HTTPException(status_code=400, detail="No URL found in the prompt.")
            
        # 2. Scrape URL
        scrape_result = firecrawl_client.scrape_url(url_text.strip(), params={'pageOptions': {'onlyMainContent': True}})
        markdown_content = scrape_result.get("markdown")
        if not markdown_content:
            raise HTTPException(status_code=500, detail="Failed to scrape content from URL.")
            
        # 3. Summarize Content
        summary = llm_service.call_model(
            prompt=markdown_content,
            system_prompt=content_extraction_system_prompt
        )
        return {"response": summary}
    except Exception as e:
        logging.error(f"Error in /search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))