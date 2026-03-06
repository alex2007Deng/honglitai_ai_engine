Dockerfile
FROM python:3.9-slim
LABEL "language"="python"

WORKDIR /usr/src/app

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 健康检查（可选）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping()" || exit 1

EXPOSE 8080

CMD ["python", "gateway.py"]