# mcp-server

**FastMCP (Model Context Protocol)** を使用したシステムモニタリング＆AWS情報取得サーバー

## 特徴

- ✅ **MCP標準準拠** - Anthropicの公式Model Context Protocolに準拠
- ✅ **FastMCP使用** - 簡潔で読みやすいコード
- ✅ **SSEサポート** - Server-Sent Eventsによるリアルタイム通信
- ✅ **IAMロール対応** - EC2/ECS環境で自動的にAWS認証

## 機能

### システム情報ツール
- `get_cpu_usage` - CPU使用率
- `get_memory_usage` - メモリ使用率
- `get_disk_usage` - ディスク使用率
- `get_system_summary` - システム全体のサマリー

### AWS情報ツール
- `get_ec2_instances` - EC2インスタンス一覧
- `get_s3_buckets` - S3バケット一覧
- `get_rds_instances` - RDSインスタンス一覧
- `get_aws_summary` - AWS リソース全体のサマリー

### プロンプト
- `system_status_prompt` - システムステータス確認用
- `aws_inventory_prompt` - AWSリソースインベントリ作成用

## セットアップ

### ローカル開発環境

```bash
# 依存関係をインストール
pip install -r requirements.txt

# サーバーを起動
cd src
python server_fastmcp.py
```

サーバーは `http://localhost:9000` で起動します。

### Docker環境

```bash
# イメージをビルド
docker build -t mcp-server .

# コンテナを起動
docker run -p 9000:9000 mcp-server
```

### bedrock-uiと統合

```bash
cd /Users/hyakuzukamaya/Desktop/bedrock-ui

# 全サービスを起動
docker-compose up -d

# MCPサーバーのログを確認
docker-compose logs -f mcp-server
```

## FastMCPの利点

### 1. シンプルなツール定義

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def get_cpu_usage() -> dict:
    """CPU使用率を取得"""
    return {"usage": 50.5}
```

### 2. 自動的な型検証

関数の型ヒントから自動的にスキーマを生成

### 3. プロンプトサポート

```python
@mcp.prompt()
def system_check() -> str:
    """システムチェック用のプロンプト"""
    return "システムの状態を確認してください"
```

### 4. 複数のトランスポート対応

- **SSE (Server-Sent Events)** - HTTP経由
- **stdio** - 標準入出力経由

## MCPエンドポイント

### ポート: 9000

FastMCPは標準的なMCPプロトコルを使用します：

#### SSE エンドポイント
```
GET /sse
```

#### ツール一覧取得
MCPクライアント経由で以下が可能：
- ツール一覧の取得
- ツールの実行
- プロンプトの取得

## Claude Desktop との統合

Claude Desktopの設定ファイルに追加：

### macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
### Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "system-monitor": {
      "command": "python",
      "args": [
        "/Users/hyakuzukamaya/Desktop/mcp-server/src/server_fastmcp.py"
      ],
      "env": {
        "AWS_REGION": "ap-northeast-1"
      }
    }
  }
}
```

これで、Claude Desktopから直接システム情報やAWS情報を取得できます！

## 使用例

### ツール実行

MCPクライアント（Claude Desktopなど）から：

```
User: CPU使用率を教えて

Claude: get_cpu_usage ツールを使用します...
→ CPU使用率: 45.2%
→ CPUコア数: 8
→ 周波数: 2400 MHz
```

### プロンプト使用

```
User: システムの状態を確認して

Claude: system_status_prompt を使用して確認します...
→ CPU使用率: 45.2% - 正常
→ メモリ使用率: 60.5% - 正常
→ ディスク使用率: 75.3% - 注意が必要
```

### AWS情報取得

```
User: EC2インスタンスを教えて

Claude: get_ec2_instances ツールを使用します...
→ 稼働中: 2インスタンス
  - i-1234567890 (t3.medium) - 10.0.1.10
  - i-0987654321 (t3.large) - 10.0.1.20
```

## bedrock-ui フロントエンドからの利用

### MCPクライアントライブラリを使用

```bash
npm install @modelcontextprotocol/sdk
```

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';

// MCPクライアントを作成
const transport = new SSEClientTransport(
  new URL('http://localhost:9000/sse')
);
const client = new Client({
  name: 'bedrock-ui',
  version: '1.0.0'
}, {
  capabilities: {}
});

await client.connect(transport);

// ツール一覧を取得
const tools = await client.listTools();
console.log('Available tools:', tools);

// ツールを実行
const result = await client.callTool({
  name: 'get_cpu_usage',
  arguments: {}
});
console.log('CPU Usage:', result);
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

## トラブルシューティング

### MCPサーバーが起動しない

```bash
# 依存関係を再インストール
pip install -r requirements.txt --upgrade

# ログを確認
docker-compose logs mcp-server
```

### AWS認証エラー

**ローカル開発:**
```bash
aws configure
```

**EC2/ECS:**
- IAMロールに必要な権限があるか確認

### ポート9000が使用中

```bash
# ポートを変更
python server_fastmcp.py --port 9001
```

## FastMCP vs 通常のHTTP API

| 機能 | FastMCP | HTTP API |
|------|---------|----------|
| MCP標準準拠 | ✅ | ❌ |
| Claude統合 | ✅ 簡単 | ❌ 困難 |
| 型安全性 | ✅ | △ |
| プロンプトサポート | ✅ | ❌ |
| コードの簡潔さ | ✅ | △ |
| SSEサポート | ✅ | 要実装 |

## 参考リンク

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Anthropic MCP Documentation](https://docs.anthropic.com/claude/docs/model-context-protocol)

## ライセンス

MIT
