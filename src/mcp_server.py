#!/usr/bin/env python3
"""
MCP Server for Bedrock UI
CPU使用率とAWS情報を提供するMCPサーバー
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
import psutil
import boto3
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server implementation"""
    
    def __init__(self):
        """Initialize MCP Server"""
        self.tools = {
            "get_cpu_usage": self.get_cpu_usage,
            "get_memory_usage": self.get_memory_usage,
            "get_disk_usage": self.get_disk_usage,
            "get_ec2_instances": self.get_ec2_instances,
            "get_s3_buckets": self.get_s3_buckets,
            "get_rds_instances": self.get_rds_instances,
        }
        
        # AWS クライアント（IAMロールから認証情報を取得）
        try:
            self.ec2_client = boto3.client('ec2')
            self.s3_client = boto3.client('s3')
            self.rds_client = boto3.client('rds')
            logger.info("AWS clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            self.ec2_client = None
            self.s3_client = None
            self.rds_client = None
    
    async def get_cpu_usage(self) -> Dict[str, Any]:
        """CPU使用率を取得"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                "success": True,
                "data": {
                    "usage_percent": cpu_percent,
                    "cpu_count": cpu_count,
                    "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用率を取得"""
        try:
            memory = psutil.virtual_memory()
            
            return {
                "success": True,
                "data": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_disk_usage(self) -> Dict[str, Any]:
        """ディスク使用率を取得"""
        try:
            disk = psutil.disk_usage('/')
            
            return {
                "success": True,
                "data": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": disk.percent,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_ec2_instances(self) -> Dict[str, Any]:
        """EC2インスタンス一覧を取得"""
        if not self.ec2_client:
            return {"success": False, "error": "EC2 client not initialized"}
        
        try:
            response = self.ec2_client.describe_instances()
            
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
                "success": True,
                "data": {
                    "instances": instances,
                    "count": len(instances),
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting EC2 instances: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_s3_buckets(self) -> Dict[str, Any]:
        """S3バケット一覧を取得"""
        if not self.s3_client:
            return {"success": False, "error": "S3 client not initialized"}
        
        try:
            response = self.s3_client.list_buckets()
            
            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    "name": bucket['Name'],
                    "creation_date": bucket['CreationDate'].isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "buckets": buckets,
                    "count": len(buckets),
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting S3 buckets: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_rds_instances(self) -> Dict[str, Any]:
        """RDSインスタンス一覧を取得"""
        if not self.rds_client:
            return {"success": False, "error": "RDS client not initialized"}
        
        try:
            response = self.rds_client.describe_db_instances()
            
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
                "success": True,
                "data": {
                    "instances": instances,
                    "count": len(instances),
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting RDS instances: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """ツールを実行"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            tool_func = self.tools[tool_name]
            result = await tool_func()
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """利用可能なツール一覧を取得"""
        return [
            {
                "name": "get_cpu_usage",
                "description": "CPU使用率を取得",
                "parameters": {}
            },
            {
                "name": "get_memory_usage",
                "description": "メモリ使用率を取得",
                "parameters": {}
            },
            {
                "name": "get_disk_usage",
                "description": "ディスク使用率を取得",
                "parameters": {}
            },
            {
                "name": "get_ec2_instances",
                "description": "EC2インスタンス一覧を取得",
                "parameters": {}
            },
            {
                "name": "get_s3_buckets",
                "description": "S3バケット一覧を取得",
                "parameters": {}
            },
            {
                "name": "get_rds_instances",
                "description": "RDSインスタンス一覧を取得",
                "parameters": {}
            }
        ]


async def main():
    """メイン関数（テスト用）"""
    server = MCPServer()
    
    # ツール一覧を表示
    print("Available tools:")
    for tool in server.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n" + "="*50 + "\n")
    
    # 各ツールをテスト
    for tool_name in server.tools.keys():
        print(f"Testing {tool_name}...")
        result = await server.execute_tool(tool_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
