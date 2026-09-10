from fastapi import APIRouter

from ai_engine.llm.service import LLMService

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI"],
)

llm_service = LLMService()


@router.get("/health")
async def ai_health():
    """
    Check local AI runtime availability.
    """

    available = llm_service.health()

    return {
        "service": "karya-ai-runtime",
        "provider": "ollama",
        "status": "healthy" if available else "unavailable",
    }


@router.get("/models")
async def available_models():
    """
    List locally available Ollama models.
    """

    models = llm_service.models()

    return {
        "count": len(models),
        "models": models,
    }