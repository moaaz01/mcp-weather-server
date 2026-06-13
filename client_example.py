#!/usr/bin/env python3
"""Example MCP client that connects to the weather server."""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Connect to the server via stdio
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("✅ Connected to MCP Weather Server\n")
            
            # List available tools
            tools = await session.list_tools()
            print("📦 Available Tools:")
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()
            
            # List resources
            resources = await session.list_resources()
            print("📄 Available Resources:")
            for res in resources.resources:
                print(f"  • {res.uri}: {res.description}")
            print()
            
            # Call a tool
            print("🌤️ Testing get_alerts('CA'):")
            result = await session.call_tool("get_alerts", {"state": "CA"})
            for alert in result.content:
                print(f"  {alert.text[:200]}")
            print()
            
            # Read a resource
            print("📊 Reading weather://CA/current:")
            resource = await session.read_resource("weather://CA/current")
            for content in resource.contents:
                print(content.text[:500])


if __name__ == "__main__":
    asyncio.run(main())
