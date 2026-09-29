"""Small pgvector repository used before introducing a framework abstraction."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SOURCE_SCOPES = {"all", "confluence_cloud", "frozen_corpus"}


def _source_clause(source_scope: str) -> tuple[str, tuple]:
    if source_scope not in SOURCE_SCOPES:
        raise ValueError(f"source_scope must be one of: {', '.join(sorted(SOURCE_SCOPES))}")
    if source_scope == "all":
        return "", ()
    if source_scope == "confluence_cloud":
        return "WHERE metadata->>'source' = %s", (source_scope,)
    return "WHERE COALESCE(metadata->>'source', 'frozen_corpus') = %s", (source_scope,)


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    page_id: str
    title: str
    section_path: tuple[str, ...]
    content: str
    metadata: dict
    similarity: float


def database_url() -> str:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is not set; copy .env.example to .env")
    return value


def connect(dsn: str | None = None):
    try:
        import psycopg
        from pgvector.psycopg import register_vector
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: python -m pip install -e .") from exc

    connection = psycopg.connect(dsn or database_url())
    connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
    connection.commit()
    register_vector(connection)
    return connection


def initialize_schema(connection, schema_path: Path = Path("sql/001_document_chunks.sql")) -> None:
    connection.execute(schema_path.read_text(encoding="utf-8"))
    connection.commit()


def existing_hashes(connection, chunk_ids: Sequence[str]) -> dict[str, str]:
    if not chunk_ids:
        return {}
    rows = connection.execute(
        "SELECT chunk_id, content_hash FROM document_chunks WHERE chunk_id = ANY(%s)",
        (list(chunk_ids),),
    ).fetchall()
    return {row[0]: row[1].strip() for row in rows}


def prune_source_chunks(connection, active_chunk_ids: Sequence[str],
                        source: str = "confluence_cloud") -> int:
    """Delete obsolete chunks for one explicit source, never other corpora."""
    if not source:
        raise ValueError("source is required for safe pruning")
    if active_chunk_ids:
        cursor = connection.execute(
            """DELETE FROM document_chunks
               WHERE metadata->>'source' = %s AND NOT (chunk_id = ANY(%s))""",
            (source, list(active_chunk_ids)),
        )
    else:
        cursor = connection.execute(
            "DELETE FROM document_chunks WHERE metadata->>'source' = %s",
            (source,),
        )
    connection.commit()
    return cursor.rowcount


def load_page_metadata(connection, source_scope: str = "all") -> list[dict]:
    where_clause, parameters = _source_clause(source_scope)
    rows = connection.execute(
        f"""
        SELECT DISTINCT ON (page_id) metadata
        FROM document_chunks
        {where_clause}
        ORDER BY page_id, chunk_id
        """,
        parameters,
    ).fetchall()
    return [row[0] for row in rows]


def upsert_chunk(connection, chunk: dict, content_hash: str, result) -> None:
    from pgvector import Vector
    from psycopg.types.json import Jsonb

    connection.execute(
        """
        INSERT INTO document_chunks (
            chunk_id, page_id, title, section_path, content, embedding_text,
            content_hash, metadata, embedding_model, embedding_dimensions,
            embedding, input_token_count
        ) VALUES (
            %(chunk_id)s, %(page_id)s, %(title)s, %(section_path)s, %(content)s,
            %(embedding_text)s, %(content_hash)s, %(metadata)s,
            %(embedding_model)s, %(embedding_dimensions)s, %(embedding)s,
            %(input_token_count)s
        )
        ON CONFLICT (chunk_id) DO UPDATE SET
            page_id = EXCLUDED.page_id,
            title = EXCLUDED.title,
            section_path = EXCLUDED.section_path,
            content = EXCLUDED.content,
            embedding_text = EXCLUDED.embedding_text,
            content_hash = EXCLUDED.content_hash,
            metadata = EXCLUDED.metadata,
            embedding_model = EXCLUDED.embedding_model,
            embedding_dimensions = EXCLUDED.embedding_dimensions,
            embedding = EXCLUDED.embedding,
            input_token_count = EXCLUDED.input_token_count,
            updated_at = NOW()
        """,
        {
            **chunk,
            "content": chunk["text"],
            "content_hash": content_hash,
            "metadata": Jsonb(chunk["metadata"]),
            "embedding_model": result.model_id,
            "embedding_dimensions": len(result.vector),
            "embedding": Vector(list(result.vector)),
            "input_token_count": result.input_token_count,
        },
    )
    connection.commit()


def similarity_search(connection, query_vector: Iterable[float], limit: int = 5,
                      source_scope: str = "all") -> list[SearchHit]:
    from pgvector import Vector

    vector = Vector(list(query_vector))
    where_clause, source_parameters = _source_clause(source_scope)
    rows = connection.execute(
        f"""
        SELECT chunk_id, page_id, title, section_path, content, metadata,
               1 - (embedding <=> %s) AS similarity
        FROM document_chunks
        {where_clause}
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (vector, *source_parameters, vector, limit),
    ).fetchall()
    return [
        SearchHit(
            chunk_id=row[0],
            page_id=row[1],
            title=row[2],
            section_path=tuple(row[3]),
            content=row[4],
            metadata=row[5],
            similarity=float(row[6]),
        )
        for row in rows
    ]
