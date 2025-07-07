from sentence_transformers import SentenceTransformer, util
from sklearn.preprocessing import minmax_scale
from functools import lru_cache
import logging

from .llm_service import call_model
from ..prompts.templates import prompt_templates

@lru_cache
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def route_prompt(user_prompt: str) -> tuple[str, float]:
    """Determines the best system prompt template for a user query."""
    embedding_model = get_embedding_model()

    # Embedding-based similarity
    user_emb = embedding_model.encode(user_prompt, convert_to_tensor=True)
    prompt_embeddings = {
        label: embedding_model.encode(info["desc"], convert_to_tensor=True)
        for label, info in prompt_templates.items()
    }
    raw_similarities = {
        label: float(util.pytorch_cos_sim(user_emb, emb))
        for label, emb in prompt_embeddings.items()
    }
    norm_similarities = {
        label: score for label, score in zip(raw_similarities.keys(), minmax_scale(list(raw_similarities.values())))
    }

    # LLM-based classification
    prompt_list = "\n".join(
        [f"- {label}: {info['desc']}" for label, info in prompt_templates.items()]
    )
    classification_prompt = f"""You are a routing assistant. Choose the best system prompt from the list below to respond to the user's request.

Prompts:
{prompt_list}

User prompt: "{user_prompt}"

Respond with only the prompt label (e.g., 'Default')."""

    try:
        llm_label = call_model(
            prompt=classification_prompt,
            model="gpt-4.1-2025-04-14", # A capable model for classification
            fallback_model="deepseek/deepseek-r1-0528:free",
            temperature=0.0,
            max_tokens=50
        ).strip()
    except Exception as e:
        logging.warning(f"LLM classification failed: {e}. Defaulting to similarity.")
        llm_label = max(norm_similarities, key=norm_similarities.get)

    # Fuse scores
    llm_conf = {label: 1.0 if label.lower() in llm_label.lower() else 0.0 for label in prompt_templates}
    
    embedding_weight = 0.6
    llm_weight = 0.4
    fused_scores = {
        label: (embedding_weight * norm_similarities.get(label, 0)) + (llm_weight * llm_conf.get(label, 0))
        for label in prompt_templates
    }
    
    best_label, best_score = max(fused_scores.items(), key=lambda item: item[1])
    
    # Fallback to default if confidence is low
    final_label = "Default" if best_score < 0.85 else best_label
    
    logging.info(f"Routing result: User prompt routed to '{final_label}' with score {best_score:.2f}")
    return final_label, best_score