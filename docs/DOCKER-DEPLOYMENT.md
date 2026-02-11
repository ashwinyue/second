# Docker 部署指南

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
nano .env  # 填入 ARK_API_KEY 等必需配置
```

### 2. 启动服务

```bash
docker compose up -d
```

### 3. 访问应用

- 前端: http://localhost:3000
- API 文档: http://localhost:3000/docs

---

## 常用命令

```bash
# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重新构建
docker compose up -d --build
```

---

## 端口配置

修改前端端口（默认 3000）：

```bash
FRONTEND_PORT=8080 docker compose up -d
```

---

## 数据存储

生成的文件保存在 `./outputs` 目录。

---

## 环境变量

| 变量 | 必需 | 默认值 |
|------|------|--------|
| `ARK_API_KEY` | ✅ | - |
| `VOLC_TTS_APPID` | ✅ | - |
| `VOLC_TTS_ACCESS_TOKEN` | ✅ | - |
| `FRONTEND_PORT` | - | 3000 |
