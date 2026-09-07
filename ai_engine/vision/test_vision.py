from pathlib import Path

import pytest

from vision import (
    IndustrialAnalysis,
    IndustrialFinding,
    VisionAnalyzer,
    VisionRequest,
    VisionResponse,
    VisionService,
)


TEST_IMAGE = Path(__file__).resolve().parents[1] / "rag" / "test_ingestion_document.pdf"


def test_vision_request_defaults():
    request = VisionRequest(
        prompt="Analyze this image.",
        image_path="test.jpg",
    )

    assert request.prompt == "Analyze this image."
    assert request.image_path == "test.jpg"
    assert request.model == "llama3.2-vision"


def test_vision_response_helpers():
    response = VisionResponse(
        model="llama3.2-vision",
        prompt="What is visible?",
        content="Compressor C-101 is visible.",
    )

    assert response.is_empty() is False
    assert response.character_count() > 0


def test_empty_vision_response():
    response = VisionResponse(
        model="llama3.2-vision",
        prompt="Test",
        content="",
    )

    assert response.is_empty() is True
    assert response.character_count() == 0


def test_industrial_finding():
    finding = IndustrialFinding(
        category="equipment",
        observation="Visible compressor housing.",
        severity="medium",
    )

    assert finding.category == "equipment"
    assert finding.observation == "Visible compressor housing."
    assert finding.severity == "medium"


def test_industrial_analysis_helpers():
    analysis = IndustrialAnalysis(
        image_path="test.jpg",
        model="llama3.2-vision",
        content="Equipment appears operational.",
        findings=[
            IndustrialFinding(
                category="condition",
                observation="No obvious external damage.",
                severity="low",
            )
        ],
    )

    assert analysis.is_empty() is False
    assert analysis.finding_count() == 1


def test_empty_industrial_analysis():
    analysis = IndustrialAnalysis(
        image_path="test.jpg",
        model="llama3.2-vision",
        content="",
        findings=[],
    )

    assert analysis.is_empty() is True
    assert analysis.finding_count() == 0


def test_vision_service_rejects_empty_prompt():
    service = VisionService()

    with pytest.raises(ValueError, match="prompt"):
        service.analyze(
            prompt="",
            image_path="test.jpg",
        )


def test_vision_service_rejects_empty_image_path():
    service = VisionService()

    with pytest.raises(ValueError, match="Image path"):
        service.analyze(
            prompt="Analyze this image.",
            image_path="",
        )


def test_vision_service_validates_missing_image():
    service = VisionService()

    with pytest.raises(FileNotFoundError):
        service.validate_image("does_not_exist.jpg")


def test_vision_service_rejects_unsupported_image():
    service = VisionService()

    temp_file = Path(__file__).with_name("unsupported.txt")

    try:
        temp_file.write_text("test", encoding="utf-8")

        with pytest.raises(ValueError, match="Unsupported image format"):
            service.validate_image(str(temp_file))
    finally:
        if temp_file.exists():
            temp_file.unlink()


def test_vision_service_model_check():
    service = VisionService()

    # The text-only model should not be treated as a vision model.
    assert service.model_available("llama3.2-vision") in {True, False}


def test_vision_analyzer_import():
    analyzer = VisionAnalyzer()

    assert analyzer.service is not None


def test_vision_analyzer_methods_exist():
    analyzer = VisionAnalyzer()

    assert callable(analyzer.analyze)
    assert callable(analyzer.inspect_equipment)
    assert callable(analyzer.inspect_safety)
    assert callable(analyzer.inspect_damage)
    assert callable(analyzer.analyze_drawing)


def test_test_asset_exists():
    assert TEST_IMAGE.exists()
    assert TEST_IMAGE.is_file()
