# Phase 0: 项目基础架构搭建

> **预估工时**: 1-2 人天  
> **前置依赖**: 无  
> **产出物**: 完整的项目初始化代码和开发环境配置

---

## 0.1 目标概述

本阶段完成项目的基础架构搭建，包括：
- 项目目录结构初始化
- 各端开发环境配置
- 代码规范与工具链配置
- Git 工作流设置

---

## 0.2 项目目录结构

```
reading-planet/
├── docs/                          # 文档目录
│   └── plans/                     # 计划文档
│       └── implementation/        # 实现计划
│
├── backend/                       # 后端服务 (Python + FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 应用入口
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── models/               # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   ├── question.py
│   │   │   └── ...
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   └── ...
│   │   ├── api/                  # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── articles.py
│   │   │   │   ├── questions.py
│   │   │   │   └── ...
│   │   │   └── router.py
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── article_service.py
│   │   │   ├── ai_service.py
│   │   │   └── ...
│   │   ├── utils/                # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── helpers.py
│   │   └── tests/                # 单元测试
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_auth.py
│   │       ├── test_articles.py
│   │       └── ...
│   ├── alembic/                  # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── requirements.txt          # Python 依赖
│   ├── requirements-dev.txt      # 开发依赖
│   ├── .env.example              # 环境变量示例
│   ├── pytest.ini                # pytest 配置
│   └── README.md
│
├── admin/                         # 管理后台 (Vue 3 + Element Plus)
│   ├── src/
│   │   ├── api/                  # API 调用封装
│   │   ├── assets/               # 静态资源
│   │   ├── components/           # 公共组件
│   │   ├── composables/          # 组合式函数
│   │   ├── layouts/              # 布局组件
│   │   ├── router/               # 路由配置
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── styles/               # 全局样式
│   │   ├── utils/                # 工具函数
│   │   ├── views/                # 页面组件
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── articles/
│   │   │   ├── questions/
│   │   │   ├── users/
│   │   │   └── settings/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── miniprogram/                   # 微信小程序 (原生开发)
│   ├── pages/                    # 页面
│   │   ├── index/                # 首页
│   │   ├── login/                # 登录页
│   │   ├── article/              # 阅读页
│   │   ├── quiz/                 # 答题页
│   │   ├── result/               # 结果页
│   │   └── profile/              # 个人中心
│   ├── components/               # 自定义组件
│   │   ├── article-card/
│   │   ├── quiz-question/
│   │   ├── radar-chart/
│   │   ├── badge-item/
│   │   └── calendar/
│   ├── utils/                    # 工具函数
│   │   ├── request.js            # 网络请求封装
│   │   ├── auth.js               # 认证相关
│   │   ├── storage.js            # 本地存储
│   │   └── util.js               # 通用工具
│   ├── services/                 # 业务服务封装
│   │   ├── userService.js
│   │   ├── articleService.js
│   │   └── quizService.js
│   ├── images/                   # 图片资源
│   ├── styles/                   # 公共样式
│   │   └── common.wxss
│   ├── app.js
│   ├── app.json
│   ├── app.wxss
│   ├── project.config.json
│   ├── sitemap.json
│   └── README.md
│
├── frontend-template/             # 界面原型 (已有)
│
├── scripts/                       # 部署和工具脚本
│   ├── setup-dev.sh              # 开发环境初始化
│   ├── deploy-backend.sh         # 后端部署
│   └── deploy-admin.sh           # 管理后台部署
│
├── .gitignore
├── .editorconfig
├── docker-compose.yml            # 本地开发 Docker 配置
├── docker-compose.prod.yml       # 生产环境 Docker 配置
└── README.md                     # 项目总览
```

---

## 0.3 后端环境初始化

### 0.3.1 创建后端项目结构

```bash
# 创建后端目录
mkdir -p backend/app/{models,schemas,api/v1,services,utils,tests}
cd backend

# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 0.3.2 requirements.txt

```txt
# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.25
asyncpg==0.29.0  # PostgreSQL 异步驱动
alembic==1.13.1  # 数据库迁移

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# HTTP 客户端 (调用 AI API)
httpx==0.26.0

# 数据验证
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# 工具
python-dotenv==1.0.0

# Redis (可选, 用于缓存)
redis==5.0.1
```

### 0.3.3 requirements-dev.txt

```txt
-r requirements.txt

# 测试
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0  # 用于测试 FastAPI

# 代码质量
black==24.1.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0

# 开发工具
watchfiles==0.21.0
```

### 0.3.4 环境变量配置 (.env.example)

```env
# 应用配置
APP_NAME=reading-planet
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/reading_planet

# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379/0

# 微信小程序配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# AI 服务配置 (硅基流动)
AI_API_URL=https://api.siliconflow.cn/v1
AI_API_KEY=your-siliconflow-api-key
AI_MODEL=Qwen/Qwen2.5-7B-Instruct

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天
```

### 0.3.5 FastAPI 应用入口 (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="阅读星球 - 儿童阅读理解训练平台 API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app": settings.APP_NAME}
```

### 0.3.6 配置管理 (app/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "reading-planet"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # 数据库
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = ""
    
    # 微信
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # AI 服务
    AI_API_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 0.3.7 pytest 配置 (pytest.ini)

```ini
[pytest]
asyncio_mode = auto
testpaths = app/tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short --cov=app --cov-report=term-missing
filterwarnings =
    ignore::DeprecationWarning
```

---

## 0.4 管理后台环境初始化

### 0.4.1 创建 Vue 3 项目

```bash
# 使用 Vite 创建 Vue 3 + TypeScript 项目
cd /path/to/reading-planet
npm create vite@latest admin -- --template vue-ts
cd admin

# 安装依赖
npm install

# 安装 Element Plus
npm install element-plus @element-plus/icons-vue

# 安装其他必要依赖
npm install vue-router@4 pinia axios
npm install -D @types/node sass unplugin-auto-import unplugin-vue-components
```

### 0.4.2 package.json 主要依赖

```json
{
  "name": "reading-planet-admin",
  "version": "0.1.0",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts",
    "test": "vitest"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.6.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.27",
    "sass": "^1.69.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0",
    "vitest": "^1.2.0",
    "@vue/test-utils": "^2.4.0"
  }
}
```

### 0.4.3 Vite 配置 (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 0.4.4 环境变量 (.env.example)

```env
# API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用标题
VITE_APP_TITLE=阅读星球管理后台
```

---

## 0.5 微信小程序环境初始化

### 0.5.1 创建小程序项目

使用微信开发者工具创建项目，选择：
- 项目目录：`miniprogram/`
- AppID：使用测试号或真实 AppID
- 开发模式：小程序
- 后端服务：不使用云服务
- 语言：JavaScript

### 0.5.2 app.json 基础配置

```json
{
  "pages": [
    "pages/index/index",
    "pages/login/login",
    "pages/article/article",
    "pages/quiz/quiz",
    "pages/result/result",
    "pages/profile/profile"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#FF9500",
    "navigationBarTitleText": "阅读星球",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#FF9500",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/tab/home.png",
        "selectedIconPath": "images/tab/home-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "images/tab/profile.png",
        "selectedIconPath": "images/tab/profile-active.png"
      }
    ]
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

### 0.5.3 网络请求封装 (utils/request.js)

```javascript
const BASE_URL = 'https://your-api-domain.com/api/v1';

/**
 * 封装请求方法
 * @param {Object} options 请求配置
 * @returns {Promise}
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    
    wx.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // Token 过期，跳转登录
          wx.removeStorageSync('token');
          wx.navigateTo({ url: '/pages/login/login' });
          reject(new Error('请重新登录'));
        } else {
          reject(new Error(res.data.message || '请求失败'));
        }
      },
      fail: (err) => {
        reject(new Error('网络错误'));
      },
    });
  });
};

// 导出便捷方法
module.exports = {
  get: (url, data) => request({ url, method: 'GET', data }),
  post: (url, data) => request({ url, method: 'POST', data }),
  put: (url, data) => request({ url, method: 'PUT', data }),
  delete: (url, data) => request({ url, method: 'DELETE', data }),
};
```

### 0.5.4 project.config.json

```json
{
  "appid": "your-wechat-app-id",
  "compileType": "miniprogram",
  "projectname": "reading-planet",
  "setting": {
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true,
    "urlCheck": true,
    "scopeDataCheck": false
  },
  "libVersion": "3.3.0"
}
```

---

## 0.6 Docker 开发环境

### 0.6.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: reading-planet-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: reading_planet
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis 缓存 (可选)
  redis:
    image: redis:7-alpine
    container_name: reading-planet-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 0.6.2 启动开发环境

```bash
# 启动数据库和 Redis
docker-compose up -d

# 查看状态
docker-compose ps
```

---

## 0.7 Git 配置

### 0.7.1 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Node.js
node_modules/
dist/
.npm
*.log

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# 小程序
miniprogram/miniprogram_npm/
miniprogram/.miniprogram/

# 构建产物
*.zip
*.tar.gz

# 本地环境配置
.env.local
.env.*.local
```

### 0.7.2 .editorconfig

```ini
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

### 0.7.3 Git 分支策略

```
main              # 生产分支，只接受 PR 合并
├── develop       # 开发主分支
├── feature/*     # 功能分支 (feature/add-login)
├── bugfix/*      # 修复分支 (bugfix/fix-auth)
└── release/*     # 发布分支 (release/v1.0.0)
```

---

## 0.8 验收标准

### 0.8.1 目录结构验收

- [ ] `backend/` 目录结构符合规范，包含必要的初始文件
- [ ] `admin/` Vue 3 项目可正常启动 (`npm run dev`)
- [ ] `miniprogram/` 可在微信开发者工具中正常打开
- [ ] Docker 容器（PostgreSQL、Redis）可正常启动

### 0.8.2 环境验收

- [ ] 后端可正常启动：`uvicorn app.main:app --reload`
- [ ] 访问 `http://localhost:8000/health` 返回健康状态
- [ ] 访问 `http://localhost:8000/docs` 可看到 Swagger 文档
- [ ] 管理后台可正常启动：`npm run dev`
- [ ] 小程序编译无错误

### 0.8.3 代码质量验收

- [ ] Python 代码通过 `black --check .` 检查
- [ ] Python 代码通过 `flake8` 检查
- [ ] TypeScript 代码通过 `npm run lint` 检查

---

## 0.9 单元测试要求

### 0.9.1 后端基础测试 (app/tests/test_health.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查接口"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 0.9.2 运行测试命令

```bash
# 后端测试
cd backend
source venv/bin/activate
pytest

# 管理后台测试
cd admin
npm run test
```

---

## 0.10 参考命令汇总

```bash
# ===== 初始化项目 =====
# 克隆仓库后执行以下命令

# 1. 启动数据库
docker-compose up -d

# 2. 初始化后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入必要配置
uvicorn app.main:app --reload

# 3. 初始化管理后台
cd ../admin
npm install
cp .env.example .env.local
npm run dev

# 4. 初始化小程序
# 使用微信开发者工具打开 miniprogram/ 目录
```

---

## 0.11 交付物清单

| 交付物 | 说明 | 验收标准 |
|--------|------|----------|
| 项目目录结构 | 完整的三端目录结构 | 符合本文档规范 |
| 后端基础代码 | FastAPI 项目骨架 | 可启动并访问 /health |
| 管理后台基础代码 | Vue 3 项目骨架 | 可正常运行 dev server |
| 小程序基础代码 | 原生小程序骨架 | 可在开发者工具编译 |
| Docker 配置 | 开发环境容器编排 | PostgreSQL/Redis 可正常运行 |
| 环境配置 | .env 模板文件 | 包含所有必要配置项 |
| Git 配置 | .gitignore, .editorconfig | 已忽略临时文件 |
| README 文档 | 各端启动说明 | 新开发者可按文档启动 |
