#!/usr/bin/env python3
"""
MCP Server for Claude Desktop
stdio モード（標準入出力）
"""

from tools import mcp

if __name__ == "__main__":
    print("=" * 60)
    print("FastMCP Server - Claude Desktop Mode")
    print("=" * 60)
    print("Transport: stdio (standard input/output)")
    print("Usage: Add to Claude Desktop config")
    print("=" * 60)
    
    # stdio モードで起動
    mcp.run()
