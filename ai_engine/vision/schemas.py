from dataclasses import dataclass


@dataclass(frozen=True)
class VisionRequest:
    """
    Request sent to the local vision model.
    """

    prompt: str
    image_path: str
    model: str = "llama3.2-vision"


@dataclass(frozen=True)
class VisionResponse:
    """
    Response returned by the vision model.
    """

    model: str
    prompt: str
    content: str

    def is_empty(self) -> bool:
        return not self.content.strip()

    def character_count(self) -> int:
        return len(self.content)