from mcp.gateway.registry import registry


def search(query: str, top_k: int = 5) -> dict:
    """
    Search KARYA's knowledge layer.

    This is currently a safe placeholder.
    Later connect this to your actual RAG pipeline.
    """

    return {
        "query": query,
        "top_k": top_k,
        "results": [],
        "source": "karya-knowledge",
    }


def get_document(document_id: str) -> dict:
    return {
        "document_id": document_id,
        "status": "not_connected",
    }


registry.register(
    name="search",
    server="knowledge",
    description="Search KARYA knowledge base",
    handler=search,
)

registry.register(
    name="get_document",
    server="knowledge",
    description="Retrieve a document from knowledge base",
    handler=get_document,
)