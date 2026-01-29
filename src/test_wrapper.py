#!/usr/bin/env python3
"""
FastMCP Server - HTTP Wrapper for Testing
標準入出力モードのFastMCPをHTTPでテストするためのラッパー
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import json
import os

app = FastAPI(title="MCP Server Test Wrapper")

# MCP Serverのパス
MCP_SERVER_PATH = "/app/server_fastmcp.py"

@app.get("/")
async def root():
    return {
        "message": "MCP Server Test Wrapper",
        "note": "This server provides HTTP endpoints to test the MCP server",
        "endpoints": {
            "/tools": "List available tools",
            "/call/{tool_name}": "Call a specific tool",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mcp-test-wrapper"}

@app.get("/tools")
async def list_tools():
    """利用可能なツール一覧を取得"""
    # server_fastmcp.pyから直接import
    import sys
    sys.path.insert(0, '/app')
    from server_fastmcp import mcp
    
    # FastMCPのツールを取得
    tools = []
    for name, tool in mcp._tools.items():
        tools.append({
            "name": name,
            "description": tool.__doc__ or "No description"
        })
    
    return {"tools": tools, "count": len(tools)}

@app.get("/call/{tool_name}")
async def call_tool(tool_name: str):
    """ツールを実行"""
    import sys
    sys.path.insert(0, '/app')
    from server_fastmcp import mcp
    
    if tool_name not in mcp._tools:
        return JSONResponse(
            status_code=404,
            content={"error": f"Tool '{tool_name}' not found"}
        )
    
    try:
        # ツールを実行
        tool_func = mcp._tools[tool_name]
        result = tool_func()
        return {"result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 個別のエンドポイント
@app.get("/cpu")
async def get_cpu():
    return await call_tool("get_cpu_usage")

@app.get("/memory")
async def get_memory():
    return await call_tool("get_memory_usage")

@app.get("/disk")
async def get_disk():
    return await call_tool("get_disk_usage")

@app.get("/system")
async def get_system():
    return await call_tool("get_system_summary")

@app.get("/aws/ec2")
async def get_ec2():
    return await call_tool("get_ec2_instances")

@app.get("/aws/s3")
async def get_s3():
    return await call_tool("get_s3_buckets")

@app.get("/aws/rds")
async def get_rds():
    return await call_tool("get_rds_instances")

@app.get("/aws/summary")
async def get_aws():
    return await call_tool("get_aws_summary")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("MCP Server Test Wrapper Starting...")
    print("=" * 60)
    print("This is a test wrapper for the FastMCP server")
    print("For Claude Desktop, use server_fastmcp.py directly")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET /tools - List all tools")
    print("  GET /cpu - Get CPU usage")
    print("  GET /memory - Get memory usage")
    print("  GET /disk - Get disk usage")
    print("  GET /system - Get system summary")
    print("  GET /aws/ec2 - Get EC2 instances")
    print("  GET /aws/s3 - Get S3 buckets")
    print("  GET /aws/rds - Get RDS instances")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=9000)
