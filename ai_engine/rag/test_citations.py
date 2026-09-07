from agents.executor import AgentExecutor
from agents.loop import AgentLoop
from agents.state import AgentState
from orchestrator.executor import OrchestratorExecutor
from orchestrator.orchestrator import KARYAOrchestrator
from orchestrator.schemas import (
    ExecutionPlan,
    ExecutionStep,
    OrchestrationRequest,
)
from rag.schemas import Citation, RAGResponse, deduplicate_citations
from tools.schemas import ToolCall, ToolResult


class CitationToolRegistry:
    def __init__(self, result: ToolResult):
        self.result = result

    def exists(self, tool_name: str) -> bool:
        return tool_name == "rag"

    def execute(self, tool_call: ToolCall) -> ToolResult:
        return self.result


class CitationRAGService:
    def __init__(self, response: RAGResponse):
        self.response = response

    def answer(self, **kwargs) -> RAGResponse:
        return self.response


def make_citation(
    similarity: float = 0.88,
    chunk_id: int = 7,
) -> Citation:
    return Citation(
        document_id="document-1",
        file_name="test.pdf",
        file_type=".pdf",
        page_number=3,
        chunk_id=chunk_id,
        source_text="Verified source text.",
        similarity=similarity,
    )


def test_citation_creation_preserves_retrieval_metadata():
    citation = make_citation()

    assert citation.document_id == "document-1"
    assert citation.file_name == "test.pdf"
    assert citation.file_type == ".pdf"
    assert citation.page_number == 3
    assert citation.chunk_id == 7
    assert citation.source_text == "Verified source text."
    assert citation.similarity == 0.88


def test_rag_tool_preserves_structured_sources():
    from tools.rag import RAGTool

    citation = make_citation()
    response = RAGResponse(answer="Grounded answer.", citations=[citation])
    tool = RAGTool(
        rag_service=CitationRAGService(response)
    )

    result = tool.execute("What is documented?")

    assert result.success is True
    assert result.output == "Grounded answer."
    assert result.citations == [citation]


def test_citations_propagate_through_agent_and_are_rendered_once():
    citation = make_citation()
    registry = CitationToolRegistry(
        ToolResult(
            tool_name="rag",
            success=True,
            output="The report records the measured value.",
            citations=[citation, citation],
        )
    )
    state = AgentState(
        user_input="Read the report.",
        plan=[
            {
                "step_id": "step_1",
                "action": "Read the report.",
                "tool": "rag",
                "arguments": {"question": "What is documented?"},
            }
        ],
    )

    AgentExecutor(tool_registry=registry).execute_current_step(state)
    AgentLoop._set_final_answer(AgentLoop(), state)

    assert state.citations == [citation]
    assert state.tool_results[0]["citations"] == [citation]
    assert state.final_answer.count("[1] test.pdf - Page 3, Chunk 7") == 1


def test_deduplication_keeps_highest_similarity_for_same_source():
    lower = make_citation(similarity=0.70)
    higher = make_citation(similarity=0.88)

    result = deduplicate_citations([lower, higher])

    assert result == [higher]


def test_missing_sources_do_not_create_citations():
    response = RAGResponse(answer="No verified source was available.", citations=[])
    tool = CitationRAGService(response)

    assert tool.answer(question="question").citations == []


def test_citations_propagate_through_orchestrator():
    citation = make_citation()
    registry = CitationToolRegistry(
        ToolResult(
            tool_name="rag",
            success=True,
            output="Grounded orchestration answer.",
            citations=[citation],
        )
    )
    request = OrchestrationRequest(user_input="Search the report.")
    plan = ExecutionPlan(request=request)
    plan.add_step(
        ExecutionStep(
            step_id="rag_step",
            action="Search the report.",
            description="Search the report.",
            component="rag",
            arguments={"question": "What is documented?"},
        )
    )

    result = OrchestratorExecutor(
        tool_registry=registry,
    ).execute(plan)

    assert result.success is True
    assert result.citations == [citation]
    assert result.step_results[0].citations == [citation]

    final = KARYAOrchestrator()._finalize_result(result)
    assert "Sources:" in final.answer
    assert "[1] test.pdf - Page 3, Chunk 7" in final.answer
