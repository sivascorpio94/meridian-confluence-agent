"""Exercise MCP initialization and capability discovery in-process."""

import asyncio

from mcp import Client

from src.mcp_server import mcp


async def inspect_server() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        templates = await client.list_resource_templates()
        print("MCP handshake: OK")
        print("Tools:")
        for tool in tools.tools:
            print(f"- {tool.name}")
        print("Resource templates:")
        for template in templates.resource_templates:
            print(f"- {template.uri_template}")


def main() -> None:
    asyncio.run(inspect_server())


if __name__ == "__main__":
    main()
