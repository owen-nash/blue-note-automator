import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_wikipedia():
    print("--- Testing Wikipedia MCP ---")
    params = StdioServerParameters(command="/home/ownash/.local/bin/wikipedia-mcp")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Wikipedia Tools: {[t.name for t in tools.tools]}")

async def test_musicbrainz():
    print("\n--- Testing MusicBrainz MCP ---")
    params = StdioServerParameters(
        command="/home/ownash/.local/bin/uv",
        args=["run", "--directory", "/home/ownash/mcp-musicbrainz", "mcp-musicbrainz"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"MusicBrainz Tools: {[t.name for t in tools.tools]}")

if __name__ == "__main__":
    asyncio.run(test_wikipedia())
    asyncio.run(test_musicbrainz())
