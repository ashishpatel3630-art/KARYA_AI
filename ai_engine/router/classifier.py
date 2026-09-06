from .policies import (
    RoutingPolicy,
    TEXT_POLICY,
    TOOL_POLICY,
    VISION_POLICY,
)


class TaskClassifier:
    """Classifies user requests into routing policies."""

    def classify(self, prompt: str) -> RoutingPolicy:
        """Determine the required capability for a user prompt."""

        text = prompt.lower().strip()

        if not text:
            return TEXT_POLICY

        vision_keywords = [
            "image",
            "photo",
            "picture",
            "drawing",
            "diagram",
            "scan",
            "engineering drawing",
        ]

        tool_keywords = [
            "calculate",
            "calculation",
            "compute",
            "solve",
            "sum",
            "multiply",
            "divide",
        ]

        if any(keyword in text for keyword in vision_keywords):
            return VISION_POLICY

        if any(keyword in text for keyword in tool_keywords):
            return TOOL_POLICY

        return TEXT_POLICY
