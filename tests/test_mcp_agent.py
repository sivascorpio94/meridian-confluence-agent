import json
import unittest
from copy import deepcopy
from types import SimpleNamespace

from src.mcp_agent import (
    BedrockMcpAgent,
    ReusableMcpAgentRunner,
    bedrock_tool_config,
    mcp_result_payload,
    text_tool_uses,
)


class FakeMcpClient:
    def __init__(self):
        self.calls = []

    async def list_tools(self):
        return [SimpleNamespace(
            name="search_knowledge",
            description="Search evidence",
            input_schema={"type": "object", "properties": {
                "query": {"type": "string"}, "limit": {"type": "integer"}
            }, "required": ["query"]},
        )]

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return SimpleNamespace(
            structured_content={"status": "found", "sources": [{"page_id": "page-01"}]},
            content=[], is_error=False,
        )


class ManagedFakeMcpClient(FakeMcpClient):
    def __init__(self):
        super().__init__()
        self.enter_count = 0
        self.exit_count = 0

    async def __aenter__(self):
        self.enter_count += 1
        return self

    async def __aexit__(self, *exc_info):
        self.exit_count += 1


class FakeBedrockClient:
    def __init__(self):
        self.requests = []

    def converse(self, **request):
        self.requests.append(deepcopy(request))
        if len(self.requests) == 1:
            return {
                "output": {"message": {"role": "assistant", "content": [{
                    "toolUse": {"toolUseId": "call-1", "name": "search_knowledge",
                                "input": {"query": "Mosaic access", "limit": "5"}}
                }]}},
                "stopReason": "tool_use",
            }
        return {
            "output": {"message": {"role": "assistant", "content": [
                {"text": "Use ServiceNow [page-01]."}
            ]}},
            "stopReason": "end_turn", "usage": {"totalTokens": 42},
        }


class RepeatingBedrockClient:
    def __init__(self):
        self.count = 0

    def converse(self, **request):
        self.count += 1
        if self.count <= 2:
            return {"output": {"message": {"role": "assistant", "content": [{
                "toolUse": {"toolUseId": f"call-{self.count}",
                            "name": "search_knowledge",
                            "input": {"query": "Mosaic access"}}
            }]}}}
        return {"output": {"message": {"role": "assistant", "content": [
            {"text": "Finished after duplicate guard."}
        ]}}, "usage": {}}


class McpAgentHelpersTest(unittest.TestCase):
    def test_translates_mcp_schema_to_bedrock(self):
        tool = SimpleNamespace(name="lookup", description="Look up a page",
                               input_schema={"type": "object"})
        config = bedrock_tool_config([tool])
        spec = config["tools"][0]["toolSpec"]
        self.assertEqual("lookup", spec["name"])
        self.assertEqual({"json": {"type": "object"}}, spec["inputSchema"])

    def test_prefers_structured_content(self):
        result = SimpleNamespace(structured_content={"ok": True}, content=[])
        self.assertEqual({"ok": True}, mcp_result_payload(result))

    def test_normalizes_text_function_call_and_argument_types(self):
        tool = SimpleNamespace(
            name="search_knowledge", input_schema={"type": "object", "properties": {
                "query": {"type": "string"}, "limit": {"type": "integer"}
            }}
        )
        calls = text_tool_uses([{"text": json.dumps({
            "type": "function", "name": "search_knowledge",
            "parameters": {"query": "Mosaic", "limit": "5"}
        })}], [tool])
        self.assertEqual("search_knowledge", calls[0]["name"])
        self.assertEqual(5, calls[0]["input"]["limit"])


class McpAgentLoopTest(unittest.IsolatedAsyncioTestCase):
    async def test_executes_tool_and_returns_final_answer(self):
        mcp = FakeMcpClient()
        bedrock = FakeBedrockClient()
        agent = BedrockMcpAgent(mcp, bedrock, model_id="test-model")

        answer = await agent.answer("How do I get Mosaic access?", verbose=False)

        self.assertEqual("Use ServiceNow [page-01].", answer)
        self.assertEqual(
            [("search_knowledge", {"query": "Mosaic access", "limit": 5})], mcp.calls
        )
        tool_result = bedrock.requests[1]["messages"][-1]["content"][0]["toolResult"]
        self.assertEqual("call-1", tool_result["toolUseId"])
        self.assertEqual("success", tool_result["status"])

    async def test_duplicate_tool_call_is_not_executed_twice(self):
        mcp = FakeMcpClient()
        agent = BedrockMcpAgent(mcp, RepeatingBedrockClient(), model_id="test-model")
        answer = await agent.answer("Mosaic access", verbose=False)
        self.assertEqual("Finished after duplicate guard.", answer)
        self.assertEqual(1, len(mcp.calls))

    async def test_reusable_runner_starts_and_closes_mcp_once(self):
        mcp = ManagedFakeMcpClient()
        bedrock_clients = []

        def bedrock_factory(region):
            client = FakeBedrockClient()
            bedrock_clients.append(client)
            return client

        runner = ReusableMcpAgentRunner(
            region="us-east-2",
            model_id="test-model",
            mcp_client_factory=lambda: mcp,
            bedrock_client_factory=bedrock_factory,
        )
        await runner.start()
        first = await runner("Mosaic access")
        # Use a fresh deterministic fake response sequence without restarting MCP.
        runner._bedrock_client = FakeBedrockClient()
        second = await runner("Mosaic access again")
        await runner.close()

        self.assertEqual(1, mcp.enter_count)
        self.assertEqual(1, mcp.exit_count)
        self.assertEqual(1, len(bedrock_clients))
        self.assertEqual("answered", first["status"])
        self.assertEqual("answered", second["status"])
        self.assertIn("model", first["timings_ms"])
        self.assertIn("tools", first["timings_ms"])


if __name__ == "__main__":
    unittest.main()
