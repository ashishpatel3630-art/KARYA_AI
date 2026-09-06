from .metadata import ModelMetadata


class ModelRegistry:
    """Registry of AI models available to KARYA."""

    def __init__(self):
        self._models: dict[str, ModelMetadata] = {}

    def register(self, model: ModelMetadata) -> None:
        """Register a model."""

        self._models[model.name] = model

    def get(self, model_name: str) -> ModelMetadata | None:
        """Get model metadata by name."""

        return self._models.get(model_name)

    def list_models(self) -> list[ModelMetadata]:
        """Return all registered models."""

        return list(self._models.values())

    def exists(self, model_name: str) -> bool:
        """Check whether a model is registered."""

        return model_name in self._models
