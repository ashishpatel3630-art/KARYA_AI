from .loader import ModelLoader
from .metadata import ModelMetadata
from .registry import ModelRegistry


class ModelManager:
    """Central manager for KARYA AI models."""

    def __init__(
        self,
        registry: ModelRegistry | None = None,
        loader: ModelLoader | None = None,
    ):
        self.registry = registry or ModelRegistry()
        self.loader = loader or ModelLoader()

    def register_model(self, model: ModelMetadata) -> None:
        """Register a model in KARYA's model registry."""

        self.registry.register(model)

    def get_model(self, model_name: str) -> ModelMetadata | None:
        """Return model metadata."""

        return self.registry.get(model_name)

    def list_models(self) -> list[ModelMetadata]:
        """Return all registered models."""

        return self.registry.list_models()

    def is_available(self, model_name: str) -> bool:
        """Check whether a registered model is available locally."""

        if not self.registry.exists(model_name):
            return False

        return self.loader.is_available(model_name)
