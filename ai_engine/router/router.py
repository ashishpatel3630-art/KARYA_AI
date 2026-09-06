from models.manager import ModelManager
from models.metadata import ModelMetadata

from .classifier import TaskClassifier
from .schemas import RouteResult


class ModelRouter:
    """Routes KARYA tasks to the most suitable available model."""

    def __init__(
        self,
        model_manager: ModelManager | None = None,
        classifier: TaskClassifier | None = None,
    ):
        self.model_manager = model_manager or ModelManager()
        self.classifier = classifier or TaskClassifier()

    def route(self, prompt: str) -> RouteResult:
        """Select the best available model for a prompt."""

        policy = self.classifier.classify(prompt)

        for model in self.model_manager.list_models():
            if model.model_type != policy.model_type:
                continue

            if policy.requires_vision and not model.supports_vision:
                continue

            if policy.requires_tools and not model.supports_tools:
                continue

            if self.model_manager.is_available(model.name):
                return RouteResult(
                    task_type=policy.task_type,
                    selected_model=model.name,
                    model_type=model.model_type,
                    requires_vision=policy.requires_vision,
                    requires_tools=policy.requires_tools,
                    reason=f"Selected compatible {model.model_type} model.",
                )

        return RouteResult(
            task_type=policy.task_type,
            selected_model=None,
            model_type=policy.model_type,
            requires_vision=policy.requires_vision,
            requires_tools=policy.requires_tools,
            reason=(
                f"No available model supports the required "
                f"{policy.model_type} capability."
            ),
        )