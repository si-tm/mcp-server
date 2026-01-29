FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# 環境変数のデフォルト値
ENV AWS_REGION=ap-northeast-1

EXPOSE 9000

# HTTPモードで起動（ALB/ECS用）
# Claude Desktop用には server_stdio.py を直接実行
CMD ["python", "server_http.py"]
