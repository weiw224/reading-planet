# 阅读星球管理后台

基于 Vue 3 + TypeScript + Element Plus 构建的管理后台系统。

## 环境要求

- Node.js 16+
- npm 或 pnpm

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env.local
# 编辑 .env.local 文件
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动。

## 开发

### 运行测试

```bash
npm run test
```

### 代码检查

```bash
npm run lint
```

### 构建

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 技术栈

- **框架**: Vue 3 + TypeScript
- **UI 库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios

## 项目结构

```
src/
├── api/          # API 调用封装
├── assets/       # 静态资源
├── components/   # 公共组件
├── composables/  # 组合式函数
├── layouts/      # 布局组件
├── router/       # 路由配置
├── stores/       # Pinia 状态管理
├── styles/       # 全局样式
├── utils/        # 工具函数
└── views/       # 页面组件
```
