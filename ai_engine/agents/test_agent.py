import pytest
from reportlab.pdfgen import canvas

from agents.loop import AgentLoop


def create_test_pdf(file_path):
    pdf = canvas.Canvas(str(file_path))

    pdf.drawString(
        100,
        750,
        "KARYA AI Industrial Maintenance Report",
    )

    pdf.drawString(
        100,
        720,
        "Equipment: Compressor C-101",
    )

    pdf.drawString(
        100,
        690,
        "Temperature: 92 C",
    )

    pdf.drawString(
        100,
        660,
        "Vibration: 8.5 mm/s",
    )

    pdf.drawString(
        100,
        630,
        "Status: Critical",
    )

    pdf.drawString(
        100,
        600,
        "Immediate maintenance inspection is required.",
    )

    pdf.save()


def test_calculator_agent():
    agent = AgentLoop()

    state = agent.run(
        "Calculate 1200 + 3500"
    )

    assert state.error is None
    assert state.completed is True
    assert len(state.plan) == 1
    assert state.plan[0]["tool"] == "calculator"
    assert len(state.tool_calls) == 1
    assert state.tool_calls[0]["tool"] == "calculator"
    assert state.tool_calls[0]["success"] is True
    assert state.final_answer


def test_file_reader_agent(tmp_path):
    pdf_path = tmp_path / "test_agent_document.pdf"

    create_test_pdf(pdf_path)

    agent = AgentLoop()

    state = agent.run(
        f"Read {pdf_path}"
    )

    assert state.error is None
    assert state.completed is True
    assert len(state.plan) == 1
    assert state.plan[0]["tool"] == "file_reader"
    assert len(state.tool_calls) == 1
    assert state.tool_calls[0]["tool"] == "file_reader"
    assert state.tool_calls[0]["success"] is True
    assert "Compressor C-101" in state.tool_calls[0]["output"]


def test_search_agent():
    agent = AgentLoop()

    state = agent.run(
        "Find information about Compressor C-101"
    )

    assert state.error is None
    assert state.completed is True
    assert len(state.plan) == 1
    assert state.plan[0]["tool"] == "search"
    assert len(state.tool_calls) == 1
    assert state.tool_calls[0]["tool"] == "search"
    assert state.tool_calls[0]["success"] is True
    assert "Compressor C-101" in state.final_answer


def test_agent_rejects_empty_input():
    agent = AgentLoop()

    with pytest.raises(
        ValueError,
        match="User input cannot be empty",
    ):
        agent.run("")
