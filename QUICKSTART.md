# MCP Server - クイックスタート

## 構成

```
tools.py (共通ロジック)
    ↓
┌───┴───┐
│       │
stdio   HTTP
│       │
Claude  ALB/ECS
Desktop
```

## テスト

### 1. HTTPモード（ALB/ECS用）

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server

# Dockerでビルド
docker build -t mcp-server .

# 起動
docker run -p 9000:9000 -e AWS_REGION=ap-northeast-1 mcp-server
```

**別のターミナルでテスト:**
```bash
# ヘルスチェック
curl http://localhost:9000/health

# CPU使用率
curl http://localhost:9000/cpu

# ツール一覧
curl http://localhost:9000/tools
```

**期待される出力:**
```json
{
  "status": "healthy",
  "service": "mcp-server-http"
}
```

### 2. stdioモード（Claude Desktop用）

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src
python server_stdio.py
```

**MCP Inspectorでテスト:**
```bash
npx @modelcontextprotocol/inspector python /Users/hyakuzukamaya/Desktop/mcp-server/src/server_stdio.py
```

## Claude Desktopへの設定

### macOS

```bash
# 設定ファイルを開く
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**以下を追加:**
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

**Claude Desktopを再起動**

**テスト:**
Claudeに「CPU使用率を教えて」と質問

## bedrock-uiとの統合

```bash
cd /Users/hyakuzukamaya/Desktop/bedrock-ui

# すでに設定済み
docker-compose up -d mcp-server

# 確認
curl http://localhost:9000/health
```

## トラブルシューティング

### tools.pyがインポートできない

```bash
# Pythonパスを設定
export PYTHONPATH=/Users/hyakuzukamaya/Desktop/mcp-server/src:$PYTHONPATH

# 確認
python -c "from tools import mcp; print('OK')"
```

### AWS認証エラー

```bash
# ローカル
aws configure

# EC2
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

## まとめ

### ファイル

- **tools.py** - ツールロジック（共通）
- **server_stdio.py** - Claude Desktop用
- **server_http.py** - ALB/ECS用

### 起動方法

| 環境 | コマンド |
|------|---------|
| Claude Desktop | `python server_stdio.py` |
| Docker/HTTP | `docker run -p 9000:9000 mcp-server` |

これで完了です！🎉
