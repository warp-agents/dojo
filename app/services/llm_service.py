import openai
import google.generativeai as genai
import logging
from functools import lru_cache
from ..core.config import settings

logging.basicConfig(level=logging.INFO)

# Use @lru_cache to ensure clients are initialized only once
@lru_cache
def get_llm7_client():
    try:
        return openai.OpenAI(
            base_url="https://api.llm7.io/v1",
            api_key=settings.LLM7_IO_API_KEY
        )
    except Exception as e:
        logging.error(f"Failed to initialize llm7.io client: {e}")
        return None

@lru_cache
def get_openrouter_client():
    try:
        return openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
    except Exception as e:
        logging.error(f"Failed to initialize OpenRouter client: {e}")
        return None

@lru_cache
def get_google_genai_model(model_name: str = "gemma-3-4b-it"):
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY_EXT)
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logging.error(f"Failed to initialize Google GenAI model: {e}")
        return None

def call_model(
    prompt: str,
    model: str = "gpt-4o-mini-2024-07-18",
    fallback_model: str = "mistralai/mistral-7b-instruct:free",
    image_url: str = None,
    temperature: float = settings.DEFAULT_TEMPERATURE,
    top_p: float = settings.DEFAULT_TOP_P,
    max_tokens: int = 1024,
    system_prompt: str = None
) -> str:
    """Sends a prompt to an LLM, with a fallback mechanism."""
    llm7_client = get_llm7_client()
    openrouter_client = get_openrouter_client()

    messages_payload = []
    if system_prompt:
        messages_payload.append({"role": "system", "content": system_prompt})
    
    user_content = [{"type": "text", "text": prompt}]
    if image_url:
        user_content.append({"type": "image_url", "image_url": {"url": image_url}})
    messages_payload.append({"role": "user", "content": user_content})

    # Attempt 1: llm7.io
    if llm7_client:
        try:
            logging.info(f"Attempting API call to llm7.io with model: {model}")
            completion = llm7_client.chat.completions.create(
                model=model,
                messages=messages_payload,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            response_content = completion.choices[0].message.content
            if response_content:
                return response_content.strip()
        except Exception as e:
            logging.warning(f"llm7.io call failed for model '{model}': {e}")

    # Attempt 2: OpenRouter (Fallback)
    if openrouter_client:
        try:
            logging.info(f"Attempting fallback call to OpenRouter with model: {fallback_model}")
            completion = openrouter_client.chat.completions.create(
                model=fallback_model,
                messages=messages_payload,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            response_content = completion.choices[0].message.content
            if response_content:
                return response_content.strip()
        except Exception as e_or:
            logging.error(f"OpenRouter fallback failed for model '{fallback_model}': {e_or}")
            raise Exception("All API calls failed.") from e_or

    raise Exception("Failed to get response from any LLM provider.")