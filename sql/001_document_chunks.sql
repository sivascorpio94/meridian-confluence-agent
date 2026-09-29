CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    page_id TEXT NOT NULL,
    title TEXT NOT NULL,
    section_path TEXT[] NOT NULL DEFAULT '{}',
    content TEXT NOT NULL,
    embedding_text TEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    metadata JSONB NOT NULL,
    embedding_model TEXT NOT NULL,
    embedding_dimensions SMALLINT NOT NULL CHECK (embedding_dimensions = 1024),
    embedding VECTOR(1024) NOT NULL,
    input_token_count INTEGER NOT NULL CHECK (input_token_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS document_chunks_page_id_idx
    ON document_chunks (page_id);

CREATE INDEX IF NOT EXISTS document_chunks_metadata_idx
    ON document_chunks USING GIN (metadata);

CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx
    ON document_chunks USING HNSW (embedding vector_cosine_ops);

