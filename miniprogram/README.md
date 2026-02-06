# 阅读星球微信小程序

基于原生微信小程序开发框架构建的儿童阅读理解训练小程序。

## 环境要求

- 微信开发者工具
- 微信小程序 AppID（测试号或真实 AppID）

## 快速开始

### 1. 使用微信开发者工具打开项目

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开微信开发者工具
3. 选择"导入项目"
4. 选择本项目目录 `miniprogram/`
5. 填入 AppID（测试号或真实 AppID）
6. 点击"导入"

### 2. 配置后端 API

编辑 `miniprogram/utils/request.js` 文件，将 `BASE_URL` 修改为实际的后端 API 地址：

```javascript
const BASE_URL = 'https://your-api-domain.com/api/v1';
```

### 3. 编译运行

在微信开发者工具中点击"编译"按钮即可预览小程序。

## 项目结构

```
miniprogram/
├── pages/         # 页面
│   ├── index/     # 首页
│   ├── login/     # 登录页
│   ├── article/   # 阅读页
│   ├── quiz/      # 答题页
│   ├── result/    # 结果页
│   └── profile/   # 个人中心
├── components/    # 自定义组件
├── utils/         # 工具函数
├── services/      # 业务服务封装
├── images/        # 图片资源
├── styles/        # 公共样式
├── app.js         # 小程序入口
├── app.json       # 小程序配置
├── app.wxss       # 全局样式
└── project.config.json  # 项目配置
```

## 开发

### 网络请求

项目已封装了网络请求工具 `utils/request.js`，支持自动添加 Token 和处理 401 错误：

```javascript
const request = require('../../utils/request');

Page({
  onLoad() {
    request.get('/api/articles').then(data => {
      console.log(data);
    });
  }
});
```

### 页面路由

使用微信小程序 API 进行页面跳转：

```javascript
wx.navigateTo({ url: '/pages/article/article' });
wx.switchTab({ url: '/pages/index/index' });
```

### 本地存储

使用微信小程序存储 API：

```javascript
wx.setStorageSync('token', 'xxx');
const token = wx.getStorageSync('token');
```

## 调试

- 在微信开发者工具中可以查看控制台日志
- 使用"调试器"查看网络请求、存储等信息
- 使用"真机调试"在真机上测试

## 发布

1. 在微信开发者工具中点击"上传"
2. 填写版本号和项目备注
3. 上传成功后，在微信公众平台提交审核
