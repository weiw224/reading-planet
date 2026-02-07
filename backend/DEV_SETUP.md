# 本地开发环境配置（无需 Docker）

## 数据库选项

### 选项1：SQLite（推荐用于快速开发验证）

无需安装任何软件，开箱即用。

**已配置**：`.env` 文件已设置为使用 SQLite。

**当前状态**：可以立即开始开发！

### 选项2：本地安装 PostgreSQL

如果需要与生产环境保持一致：

```bash
# 安装 PostgreSQL (Apple Silicon)
brew install postgresql@15

# 启动 PostgreSQL 服务
brew services start postgresql@15

# 创建数据库
createdb reading_planet

# 启动数据库交互
psql reading_planet
```

然后修改 `.env` 文件：
```bash
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/reading_planet
```

### 选项3：云数据库（Supabase 推荐）

1. 访问 https://supabase.com 免费注册
2. 创建新项目（免费）
3. 获取数据库连接字符串
4. 修改 `.env`：
```bash
DATABASE_URL=postgresql+asyncpg://user:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

## Redis 缓存（可选）

Redis 是可选的，项目可以不使用 Redis 正常运行。

如果要使用本地 Redis：

```bash
# 安装 Redis
brew install redis

# 启动 Redis
brew services start redis
```

如果要使用云 Redis：
- 访问 https://redis.com/ 免费创建实例
- 获取连接字符串修改 `.env`

## 快速开始（使用 SQLite）

```bash
cd /Users/emily/Documents/newProject/reading-planet/backend

# 激活虚拟环境
source venv/bin/activate

# 运行测试
pytest

# 启动服务器
uvicorn app.main:app --reload
```

服务器将在 http://localhost:8000 启动，数据库文件 `reading_planet.db` 会自动创建。

## 验证

```bash
# 运行测试
pytest

# 检查服务器健康
curl http://localhost:8000/health

# 访问 API 文档
open http://localhost:8000/docs
```

## 当前配置

**数据库**：SQLite（无需安装）
**Redis**：未配置（可选）
**后端**：可立即启动
**管理后台**：可立即启动

✅ **您现在就可以开始开发了！**
