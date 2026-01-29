#!/usr/bin/env python3
"""
MCP Server HTTP API
FastAPIを使用してMCPサーバーをHTTPエンドポイントとして公開
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uvicorn
from mcp_server import MCPServer

app = FastAPI(
    title="MCP Server API",
    description="CPU使用率とAWS情報を提供するMCPサーバー",
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

# MCPサーバーインスタンス
mcp_server = MCPServer()


class ToolRequest(BaseModel):
    """ツール実行リクエスト"""
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "MCP Server API is running",
        "version": "1.0.0",
        "endpoints": {
            "tools": "/tools",
            "execute": "/execute",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "mcp-server"
    }


@app.get("/tools")
async def list_tools():
    """利用可能なツール一覧を取得"""
    try:
        tools = mcp_server.list_tools()
        return {
            "success": True,
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """ツールを実行"""
    try:
        result = await mcp_server.execute_tool(
            request.tool_name,
            request.arguments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 個別のエンドポイント（便利なショートカット）
@app.get("/cpu")
async def get_cpu_usage():
    """CPU使用率を取得"""
    return await mcp_server.get_cpu_usage()


@app.get("/memory")
async def get_memory_usage():
    """メモリ使用率を取得"""
    return await mcp_server.get_memory_usage()


@app.get("/disk")
async def get_disk_usage():
    """ディスク使用率を取得"""
    return await mcp_server.get_disk_usage()


@app.get("/aws/ec2")
async def get_ec2_instances():
    """EC2インスタンス一覧を取得"""
    return await mcp_server.get_ec2_instances()


@app.get("/aws/s3")
async def get_s3_buckets():
    """S3バケット一覧を取得"""
    return await mcp_server.get_s3_buckets()


@app.get("/aws/rds")
async def get_rds_instances():
    """RDSインスタンス一覧を取得"""
    return await mcp_server.get_rds_instances()


if __name__ == "__main__":
    # ポート9000で起動
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
