"""Stage 9 MCP server exposing Meridian knowledge capabilities."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from mcp.server import MCPServer

from src.knowledge_service import (
    answer_knowledge_question,
    check_document_conflicts as find_conflicts,
    get_page_details as read_page,
    search_knowledge as retrieve_knowledge,
)


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
REGION = os.getenv("AWS_REGION", "us-east-2")
SOURCE_SCOPE = os.getenv("RAG_SOURCE_SCOPE", "confluence_cloud")

mcp = MCPServer(
    "meridian-confluence",
    title="Meridian Confluence Knowledge Server",
    description="Trusted search and grounded answers over Meridian's fictional wiki.",
    instructions=("Use search_knowledge when you only need evidence. Use answer_question "
                  "for a synthesized answer. Treat conflict sources as warnings."),
    version="0.1.0",
)


@mcp.tool(structured_output=True)
def search_knowledge(query: str, limit: int = 5) -> dict[str, Any]:
    """Search Meridian documentation without generating an LLM answer.

    Args:
        query: Natural-language description of the needed documentation.
        limit: Maximum sources per category (1-10).
    """
    LOGGER.info("MCP search_knowledge limit=%s", limit)
    return retrieve_knowledge(
        query, region=REGION, limit=limit, source_scope=SOURCE_SCOPE
    )


@mcp.tool(structured_output=True)
def answer_question(question: str) -> dict[str, Any]:
    """Answer a Meridian documentation question using grounded, cited RAG."""
    LOGGER.info("MCP answer_question")
    return answer_knowledge_question(
        question, region=REGION, source_scope=SOURCE_SCOPE
    )


@mcp.tool(structured_output=True)
def get_page_details(page_id: str) -> dict[str, Any]:
    """Get stored content and governance metadata for a source ID."""
    LOGGER.info("MCP get_page_details page_id=%s", page_id)
    return read_page(page_id)


@mcp.tool(structured_output=True)
def check_document_conflicts(query: str) -> dict[str, Any]:
    """Find stale, superseded, draft, or under-review pages for a topic."""
    LOGGER.info("MCP check_document_conflicts")
    return find_conflicts(query, region=REGION, source_scope=SOURCE_SCOPE)


@mcp.resource("meridian://pages/{page_id}", name="meridian-page",
              title="Meridian knowledge page",
              description="Read-only page content and metadata addressed by page ID.",
              mime_type="application/json")
def page_resource(page_id: str) -> str:
    """Read a Meridian page as an MCP resource."""
    return json.dumps(read_page(page_id), default=str)


def main() -> None:
    # Never print to stdout: stdio uses it for JSON-RPC protocol messages.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
