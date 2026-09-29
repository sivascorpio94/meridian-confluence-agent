"""Direct Amazon Bedrock embeddings client used before LangChain is introduced."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Sequence


MODEL_ID = "amazon.titan-embed-text-v2:0"
DEFAULT_DIMENSIONS = 1024


@dataclass(frozen=True)
class EmbeddingResult:
    vector: tuple[float, ...]
    input_token_count: int
    model_id: str


class BedrockEmbeddingClient:
    def __init__(
        self,
        region: str = "us-east-1",
        model_id: str = MODEL_ID,
        dimensions: int = DEFAULT_DIMENSIONS,
    ) -> None:
        if dimensions not in {256, 512, 1024}:
            raise ValueError("Titan V2 dimensions must be 256, 512, or 1024")
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            raise RuntimeError("Install project dependencies with: pip install -e .") from exc

        self.model_id = model_id
        self.dimensions = dimensions
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(
                connect_timeout=5,
                read_timeout=30,
                retries={"mode": "standard", "max_attempts": 3},
            ),
        )

    def embed(self, text: str) -> EmbeddingResult:
        if not text.strip():
            raise ValueError("Embedding input cannot be empty")

        request = {
            "inputText": text,
            "dimensions": self.dimensions,
            "normalize": True,
            "embeddingTypes": ["float"],
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request),
            accept="application/json",
            contentType="application/json",
        )
        payload = json.loads(response["body"].read())
        vector = tuple(float(value) for value in payload["embedding"])
        if len(vector) != self.dimensions:
            raise ValueError(
                f"Expected {self.dimensions} dimensions, received {len(vector)}"
            )
        return EmbeddingResult(
            vector=vector,
            input_token_count=int(payload["inputTextTokenCount"]),
            model_id=self.model_id,
        )


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vectors must have the same dimensions")
    if not left:
        raise ValueError("Vectors cannot be empty")

    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")
    return dot_product / (left_norm * right_norm)
