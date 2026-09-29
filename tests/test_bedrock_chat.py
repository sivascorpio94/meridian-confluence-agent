import unittest
from unittest.mock import Mock

from src.bedrock_chat import BedrockChatClient


class BedrockChatTests(unittest.TestCase):
    def test_converse_response_is_normalized(self):
        runtime = Mock()
        runtime.converse.return_value = {
            "output": {"message": {"content": [{"text": "Answer [page-01]."}]}},
            "usage": {"inputTokens": 100, "outputTokens": 12},
            "metrics": {"latencyMs": 345},
            "stopReason": "end_turn",
        }
        client = BedrockChatClient(
            region="us-east-2", model_id="test-model", client=runtime
        )

        result = client.generate("system", "user", temperature=0.1, max_tokens=50)

        self.assertEqual("Answer [page-01].", result.text)
        self.assertEqual(100, result.input_tokens)
        self.assertEqual(12, result.output_tokens)
        self.assertEqual(345, result.latency_ms)
        runtime.converse.assert_called_once()

    def test_invalid_temperature_is_rejected(self):
        client = BedrockChatClient(client=Mock())
        with self.assertRaises(ValueError):
            client.generate("system", "user", temperature=1.1)


if __name__ == "__main__":
    unittest.main()
