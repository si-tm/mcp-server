#!/usr/bin/env python3
"""
MCP Server for Bedrock/ALB/ECS
HTTP モード（FastAPI Wrapper + Healthcheck）
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# 共通ツールをインポート
from tools import mcp

app = FastAPI(
    title="MCP Server - HTTP Mode",
    description="FastMCP tools exposed via HTTP for ALB/ECS",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# 基本エンドポイント
# ========================================

@app.get("/")
async def root():
    return {
        "message": "MCP Server - HTTP Mode",
        "version": "1.0.0",
        "transport": "HTTP (FastAPI)",
        "region": os.getenv('AWS_REGION', 'ap-northeast-1'),
        "tools_count": len(mcp._tools),
        "endpoints": {
            "/health": "Health check",
            "/tools": "List all tools",
            "/call/{tool_name}": "Call a specific tool",
            "/cpu": "CPU usage",
            "/memory": "Memory usage",
            "/disk": "Disk usage",
            "/system": "System summary",
            "/aws/ec2": "EC2 instances",
            "/aws/s3": "S3 buckets",
            "/aws/rds": "RDS instances",
            "/aws/summary": "AWS summary"
        }
    }


@app.get("/health")
async def health():
    """ヘルスチェック - ALB用"""
    return {
        "status": "healthy",
        "service": "mcp-server-http"
    }


# ========================================
# ツール管理エンドポイント
# ========================================

@app.get("/tools")
async def list_tools():
    """利用可能なツール一覧を取得"""
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
    if tool_name not in mcp._tools:
        return JSONResponse(
            status_code=404,
            content={"error": f"Tool '{tool_name}' not found"}
        )
    
    try:
        tool_func = mcp._tools[tool_name]
        result = tool_func()
        return {"result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ========================================
# システム情報エンドポイント（ショートカット）
# ========================================

@app.get("/cpu")
async def get_cpu():
    """CPU使用率を取得"""
    return await call_tool("get_cpu_usage")


@app.get("/memory")
async def get_memory():
    """メモリ使用率を取得"""
    return await call_tool("get_memory_usage")


@app.get("/disk")
async def get_disk():
    """ディスク使用率を取得"""
    return await call_tool("get_disk_usage")


@app.get("/system")
async def get_system():
    """システムサマリーを取得"""
    return await call_tool("get_system_summary")


# ========================================
# AWS情報エンドポイント（ショートカット）
# ========================================

@app.get("/aws/ec2")
async def get_ec2():
    """EC2インスタンス一覧を取得"""
    return await call_tool("get_ec2_instances")


@app.get("/aws/s3")
async def get_s3():
    """S3バケット一覧を取得"""
    return await call_tool("get_s3_buckets")


@app.get("/aws/rds")
async def get_rds():
    """RDSインスタンス一覧を取得"""
    return await call_tool("get_rds_instances")


@app.get("/aws/summary")
async def get_aws():
    """AWSリソースサマリーを取得"""
    return await call_tool("get_aws_summary")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("FastMCP Server - HTTP Mode (ALB/ECS)")
    print("=" * 60)
    print("Transport: HTTP (FastAPI)")
    print(f"Host: 0.0.0.0")
    print(f"Port: 9000")
    print(f"AWS Region: {os.getenv('AWS_REGION', 'ap-northeast-1')}")
    print(f"Tools: {len(mcp._tools)}")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
