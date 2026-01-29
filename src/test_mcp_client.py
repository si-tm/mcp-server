#!/usr/bin/env python3
"""
MCPクライアントを使ってサーバーをテスト
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """MCPサーバーに接続してツールをテスト"""
    
    print("=" * 60)
    print("MCP Client Test")
    print("=" * 60)
    print()
    
    # サーバーパラメータ
    server_params = StdioServerParameters(
        command="python",
        args=["server_fastmcp.py"],
        env=None
    )
    
    print("1. MCPサーバーに接続中...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("✓ 接続成功")
            print()
            
            # 初期化
            print("2. サーバーを初期化中...")
            await session.initialize()
            print("✓ 初期化完了")
            print()
            
            # ツール一覧を取得
            print("3. 利用可能なツールを取得中...")
            tools_response = await session.list_tools()
            tools = tools_response.tools
            
            print(f"✓ {len(tools)} 個のツールが利用可能:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # CPU使用率を取得
            print("4. get_cpu_usage ツールを実行...")
            result = await session.call_tool("get_cpu_usage", arguments={})
            print("✓ 結果:")
            print(json.dumps(result.content[0].text, indent=2, ensure_ascii=False))
            print()
            
            # メモリ使用率を取得
            print("5. get_memory_usage ツールを実行...")
            result = await session.call_tool("get_memory_usage", arguments={})
            print("✓ 結果:")
            print(json.dumps(result.content[0].text, indent=2, ensure_ascii=False))
            print()
            
            # システムサマリーを取得
            print("6. get_system_summary ツールを実行...")
            result = await session.call_tool("get_system_summary", arguments={})
            print("✓ 結果:")
            print(json.dumps(result.content[0].text, indent=2, ensure_ascii=False))
            print()
            
            # プロンプト一覧を取得
            print("7. 利用可能なプロンプトを取得中...")
            prompts_response = await session.list_prompts()
            prompts = prompts_response.prompts
            
            print(f"✓ {len(prompts)} 個のプロンプトが利用可能:")
            for prompt in prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            print()
            
            print("=" * 60)
            print("テスト完了！すべて正常に動作しています")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
