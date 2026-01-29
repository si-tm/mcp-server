#!/usr/bin/env python3
"""
MCP Server using FastMCP
CPU使用率とAWS情報を提供する標準MCP準拠サーバー
"""

import os
import psutil
import boto3
from datetime import datetime
from typing import Any
from mcp.server.fastmcp import FastMCP

# FastMCPサーバーを初期化
mcp = FastMCP("System & AWS Monitor")

# AWS リージョンを環境変数から取得（デフォルト: ap-northeast-1）
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')

# AWS クライアント（IAMロールから認証情報を取得）
try:
    ec2_client = boto3.client('ec2', region_name=AWS_REGION)
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    rds_client = boto3.client('rds', region_name=AWS_REGION)
    print(f"✓ AWS clients initialized (region: {AWS_REGION})")
except Exception as e:
    print(f"⚠ Warning: Failed to initialize AWS clients: {e}")
    ec2_client = None
    s3_client = None
    rds_client = None


@mcp.tool()
def get_cpu_usage() -> dict[str, Any]:
    """CPU使用率を取得"""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    return {
        "usage_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_memory_usage() -> dict[str, Any]:
    """メモリ使用率を取得"""
    memory = psutil.virtual_memory()
    
    return {
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
        "used_gb": round(memory.used / (1024**3), 2),
        "usage_percent": memory.percent,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_disk_usage() -> dict[str, Any]:
    """ディスク使用率を取得"""
    disk = psutil.disk_usage('/')
    
    return {
        "total_gb": round(disk.total / (1024**3), 2),
        "used_gb": round(disk.used / (1024**3), 2),
        "free_gb": round(disk.free / (1024**3), 2),
        "usage_percent": disk.percent,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_system_summary() -> dict[str, Any]:
    """システム全体のサマリーを取得"""
    return {
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage()
    }


@mcp.tool()
def get_ec2_instances() -> dict[str, Any]:
    """EC2インスタンス一覧を取得"""
    if not ec2_client:
        return {"error": "EC2 client not initialized"}
    
    try:
        response = ec2_client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    "instance_id": instance['InstanceId'],
                    "instance_type": instance['InstanceType'],
                    "state": instance['State']['Name'],
                    "private_ip": instance.get('PrivateIpAddress'),
                    "public_ip": instance.get('PublicIpAddress'),
                    "launch_time": instance['LaunchTime'].isoformat()
                })
        
        return {
            "instances": instances,
            "count": len(instances),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_s3_buckets() -> dict[str, Any]:
    """S3バケット一覧を取得"""
    if not s3_client:
        return {"error": "S3 client not initialized"}
    
    try:
        response = s3_client.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            buckets.append({
                "name": bucket['Name'],
                "creation_date": bucket['CreationDate'].isoformat()
            })
        
        return {
            "buckets": buckets,
            "count": len(buckets),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_rds_instances() -> dict[str, Any]:
    """RDSインスタンス一覧を取得"""
    if not rds_client:
        return {"error": "RDS client not initialized"}
    
    try:
        response = rds_client.describe_db_instances()
        instances = []
        for db_instance in response['DBInstances']:
            instances.append({
                "db_instance_id": db_instance['DBInstanceIdentifier'],
                "db_instance_class": db_instance['DBInstanceClass'],
                "engine": db_instance['Engine'],
                "engine_version": db_instance['EngineVersion'],
                "status": db_instance['DBInstanceStatus'],
                "endpoint": db_instance.get('Endpoint', {}).get('Address'),
                "port": db_instance.get('Endpoint', {}).get('Port')
            })
        
        return {
            "instances": instances,
            "count": len(instances),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_aws_summary() -> dict[str, Any]:
    """AWS リソースのサマリーを取得"""
    return {
        "ec2": get_ec2_instances(),
        "s3": get_s3_buckets(),
        "rds": get_rds_instances()
    }


@mcp.prompt()
def system_status_prompt() -> str:
    """システムステータス確認用プロンプト"""
    return """システムの現在の状態を確認してください。

以下の情報を取得して報告してください：
1. CPU使用率
2. メモリ使用率
3. ディスク使用率
4. 何か問題がある場合は警告してください
"""


@mcp.prompt()
def aws_inventory_prompt() -> str:
    """AWSリソースインベントリ確認用プロンプト"""
    return """AWS環境のリソースインベントリを作成してください。

以下のリソースを確認してください：
1. EC2インスタンス（稼働中/停止中）
2. S3バケット
3. RDSインスタンス

各リソースの数と状態をまとめて報告してください。
"""


if __name__ == "__main__":
    # stdio モードで起動（標準入出力経由）
    # Claude DesktopなどのMCPクライアントから使用
    mcp.run()
