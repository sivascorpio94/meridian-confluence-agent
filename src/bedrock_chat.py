"""Minimal Bedrock Converse client used before introducing LangChain."""

from __future__ import annotations

import time
from dataclasses import dataclass


DEFAULT_CHAT_MODEL_ID = "us.meta.llama3-3-70b-instruct-v1:0"


@dataclass(frozen=True)
class ChatResult:
    text: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str


class BedrockChatClient:
    def __init__(
        self,
        region: str = "us-east-2",
        model_id: str = DEFAULT_CHAT_MODEL_ID,
        client=None,
    ):
        self.model_id = model_id
        if client is None:
            try:
                import boto3
                from botocore.config import Config
            except ImportError as exc:
                raise RuntimeError(
                    "Install dependencies with: python -m pip install -e ."
                ) from exc
            client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                config=Config(
                    connect_timeout=5,
                    read_timeout=30,
                    retries={"mode": "standard", "max_attempts": 3},
                ),
            )
        self.client = client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 700,
    ) -> ChatResult:
        if not 0 <= temperature <= 1:
            raise ValueError("temperature must be between 0 and 1")
        started = time.perf_counter()
        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": 0.9,
            },
        )
        content = response["output"]["message"]["content"]
        text = "\n".join(block["text"] for block in content if "text" in block).strip()
        usage = response.get("usage", {})
        metrics = response.get("metrics", {})
        elapsed_ms = int((time.perf_counter() - started) * 1_000)
        return ChatResult(
            text=text,
            model_id=self.model_id,
            input_tokens=int(usage.get("inputTokens", 0)),
            output_tokens=int(usage.get("outputTokens", 0)),
            latency_ms=int(metrics.get("latencyMs", elapsed_ms)),
            stop_reason=response.get("stopReason", "unknown"),
        )
