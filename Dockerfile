# 统一 Dockerfile - 通过 TARGET 参数选择构建目标
# 使用方式:
#   docker build --build-arg TARGET=backend -t dear-backend .
#   docker build --build-arg TARGET=frontend -t dear-frontend .

ARG TARGET=backend

# ==================== 后端构建 ====================
FROM python:3.10-slim AS backend
WORKDIR /app

# 安装 ffmpeg 和 curl
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY pyproject.toml uv.lock ./
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv sync --frozen --no-dev

# 复制代码
COPY app ./app
RUN mkdir -p /app/outputs/images /app/outputs/videos /app/outputs/audio /app/outputs/composed /app/outputs/final /app/temp

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/v1/health || exit 1

CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8001"]


# ==================== 前端构建 ====================
FROM node:18-alpine AS builder
WORKDIR /app
COPY web/package*.json ./
RUN npm ci --only=production
COPY web ./
RUN npm run build

FROM nginx:alpine AS frontend
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]


# ==================== 默认目标 ====================
FROM backend AS final
