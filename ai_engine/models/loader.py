from llm.client import OllamaClient


class ModelLoader:
    """Loads and verifies models through the local Ollama runtime."""

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def is_available(self, model_name: str) -> bool:
        """Check whether a model is available in Ollama."""

        models = self.client.list_models()

        for model in models:
            if model.get("name") == model_name:
                return True

        return False