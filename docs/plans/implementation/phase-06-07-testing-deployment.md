# Phase 6-7: 测试、联调与部署

> **预估工时**: 4-5 人天  
> **前置依赖**: Phase 1-5 完成  
> **产出物**: 完整可上线的应用

---

## 6.1 Phase 6: 集成测试与联调

### 6.1.1 目标

- 端到端流程测试
- 小程序与后端联调
- 管理后台与后端联调
- 性能测试与优化

---

### 6.1.2 测试用例清单

#### 用户端核心流程

| 测试编号 | 测试项 | 预期结果 | 通过 |
|---------|-------|---------|-----|
| U-001 | 微信登录 | 新用户跳转年级选择，老用户进入首页 | [ ] |
| U-002 | 年级选择 | 选择后保存成功，进入首页 | [ ] |
| U-003 | 首页加载 | 显示今日推荐、日历、打卡天数 | [ ] |
| U-004 | 开始阅读 | 正确加载文章内容 | [ ] |
| U-005 | 答题流程 | 选择-提交-显示结果-下一题 | [ ] |
| U-006 | 查看原文 | 答题时可展开查看文章 | [ ] |
| U-007 | 温柔提示 | 点击显示提示内容 | [ ] |
| U-008 | 完成阅读 | 显示得分、能力分析、打卡状态 | [ ] |
| U-009 | 勋章解锁 | 首次阅读获得"阅读新星" | [ ] |
| U-010 | 连续打卡 | 连续3天获得"三日小达人" | [ ] |
| U-011 | 能力雷达图 | 个人中心正确显示雷达图 | [ ] |
| U-012 | 历史记录 | 显示已完成的阅读列表 | [ ] |
| U-013 | 补弱项推荐 | 根据能力推荐文章 | [ ] |

#### 管理端核心流程

| 测试编号 | 测试项 | 预期结果 | 通过 |
|---------|-------|---------|-----|
| A-001 | 管理员登录 | 正确用户名密码可登录 | [ ] |
| A-002 | 仪表盘数据 | 统计数据正确显示 | [ ] |
| A-003 | 创建文章 | 文章保存为草稿状态 | [ ] |
| A-004 | 发布文章 | 状态变更为已发布 | [ ] |
| A-005 | AI 推荐标签 | 返回合理的标签建议 | [ ] |
| A-006 | AI 生成题目 | 生成5道质量合格的题目 | [ ] |
| A-007 | 保存题目 | AI 题目保存到数据库 | [ ] |
| A-008 | 编辑题目 | 修改内容保存成功 | [ ] |
| A-009 | 用户列表 | 显示用户列表和统计 | [ ] |
| A-010 | 标签管理 | CRUD 操作正常 | [ ] |

#### 异常流程测试

| 测试编号 | 测试项 | 预期结果 | 通过 |
|---------|-------|---------|-----|
| E-001 | Token 过期 | 自动跳转登录页 | [ ] |
| E-002 | 网络断开 | 友好的错误提示 | [ ] |
| E-003 | 接口超时 | 显示重试提示 | [ ] |
| E-004 | 重复提交答案 | 返回错误提示 | [ ] |
| E-005 | 并发打卡 | 只创建一条记录 | [ ] |

---

### 6.1.3 性能测试

#### API 响应时间要求

| 接口 | 目标响应时间 | 实际 |
|-----|------------|-----|
| 登录 | < 500ms | |
| 首页数据 | < 800ms | |
| 文章详情 | < 500ms | |
| 提交答案 | < 300ms | |
| 完成阅读 | < 1000ms | |
| AI 生成题目 | < 30s | |

#### 并发测试

```bash
# 使用 wrk 进行压力测试
wrk -t4 -c100 -d30s http://api.example.com/api/v1/articles/

# 预期结果:
# - 100 并发请求下，响应时间 < 1s
# - 错误率 < 1%
```

---

### 6.1.4 联调检查清单

#### 小程序联调

- [ ] 所有 API 地址配置正确
- [ ] 请求头 Token 正确传递
- [ ] 响应数据格式正确解析
- [ ] 错误码正确处理
- [ ] 图片资源正确加载
- [ ] 分享功能正常（如有）

#### 管理后台联调

- [ ] 开发环境代理配置正确
- [ ] 生产环境 API 地址正确
- [ ] 文件上传功能正常
- [ ] 分页加载正常
- [ ] 表单验证完整

---

## 6.2 Phase 7: 部署

### 6.2.1 部署架构

```
                    ┌─────────────────┐
                    │   CloudFlare    │
                    │   (CDN/WAF)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ 小程序静态   │  │ Admin 静态  │  │  API 服务   │
    │  (微信云)   │  │  (Nginx)    │  │ (Docker)   │
    └─────────────┘  └─────────────┘  └──────┬──────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          │                  │                  │
                          ▼                  ▼                  ▼
                   ┌───────────┐      ┌───────────┐      ┌───────────┐
                   │ PostgreSQL │      │   Redis   │      │ AI API    │
                   │  (RDS)    │      │  (Cache)  │      │(SiliconFlow)
                   └───────────┘      └───────────┘      └───────────┘
```

---

### 6.2.2 后端部署 (Docker)

#### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DEBUG=false
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - WECHAT_APP_ID=${WECHAT_APP_ID}
      - WECHAT_APP_SECRET=${WECHAT_APP_SECRET}
      - AI_API_URL=${AI_API_URL}
      - AI_API_KEY=${AI_API_KEY}
    depends_on:
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

volumes:
  redis_data:
```

#### 部署脚本 (scripts/deploy-backend.sh)

```bash
#!/bin/bash
set -e

echo "🚀 开始部署后端服务..."

# 拉取最新代码
git pull origin main

# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 停止旧容器
docker-compose -f docker-compose.prod.yml down

# 运行数据库迁移
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# 启动新容器
docker-compose -f docker-compose.prod.yml up -d

# 检查健康状态
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ 后端部署完成！"
```

---

### 6.2.3 管理后台部署

#### Nginx 配置

```nginx
# /etc/nginx/sites-available/reading-planet-admin
server {
    listen 80;
    server_name admin.reading-planet.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name admin.reading-planet.com;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/admin.reading-planet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.reading-planet.com/privkey.pem;
    
    # 静态文件
    root /var/www/reading-planet-admin/dist;
    index index.html;
    
    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 部署脚本 (scripts/deploy-admin.sh)

```bash
#!/bin/bash
set -e

echo "🚀 开始部署管理后台..."

cd admin

# 安装依赖
npm ci

# 构建生产版本
npm run build

# 部署到服务器
rsync -avz --delete dist/ user@server:/var/www/reading-planet-admin/dist/

# 重载 Nginx
ssh user@server "sudo nginx -t && sudo systemctl reload nginx"

echo "✅ 管理后台部署完成！"
```

---

### 6.2.4 小程序部署

#### 部署流程

1. **配置服务器域名**
   - 登录 [微信公众平台](https://mp.weixin.qq.com)
   - 开发管理 → 开发设置 → 服务器域名
   - 添加 request 合法域名: `https://api.reading-planet.com`

2. **更新配置**
   ```javascript
   // utils/request.js
   const BASE_URL = 'https://api.reading-planet.com/api/v1'
   ```

3. **上传代码**
   - 微信开发者工具 → 上传
   - 填写版本号和描述

4. **提交审核**
   - 微信公众平台 → 版本管理 → 提交审核
   - 填写审核信息

5. **发布上线**
   - 审核通过后发布

---

### 6.2.5 数据库备份策略

```bash
# scripts/backup-db.sh
#!/bin/bash

# 配置
DB_NAME="reading_planet"
DB_USER="postgres"
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 保留最近30天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "✅ 数据库备份完成: backup_$DATE.sql.gz"
```

添加到 crontab:
```bash
# 每天凌晨3点备份
0 3 * * * /path/to/scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

---

### 6.2.6 监控告警

#### 健康检查 API

```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查"""
    try:
        # 检查数据库连接
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
    }
```

#### 监控指标

使用 Prometheus + Grafana 监控:

- 请求量 (QPS)
- 响应时间 (P50, P95, P99)
- 错误率
- 数据库连接数
- Redis 内存使用

---

### 6.2.7 上线检查清单

#### 上线前检查

- [ ] 所有测试用例通过
- [ ] 数据库迁移脚本测试通过
- [ ] 初始数据（标签、能力、勋章）导入完成
- [ ] 环境变量配置正确
- [ ] SSL 证书配置正确
- [ ] 域名解析配置正确
- [ ] 小程序服务器域名配置
- [ ] AI API 额度充足
- [ ] 数据库备份策略配置
- [ ] 监控告警配置

#### 上线后验证

- [ ] 首页正常加载
- [ ] 登录流程正常
- [ ] 阅读答题流程正常
- [ ] 管理后台可访问
- [ ] AI 功能正常
- [ ] 监控数据正常

---

### 6.2.8 功能退化与 MVP 调整备忘

为了确保 MVP 版本按时发布并降低技术风险，部分设计文档中的功能在 V1.0 实现中进行了简化或推迟。这些功能应在后续版本中优先考虑回归。

| 功能模块 | 原设计 | MVP 实现 | 调整原因 | 后续规划 |
|---------|--------|---------|---------|----------|
| **简答题输入** | 支持**语音转文字**输入 | 仅支持**文本输入框** | 避免复杂的微信录音接口对接，专注于核心阅读体验 | V1.2 版本引入语音输入功能 |
| **简答题评分** | **AI 智能评分** (0-100分 + 评语) | 后端**默认通过** (Always Pass) | 降低 MVP 对 AI 实时响应速度的依赖，保证主流程流畅性 | V1.1 版本接入 Phase 5 已实现的 AI 评分逻辑 |

---

## 6.3 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 测试用例 | `docs/test-cases.md` | 测试覆盖完整 |
| Docker 配置 | `backend/Dockerfile` | 镜像构建成功 |
| Docker Compose | `docker-compose.prod.yml` | 服务启动正常 |
| 后端部署脚本 | `scripts/deploy-backend.sh` | 部署成功 |
| 前端部署脚本 | `scripts/deploy-admin.sh` | 部署成功 |
| Nginx 配置 | `nginx/admin.conf` | HTTPS 访问正常 |
| 备份脚本 | `scripts/backup-db.sh` | 备份恢复正常 |
| 监控配置 | `monitoring/` | 告警正常 |

---

## 6.4 项目总结

### 完整工时估算

| 阶段 | 内容 | 工时（人天）|
|-----|------|-----------|
| Phase 0 | 项目基础架构 | 1-2 |
| Phase 1 | 数据库设计 | 2-3 |
| Phase 2.1 | 后端-认证用户 | 2-3 |
| Phase 2.2 | 后端-文章题目 | 3-4 |
| Phase 2.3 | 后端-进度打卡 | 2-3 |
| Phase 2.4 | 后端-管理API | 3-4 |
| Phase 3 | 管理后台前端 | 5-7 |
| Phase 4 | 微信小程序 | 7-10 |
| Phase 5 | AI 集成 | 3-4 |
| Phase 6 | 测试联调 | 2-3 |
| Phase 7 | 部署上线 | 2-3 |
| **总计** | | **32-46 人天** |

### 建议开发顺序

```
Phase 0 (基础架构)
    ↓
Phase 1 (数据库)
    ↓
Phase 2.1-2.4 (后端API) ←→ Phase 3 (管理后台) [可并行]
    ↓
Phase 4 (小程序)
    ↓
Phase 5 (AI集成)
    ↓
Phase 6-7 (测试部署)
```

### 后续迭代建议

1. **V1.1 - 内容扩充**
   - 批量导入公版文章
   - AI 辅助审核优化

2. **V1.2 - 功能增强**
   - 朗读/听读功能
   - 错题本
   - 学习报告

3. **V1.3 - 社交互动**
   - 班级/家庭组
   - 排行榜
   - 分享功能

4. **V2.0 - 商业化**
   - 付费课程
   - VIP 会员
   - 家长端小程序
