# Reading Planet Backend

后端服务，基于 FastAPI + PostgreSQL + Redis 构建。

## 环境要求

- Python 3.9+
- PostgreSQL 15+
- Redis 7+ (可选)

## 快速开始

### 1. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要配置
```

### 3. 启动数据库

```bash
# 使用 Docker Compose
docker-compose up -d

# 或者使用本地数据库
# 确保 PostgreSQL 正在运行并创建数据库 reading_planet
```

### 4. 运行应用

```bash
uvicorn app.main:app --reload
```

应用将在 http://localhost:8000 启动。

## 开发

### 运行测试

```bash
pytest
```

### 代码检查

```bash
black .
isort .
flake8 .
mypy .
```

### 数据库迁移

```bash
alembic upgrade head
```

## API 文档

启动应用后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 健康检查

```bash
curl http://localhost:8000/health
```
