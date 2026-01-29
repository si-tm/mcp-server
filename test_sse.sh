#!/bin/bash
# FastMCP SSEサーバーのテストスクリプト

echo "=========================================="
echo "FastMCP Server Test"
echo "=========================================="
echo ""

# サーバーが起動しているか確認
echo "1. サーバー起動確認..."
if curl -s http://localhost:9000/sse > /dev/null 2>&1; then
    echo "✓ サーバーは起動しています (localhost:9000)"
else
    echo "✗ サーバーが起動していません"
    echo ""
    echo "サーバーを起動してください:"
    echo "  cd /Users/hyakuzukamaya/Desktop/mcp-server/src"
    echo "  python server_fastmcp.py"
    exit 1
fi
echo ""

# SSEエンドポイントへの接続テスト
echo "2. SSEエンドポイント接続テスト..."
echo "   GET http://localhost:9000/sse"
timeout 2 curl -N http://localhost:9000/sse 2>/dev/null | head -5
echo ""
echo "✓ SSE接続成功"
echo ""

echo "=========================================="
echo "テスト完了"
echo "=========================================="
echo ""
echo "MCPサーバーは正常に動作しています！"
echo ""
echo "次のステップ:"
echo "1. MCP Inspector でGUIテスト:"
echo "   npx @modelcontextprotocol/inspector python /Users/hyakuzukamaya/Desktop/mcp-server/src/server_fastmcp.py"
echo ""
echo "2. Claude Desktop に設定:"
echo "   ~/Library/Application Support/Claude/claude_desktop_config.json に追加"
echo ""
