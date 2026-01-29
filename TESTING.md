# FastMCP Server テストガイド

Claude Desktopに接続する前に、MCPサーバーが正しく動作することを確認します。

## テスト方法一覧

1. **直接実行テスト** - 各ツールを個別にテスト（最も簡単）
2. **SSE接続テスト** - サーバーが起動しているか確認
3. **MCP Inspector** - GUIでツールをテスト（推奨）
4. **MCPクライアント** - プログラムでサーバーをテスト

---

## 方法1: 直接実行テスト（最も簡単）

### ステップ1: テストスクリプトを実行

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src
python test_server.py
```

### 期待される出力

```
============================================================
FastMCP Server Test
============================================================

Available tools: 8

============================================================
1. CPU使用率テスト
============================================================
✓ CPU使用率: 45.2%
✓ CPUコア数: 8
✓ CPU周波数: 2400.0 MHz
✓ タイムスタンプ: 2024-01-29T12:00:00

============================================================
2. メモリ使用率テスト
============================================================
✓ メモリ使用率: 60.5%
✓ 総メモリ: 16.0 GB
✓ 使用中: 9.68 GB
✓ 利用可能: 6.32 GB

...
```

### トラブルシューティング

**エラー: `ModuleNotFoundError: No module named 'mcp'`**
```bash
pip install -r /Users/hyakuzukamaya/Desktop/mcp-server/requirements.txt
```

**AWS認証エラー**
```bash
# ローカル開発の場合
aws configure

# 表示される: ⚠ AWS認証なし: Unable to locate credentials
# → 正常（AWS情報は取得できないが、システム情報は取得可能）
```

---

## 方法2: SSE接続テスト

### ステップ1: サーバーを起動

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src
python server_fastmcp.py
```

**期待される出力:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
```

### ステップ2: 別のターミナルでテスト

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server
bash test_sse.sh
```

または手動で：

```bash
# サーバーが起動しているか確認
curl http://localhost:9000/sse
```

---

## 方法3: MCP Inspector（推奨・GUIあり）

### ステップ1: MCP Inspectorをインストール

```bash
npm install -g @modelcontextprotocol/inspector
```

### ステップ2: MCP Inspectorを起動

```bash
npx @modelcontextprotocol/inspector python /Users/hyakuzukamaya/Desktop/mcp-server/src/server_fastmcp.py
```

### ステップ3: ブラウザでテスト

1. ブラウザが自動的に開く（通常 http://localhost:5173）
2. 左側のパネルで利用可能なツールが表示される
3. ツールをクリックして実行
4. 右側のパネルで結果を確認

### MCP Inspectorの画面

```
┌─────────────────────────────────────────────────────┐
│ MCP Inspector                                       │
├──────────────┬──────────────────────────────────────┤
│ Tools        │ Test Tool: get_cpu_usage             │
│              │                                      │
│ ○ get_cpu_   │ Arguments: {}                       │
│   usage      │                                      │
│              │ [Execute]                           │
│ ○ get_memory │                                      │
│   _usage     │ Result:                             │
│              │ {                                    │
│ ○ get_disk_  │   "usage_percent": 45.2,            │
│   usage      │   "cpu_count": 8,                   │
│              │   ...                               │
│ ○ get_system │ }                                    │
│   _summary   │                                      │
│              │                                      │
│ ○ get_ec2_   │                                      │
│   instances  │                                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

---

## 方法4: MCPクライアントでテスト

### ステップ1: テストスクリプトを実行

```bash
cd /Users/hyakuzukamaya/Desktop/mcp-server/src
python test_mcp_client.py
```

### 期待される出力

```
============================================================
MCP Client Test
============================================================

1. MCPサーバーに接続中...
✓ 接続成功

2. サーバーを初期化中...
✓ 初期化完了

3. 利用可能なツールを取得中...
✓ 8 個のツールが利用可能:
  - get_cpu_usage: CPU使用率を取得
  - get_memory_usage: メモリ使用率を取得
  ...

4. get_cpu_usage ツールを実行...
✓ 結果:
{
  "usage_percent": 45.2,
  "cpu_count": 8,
  ...
}
```

---

## Dockerでテスト

### ステップ1: bedrock-uiから起動

```bash
cd /Users/hyakuzukamaya/Desktop/bedrock-ui

# MCPサーバーを含む全サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs mcp-server
```

### ステップ2: テスト

```bash
# コンテナ内でテストスクリプトを実行
docker-compose exec mcp-server python test_server.py

# または、ホストからSSE接続テスト
curl http://localhost:9000/sse
```

---

## チェックリスト

テストが成功したら、以下を確認：

- [ ] `test_server.py` がエラーなく完了
- [ ] システム情報（CPU、メモリ、ディスク）が取得できる
- [ ] SSEエンドポイント（http://localhost:9000/sse）に接続できる
- [ ] MCP Inspectorでツールが表示され、実行できる
- [ ] AWS情報は認証があれば取得できる（なくてもOK）

すべてチェックできたら、Claude Desktopへの設定に進めます！

---

## トラブルシューティング

### ポート9000が使用中

```bash
# ポートを使用しているプロセスを確認
lsof -i :9000

# プロセスを停止
kill -9 <PID>

# または、別のポートを使用
# server_fastmcp.py の最後の行を変更:
# mcp.run(transport="sse", port=9001, host="0.0.0.0")
```

### 依存関係のエラー

```bash
# すべての依存関係を再インストール
pip install -r /Users/hyakuzukamaya/Desktop/mcp-server/requirements.txt --upgrade
```

### FastMCPが見つからない

```bash
# FastMCPを直接インストール
pip install mcp==0.9.0 --upgrade
```

### AWS認証エラー（オプション）

システム情報のテストには影響しません。AWS情報が必要な場合のみ：

```bash
# AWS認証情報を設定
aws configure

# 認証情報を確認
aws sts get-caller-identity
```

---

## 次のステップ

すべてのテストが成功したら：

1. **Claude Desktopに設定** - `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Claude Desktopを再起動**
3. **Claudeに「CPU使用率を教えて」と質問**

テストが成功していれば、Claudeがツールを使って情報を取得できます！
