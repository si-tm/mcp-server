#!/usr/bin/env python3
"""
FastMCPサーバーのテストスクリプト
各ツールを実行して結果を確認
"""

import asyncio
import sys
import os

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from server_fastmcp import mcp


async def test_all_tools():
    """すべてのツールをテスト"""
    
    print("=" * 60)
    print("FastMCP Server Test")
    print("=" * 60)
    print()
    
    # 利用可能なツールを取得
    tools = [name for name in dir(mcp) if not name.startswith('_')]
    print(f"Available tools: {len(tools)}")
    print()
    
    # システム情報ツールのテスト
    print("=" * 60)
    print("1. CPU使用率テスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_cpu_usage
        result = get_cpu_usage()
        print(f"✓ CPU使用率: {result['usage_percent']}%")
        print(f"✓ CPUコア数: {result['cpu_count']}")
        print(f"✓ CPU周波数: {result['cpu_freq_mhz']} MHz")
        print(f"✓ タイムスタンプ: {result['timestamp']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("2. メモリ使用率テスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_memory_usage
        result = get_memory_usage()
        print(f"✓ メモリ使用率: {result['usage_percent']}%")
        print(f"✓ 総メモリ: {result['total_gb']} GB")
        print(f"✓ 使用中: {result['used_gb']} GB")
        print(f"✓ 利用可能: {result['available_gb']} GB")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("3. ディスク使用率テスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_disk_usage
        result = get_disk_usage()
        print(f"✓ ディスク使用率: {result['usage_percent']}%")
        print(f"✓ 総容量: {result['total_gb']} GB")
        print(f"✓ 使用中: {result['used_gb']} GB")
        print(f"✓ 空き容量: {result['free_gb']} GB")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("4. システムサマリーテスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_system_summary
        result = get_system_summary()
        print(f"✓ CPU: {result['cpu']['usage_percent']}%")
        print(f"✓ メモリ: {result['memory']['usage_percent']}%")
        print(f"✓ ディスク: {result['disk']['usage_percent']}%")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    # AWS情報ツールのテスト
    print("=" * 60)
    print("5. EC2インスタンステスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_ec2_instances
        result = get_ec2_instances()
        if 'error' in result:
            print(f"⚠ AWS認証なし: {result['error']}")
        else:
            print(f"✓ インスタンス数: {result['count']}")
            for instance in result.get('instances', [])[:3]:  # 最初の3つのみ表示
                print(f"  - {instance['instance_id']} ({instance['instance_type']}) - {instance['state']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("6. S3バケットテスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_s3_buckets
        result = get_s3_buckets()
        if 'error' in result:
            print(f"⚠ AWS認証なし: {result['error']}")
        else:
            print(f"✓ バケット数: {result['count']}")
            for bucket in result.get('buckets', [])[:3]:  # 最初の3つのみ表示
                print(f"  - {bucket['name']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("7. RDSインスタンステスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_rds_instances
        result = get_rds_instances()
        if 'error' in result:
            print(f"⚠ AWS認証なし: {result['error']}")
        else:
            print(f"✓ RDSインスタンス数: {result['count']}")
            for instance in result.get('instances', [])[:3]:  # 最初の3つのみ表示
                print(f"  - {instance['db_instance_id']} ({instance['engine']}) - {instance['status']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("8. AWSサマリーテスト")
    print("=" * 60)
    try:
        from server_fastmcp import get_aws_summary
        result = get_aws_summary()
        ec2_count = result.get('ec2', {}).get('count', 0) if 'error' not in result.get('ec2', {}) else 'N/A'
        s3_count = result.get('s3', {}).get('count', 0) if 'error' not in result.get('s3', {}) else 'N/A'
        rds_count = result.get('rds', {}).get('count', 0) if 'error' not in result.get('rds', {}) else 'N/A'
        
        print(f"✓ EC2インスタンス: {ec2_count}")
        print(f"✓ S3バケット: {s3_count}")
        print(f"✓ RDSインスタンス: {rds_count}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    print()
    
    print("=" * 60)
    print("テスト完了")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("1. サーバーを起動: python server_fastmcp.py")
    print("2. 別のターミナルでテスト: python test_server.py --connect")
    print("3. MCP Inspectorでテスト: mcp-inspector python server_fastmcp.py")
    print("4. Claude Desktopに設定")


if __name__ == "__main__":
    asyncio.run(test_all_tools())
