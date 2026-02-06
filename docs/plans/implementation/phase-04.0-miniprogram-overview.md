# Phase 4.0: 微信小程序开发 - 总览与设计规范

> **预估工时**: 7-10 人天  
> **前置依赖**: Phase 2 (后端 API)  
> **产出物**: 完整的微信小程序用户端

---

## 4.0.1 文档索引

本阶段文档拆分为以下部分：

| 文件 | 内容 |
|-----|------|
| `phase-04.0-miniprogram-overview.md` | 总览、设计规范、项目结构 (本文件) |
| `phase-04.1-miniprogram-core.md` | 核心配置、网络请求、数据服务 |
| `phase-04.2a-pages-login.md` | 登录页、年级选择页 |
| `phase-04.2b-pages-index.md` | 首页（今日成就、日历、推荐） |
| `phase-04.2c-pages-article.md` | 文章阅读页 |
| `phase-04.2d-pages-quiz.md` | 答题页（多种题型） |
| `phase-04.2e-pages-result.md` | 练习结果页 |
| `phase-04.2f-pages-profile.md` | 个人中心、勋章墙、历史记录 |
| `phase-04.3-miniprogram-components.md` | 自定义组件库 |

---

## 4.0.2 设计规范（基于原型）

### 配色方案

根据 `frontend-template` 原型设计，采用**温暖橙黄色系**：

```css
/* 主色调 - 橙黄色系 */
--color-primary: #F5A623;           /* 主色：金橙色 */
--color-primary-light: #FFD93D;     /* 浅金色 */
--color-primary-dark: #E8941C;      /* 深橙色 */

/* 背景色 - 米黄/奶油色系 */
--bg-page: #FFF8E7;                 /* 页面背景：米黄色 */
--bg-card: #FFFFFF;                 /* 卡片背景 */
--bg-card-warm: #FFF5E6;            /* 暖色卡片背景 */
--bg-section: #FEF3E2;              /* 区块背景 */

/* 文字颜色 */
--text-primary: #333333;            /* 主文字 */
--text-secondary: #666666;          /* 次要文字 */
--text-hint: #999999;               /* 提示文字 */
--text-orange: #F5A623;             /* 强调文字 */

/* 功能色 */
--color-success: #52C41A;           /* 成功/正确 */
--color-error: #FF4D4F;             /* 错误 */
--color-fire: #FF6B35;              /* 火焰/连续天数 */

/* 进度条 */
--progress-bg: #FEE4B3;             /* 进度条背景 */
--progress-fill: #F5A623;           /* 进度条填充 */
```

### 字体规范

```css
/* 字体大小 */
--font-xs: 20rpx;      /* 辅助说明 */
--font-sm: 24rpx;      /* 小字 */
--font-base: 28rpx;    /* 正文 */
--font-md: 32rpx;      /* 中号 */
--font-lg: 36rpx;      /* 大号 */
--font-xl: 40rpx;      /* 标题 */
--font-xxl: 48rpx;     /* 大标题 */
--font-huge: 64rpx;    /* 统计数字 */

/* 字体粗细 */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 圆角规范

```css
--radius-sm: 8rpx;     /* 小圆角 */
--radius-md: 16rpx;    /* 中圆角 */
--radius-lg: 24rpx;    /* 大圆角 */
--radius-xl: 32rpx;    /* 超大圆角 */
--radius-full: 50%;    /* 圆形 */
```

### 阴影规范

```css
--shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
--shadow-md: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
--shadow-lg: 0 8rpx 32rpx rgba(0, 0, 0, 0.12);
```

---

## 4.0.3 原型页面对应表

| 原型文件夹 | 对应页面 | 路由 |
|-----------|---------|------|
| `微信登录界面` | 登录页 | `/pages/login/login` |
| `首页_(每日练习与日历)` | 首页 | `/pages/index/index` |
| `article_reading_view` | 文章阅读页 | `/pages/article/article` |
| `interactive_quiz_question_*` | 答题页 | `/pages/quiz/quiz` |
| `互动练习题_(连线题)` | 连线题组件 | 答题页组件 |
| `互动练习题_(拖拽排序)` | 排序题组件 | 答题页组件 |
| `温柔提示引导图卡` | 温柔提示弹窗 | 答题页组件 |
| `practice_results_&_badge_unlock` | 结果页 | `/pages/result/result` |
| `个人主页_(能力与历史)_*` | 个人中心 | `/pages/profile/profile` |

---

## 4.0.4 项目结构

```
miniprogram/
├── pages/                        # 页面
│   ├── index/                    # 首页（每日练习与日历）
│   │   ├── index.js
│   │   ├── index.wxml
│   │   ├── index.wxss
│   │   └── index.json
│   │
│   ├── login/                    # 登录页
│   ├── grade-select/             # 年级选择页
│   ├── article/                  # 文章阅读页
│   ├── quiz/                     # 答题页（多种题型）
│   ├── result/                   # 练习结果页
│   ├── profile/                  # 个人主页
│   ├── badges/                   # 勋章墙
│   └── history/                  # 历史记录
│
├── components/                   # 自定义组件
│   ├── article-card/             # 文章卡片
│   ├── calendar/                 # 日历打卡组件
│   ├── today-stats/              # 今日成就统计
│   ├── quiz-choice/              # 选择题组件
│   ├── quiz-matching/            # 连线题组件
│   ├── quiz-sorting/             # 排序题组件
│   ├── quiz-fill/                # 填空题组件
│   ├── gentle-hint/              # 温柔提示图卡
│   ├── article-popup/            # 查看原文弹窗
│   ├── progress-bar/             # 答题进度条
│   ├── radar-chart/              # 能力雷达图
│   ├── badge-item/               # 勋章展示项
│   ├── badge-popup/              # 勋章详情弹窗
│   ├── mascot/                   # 小动物引导角色
│   └── empty-state/              # 空状态
│
├── utils/                        # 工具函数
│   ├── request.js                # 网络请求封装
│   ├── auth.js                   # 认证相关
│   ├── storage.js                # 本地存储
│   └── util.js                   # 通用工具
│
├── services/                     # 业务服务
│   ├── userService.js
│   ├── articleService.js
│   ├── quizService.js
│   └── progressService.js
│
├── images/                       # 图片资源
│   ├── icons/                    # 图标
│   │   ├── home.png
│   │   ├── home-active.png
│   │   ├── practice.png
│   │   ├── practice-active.png
│   │   ├── profile.png
│   │   ├── profile-active.png
│   │   ├── fire.png             # 连续天数火焰
│   │   ├── trophy.png           # 勋章
│   │   ├── star.png             # 成长值星星
│   │   ├── book.png             # 阅读图标
│   │   ├── hint.png             # 温柔提示图标
│   │   └── ...
│   │
│   ├── mascots/                  # 引导角色
│   │   ├── koala.png            # 考拉（登录页）
│   │   ├── owl.png              # 猫头鹰（答题引导）
│   │   ├── fox.png              # 小狐狸（近义词/连线）
│   │   └── rabbit.png           # 小兔子（可爱提示）
│   │
│   ├── badges/                   # 勋章图标
│   │   ├── badge-reader.png     # 博学多才
│   │   ├── badge-thinker.png    # 思考之星
│   │   └── ...
│   │
│   └── backgrounds/              # 背景图
│       ├── login-bg.png
│       └── result-stars.png
│
├── styles/                       # 公共样式
│   └── theme.wxss               # 主题变量和基础样式
│
├── app.js                        # 应用入口
├── app.json                      # 应用配置
├── app.wxss                      # 全局样式
├── project.config.json           # 项目配置
└── sitemap.json
```

---

## 4.0.5 图片资源清单

根据原型设计，需要准备以下图片资源：

### 引导角色（吉祥物）

| 角色 | 使用场景 | 尺寸建议 |
|-----|---------|---------|
| 考拉 (Koala) | 登录页、欢迎引导 | 400x400px |
| 猫头鹰 (Owl) | 答题页引导、进度指示 | 80x80px |
| 小狐狸 (Fox) | 近义词/词语匹配题 | 120x120px |
| 小兔子 (Rabbit) | 温柔提示、可爱插画 | 200x200px |

### 图标资源

| 图标 | 用途 | 尺寸 |
|-----|------|------|
| 火焰 | 连续天数指示 | 48x48px |
| 奖杯 | 勋章数量 | 48x48px |
| 星星 | 成长值/难度 | 48x48px |
| 书本 | 阅读图标 | 48x48px |
| 灯泡 | 温柔提示按钮 | 48x48px |
| 日历锁 | 未来日期 | 32x32px |
| 对勾圆 | 已完成打卡 | 48x48px |

### 勋章资源

| 勋章 | 描述 | 状态 |
|-----|------|------|
| 博学多才 | 阅读达人 | 已获得(彩色)/未获得(灰色) |
| 思考之星 | 思考能力 | 已获得(彩色)/未获得(灰色) |
| 成就达人 | 综合成就 | 已获得(彩色)/未获得(灰色) |
| 无敌战神 | 战胜困难 | 已获得(彩色)/未获得(灰色) |
| 满分达人 | 满分成绩 | 已获得(彩色)/未获得(灰色) |
| 阅读狂人 | 连续阅读 | 已获得(彩色)/未获得(灰色) |
| 角色大侦探 | 人物分析 | 已获得(彩色)/未获得(灰色) |
| 人物侦探 | 人物特征 | 已获得(彩色)/未获得(灰色) |

---

## 4.0.6 TabBar 配置

原型显示有 **3 个 Tab**：

```json
{
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#F5A623",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/icons/home.png",
        "selectedIconPath": "images/icons/home-active.png"
      },
      {
        "pagePath": "pages/practice/practice",
        "text": "练习",
        "iconPath": "images/icons/practice.png",
        "selectedIconPath": "images/icons/practice-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "images/icons/profile.png",
        "selectedIconPath": "images/icons/profile-active.png"
      }
    ]
  }
}
```

---

## 4.0.7 核心功能流程

### 用户首次使用流程

```
启动小程序
    ↓
[检查登录状态]
    ↓ (未登录)
登录页 (微信一键登录)
    ↓
[调用 /auth/wechat-login]
    ↓ (新用户)
年级选择页
    ↓
[保存年级信息]
    ↓
首页
```

### 每日阅读流程

```
首页
    ↓
[点击今日推荐卡片]
    ↓
文章阅读页
    ↓
[阅读完成，点击开始答题]
    ↓
答题页 (5道题目)
    ↓
[逐题作答，可查看原文/温柔提示]
    ↓
[全部完成]
    ↓
结果页 (得分、能力分析、勋章)
    ↓
[返回首页 / 再来一篇]
```

### 答题页交互流程

```
显示第 N 题
    ↓
[用户选择答案]
    ↓
[点击确认答案]
    ↓
[调用 /progress/{id}/submit]
    ↓
显示答案反馈（对/错 + 解析）
    ↓
[点击下一题]
    ↓
(循环直到最后一题)
    ↓
[完成所有题目]
    ↓
[调用 /progress/{id}/complete]
    ↓
跳转结果页
```

---

## 4.0.8 状态管理

使用 `app.globalData` 管理全局状态：

```javascript
// app.js
App({
  globalData: {
    // 用户相关
    token: null,
    userInfo: null,
    isLoggedIn: false,
    
    // 当前阅读进度
    currentProgress: {
      progressId: null,
      articleId: null,
      startTime: null,
    },
    
    // 系统配置
    systemInfo: null,
  },
})
```

---

## 4.0.9 验收标准总览

### 视觉验收

- [ ] 配色与原型一致（橙黄色系）
- [ ] 组件样式与原型一致
- [ ] 引导角色（考拉、猫头鹰等）正确显示
- [ ] 动画效果流畅

### 功能验收

- [ ] 登录流程完整
- [ ] 首页数据正确加载
- [ ] 答题流程完整
- [ ] 多种题型支持
- [ ] 温柔提示正常显示
- [ ] 查看原文功能正常
- [ ] 结果页数据正确
- [ ] 勋章解锁正常
- [ ] 个人中心数据正确

### 性能验收

- [ ] 首页加载时间 < 2秒
- [ ] 页面切换流畅
- [ ] 图片加载优化

