# mcp-server

FastMCPを使用したシステムモニタリング＆AWS情報取得サーバー

## アーキテクチャ

```
共通ツールロジック（tools.py）
         ↓
    ┌────┴────┐
    │         │
stdio モード  HTTPモード
    │         │
Claude Desktop  ALB/ECS
```

### 役割分担

| 用途 | ファイル | トランスポート | 特徴 |
|------|---------|-------------|------|
| **Claude Desktop** | `server_stdio.py` | stdio | ローカル実行・ALB不要 |
| **Bedrock/ALB/ECS** | `server_http.py` | HTTP | healthcheck対応 |
| **ツールロジック** | `tools.py` | - | 共通・再利用 |

## ファイル構成

```
mcp-server/
├── src/
│   ├── tools.py          # ツールロジック（共通）
│   ├── server_stdio.py   # Claude Desktop用
│   └── server_http.py    # Bedrock/ALB/ECS用
├── Dockerfile
├── requirements.txt
└── README.md
```

## 機能

### システム情報ツール
- `get_cpu_usage` - CPU使用率
- `get_memory_usage` - メモリ使用率
- `get_disk_usage` - ディスク使用率
- `get_system_summary` - システムサマリー

### AWS情報ツール
- `get_ec2_instances` - EC2インスタンス一覧
- `get_s3_buckets` - S3バケット一覧
- `get_rds_instances` - RDSインスタンス一覧
- `get_aws_summary` - AWSサマリー

### プロンプト
- `system_status_prompt` - システムステータス確認用
- `aws_inventory_prompt` - AWSリソースインベントリ確認用

## 使い方

### 1. Claude Desktop用（stdio）

#### 設定ファイルに追加

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "system-monitor": {
      "command": "python",
      "args": [
        "/Users/hyakuzukamaya/Desktop/mcp-server/src/server_stdio.py"
      ],
      "env": {
        "AWS_REGION": "ap-northeast-1"
      }
    }
  }
}
```

#### 起動確認

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src
python server_stdio.py
```

Claude Desktopを再起動して、「CPU使用率を教えて」と質問すると、ツールを使って情報を取得します。

### 2. Bedrock/ALB/ECS用（HTTP）

#### Docker環境

```bash
# イメージをビルド
docker build -t mcp-server .

# 起動
docker run -p 9000:9000 -e AWS_REGION=ap-northeast-1 mcp-server
```

#### bedrock-uiと統合

```bash
cd /Users/hyakuzukamaya/Desktop/bedrock-ui

# docker-compose.ymlに既に設定済み
docker-compose up -d mcp-server

# ログを確認
docker-compose logs -f mcp-server
```

## APIエンドポイント（HTTPモード）

### 基本情報
```bash
# サーバー情報
GET /

# ヘルスチェック（ALB用）
GET /health

# ツール一覧
GET /tools
```

### システム情報
```bash
# CPU使用率
GET /cpu

# メモリ使用率
GET /memory

# ディスク使用率
GET /disk

# システムサマリー
GET /system
```

### AWS情報
```bash
# EC2インスタンス
GET /aws/ec2

# S3バケット
GET /aws/s3

# RDSインスタンス
GET /aws/rds

# AWSサマリー
GET /aws/summary
```

### 汎用ツール実行
```bash
# 任意のツールを実行
GET /call/{tool_name}

# 例
GET /call/get_cpu_usage
```

## テスト

### ローカルテスト

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src

# stdioモードテスト（Claude Desktop用）
python server_stdio.py

# HTTPモードテスト（ALB/ECS用）
python server_http.py
```

別のターミナルで：
```bash
# ヘルスチェック
curl http://localhost:9000/health

# CPU使用率
curl http://localhost:9000/cpu

# ツール一覧
curl http://localhost:9000/tools
```

### MCP Inspector（GUIテスト）

```bash
# Claude Desktop用サーバーをテスト
npx @modelcontextprotocol/inspector python /Users/hyakuzukamaya/Desktop/mcp-server/src/server_stdio.py
```

## 必要なIAM権限

AWS情報を取得するには、以下の権限が必要：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "s3:ListAllMyBuckets",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

## デプロイ

### EC2へのデプロイ

```bash
# IAMロールをアタッチ
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=mcp-server-profile

# Docker Composeで起動
cd /path/to/bedrock-ui
docker-compose up -d mcp-server
```

### ECSへのデプロイ

```bash
# ECRにプッシュ
docker build -t mcp-server .
docker tag mcp-server:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/mcp-server:latest
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/mcp-server:latest

# タスク定義にtaskRoleArnを設定
# ECSサービスを起動
```

## トラブルシューティング

### AWS認証エラー

**ローカル開発:**
```bash
aws configure
export AWS_REGION=ap-northeast-1
```

**EC2/ECS:**
```bash
# IAMロールを確認
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### ツールが見つからない

```bash
# Python パスを確認
export PYTHONPATH=/Users/hyakuzukamaya/Desktop/mcp-server/src:$PYTHONPATH

# tools.pyがインポートできるか確認
python -c "from tools import mcp; print(len(mcp._tools))"
```

## まとめ

### 特徴

✅ **ツールロジックは1か所** - `tools.py`に集約  
✅ **起動方式だけ分ける** - stdio / HTTP  
✅ **Claude Desktop対応** - `server_stdio.py`  
✅ **ALB/ECS対応** - `server_http.py` + healthcheck  
✅ **共通・再利用** - 同じツールを両方で使用

### 使い分け

| 環境 | 使用ファイル | 用途 |
|------|------------|------|
| **ローカル（Claude Desktop）** | `server_stdio.py` | 開発・テスト |
| **本番（ALB/ECS）** | `server_http.py` | システム監視 |

これで、ツールロジックを重複なく管理できます！🎉
