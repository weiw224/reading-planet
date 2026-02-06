# Phase 4.1: 微信小程序 - 核心配置与数据服务

> **前置依赖**: Phase 4.0 (设计规范)  
> **本文件范围**: 应用配置、全局样式、网络请求、业务服务

---

## 4.1.1 应用配置 (app.json)

```json
{
  "pages": [
    "pages/index/index",
    "pages/practice/practice",
    "pages/login/login",
    "pages/grade-select/grade-select",
    "pages/article/article",
    "pages/quiz/quiz",
    "pages/result/result",
    "pages/profile/profile",
    "pages/badges/badges",
    "pages/history/history"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#FFF8E7",
    "navigationBarTitleText": "阅读星球",
    "navigationBarTextStyle": "black",
    "backgroundColor": "#FFF8E7"
  },
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
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json",
  "lazyCodeLoading": "requiredComponents"
}
```

---

## 4.1.2 应用入口 (app.js)

```javascript
App({
  globalData: {
    // 用户认证
    token: null,
    userInfo: null,
    isLoggedIn: false,
    
    // 当前阅读进度
    currentProgress: {
      progressId: null,
      articleId: null,
      startTime: null,
    },
    
    // 系统信息
    systemInfo: null,
    statusBarHeight: 0,
    
    // API 配置
    apiBaseUrl: 'https://api.reading-planet.com/api/v1',
  },

  onLaunch() {
    // 获取系统信息
    this.initSystemInfo()
    
    // 检查登录状态
    this.checkLoginStatus()
  },

  // 初始化系统信息
  initSystemInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync()
      this.globalData.systemInfo = systemInfo
      this.globalData.statusBarHeight = systemInfo.statusBarHeight
    } catch (e) {
      console.error('获取系统信息失败:', e)
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      this.globalData.isLoggedIn = true
    }
  },

  // 设置登录信息
  setLoginInfo(token, userInfo) {
    this.globalData.token = token
    this.globalData.userInfo = userInfo
    this.globalData.isLoggedIn = true
    
    wx.setStorageSync('token', token)
    wx.setStorageSync('userInfo', userInfo)
  },

  // 更新用户信息
  updateUserInfo(userInfo) {
    this.globalData.userInfo = userInfo
    wx.setStorageSync('userInfo', userInfo)
  },

  // 清除登录信息
  clearLoginInfo() {
    this.globalData.token = null
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    this.globalData.currentProgress = {
      progressId: null,
      articleId: null,
      startTime: null,
    }
    
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
  },

  // 设置当前阅读进度
  setCurrentProgress(progressId, articleId) {
    this.globalData.currentProgress = {
      progressId,
      articleId,
      startTime: Date.now(),
    }
  },

  // 清除当前阅读进度
  clearCurrentProgress() {
    this.globalData.currentProgress = {
      progressId: null,
      articleId: null,
      startTime: null,
    }
  },
})
```

---

## 4.1.3 主题样式 (styles/theme.wxss)

```css
/* ========================================
   阅读星球 - 主题样式文件
   基于原型设计的橙黄色系配色
======================================== */

/* 页面基础 */
page {
  --color-primary: #F5A623;
  --color-primary-light: #FFD93D;
  --color-primary-dark: #E8941C;
  
  --bg-page: #FFF8E7;
  --bg-card: #FFFFFF;
  --bg-card-warm: #FFF5E6;
  --bg-section: #FEF3E2;
  
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-hint: #999999;
  --text-orange: #F5A623;
  
  --color-success: #52C41A;
  --color-error: #FF4D4F;
  --color-fire: #FF6B35;
  
  --progress-bg: #FEE4B3;
  --progress-fill: #F5A623;
  
  --radius-sm: 8rpx;
  --radius-md: 16rpx;
  --radius-lg: 24rpx;
  --radius-xl: 32rpx;
  
  --shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8rpx 32rpx rgba(0, 0, 0, 0.12);
  
  background-color: var(--bg-page);
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: var(--text-primary);
  box-sizing: border-box;
}

/* ======================================== 
   通用工具类
======================================== */

/* 文字颜色 */
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-hint { color: var(--text-hint); }
.text-orange { color: var(--color-primary); }
.text-success { color: var(--color-success); }
.text-error { color: var(--color-error); }
.text-white { color: #ffffff; }

/* 背景颜色 */
.bg-page { background-color: var(--bg-page); }
.bg-card { background-color: var(--bg-card); }
.bg-warm { background-color: var(--bg-card-warm); }
.bg-primary { background-color: var(--color-primary); }

/* 字体大小 */
.text-xs { font-size: 20rpx; }
.text-sm { font-size: 24rpx; }
.text-base { font-size: 28rpx; }
.text-md { font-size: 32rpx; }
.text-lg { font-size: 36rpx; }
.text-xl { font-size: 40rpx; }
.text-xxl { font-size: 48rpx; }
.text-huge { font-size: 64rpx; }

/* 字体粗细 */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Flex 布局 */
.flex { display: flex; }
.flex-row { display: flex; flex-direction: row; }
.flex-col { display: flex; flex-direction: column; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.flex-around { display: flex; align-items: center; justify-content: space-around; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.flex-1 { flex: 1; }
.flex-wrap { flex-wrap: wrap; }

/* 间距 */
.p-0 { padding: 0; }
.p-10 { padding: 10rpx; }
.p-20 { padding: 20rpx; }
.p-30 { padding: 30rpx; }
.p-40 { padding: 40rpx; }
.px-20 { padding-left: 20rpx; padding-right: 20rpx; }
.px-30 { padding-left: 30rpx; padding-right: 30rpx; }
.py-20 { padding-top: 20rpx; padding-bottom: 20rpx; }
.py-30 { padding-top: 30rpx; padding-bottom: 30rpx; }

.m-0 { margin: 0; }
.m-10 { margin: 10rpx; }
.m-20 { margin: 20rpx; }
.m-30 { margin: 30rpx; }
.mb-10 { margin-bottom: 10rpx; }
.mb-20 { margin-bottom: 20rpx; }
.mb-30 { margin-bottom: 30rpx; }
.mt-20 { margin-top: 20rpx; }
.mt-30 { margin-top: 30rpx; }
.mr-10 { margin-right: 10rpx; }
.mr-20 { margin-right: 20rpx; }
.ml-10 { margin-left: 10rpx; }
.ml-20 { margin-left: 20rpx; }

/* 圆角 */
.rounded-sm { border-radius: var(--radius-sm); }
.rounded-md { border-radius: var(--radius-md); }
.rounded-lg { border-radius: var(--radius-lg); }
.rounded-xl { border-radius: var(--radius-xl); }
.rounded-full { border-radius: 50%; }

/* 阴影 */
.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }

/* 文字对齐 */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* 溢出处理 */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ======================================== 
   通用组件样式
======================================== */

/* 卡片 */
.card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.card-warm {
  background: var(--bg-card-warm);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

/* 主按钮 */
.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: 50rpx;
  padding: 24rpx 60rpx;
  font-size: 32rpx;
  font-weight: 500;
  line-height: 1;
}

.btn-primary::after {
  border: none;
}

.btn-primary:active {
  background: var(--color-primary-dark);
}

/* 次要按钮 */
.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  color: var(--color-primary);
  border: 2rpx solid var(--color-primary);
  border-radius: 50rpx;
  padding: 22rpx 58rpx;
  font-size: 32rpx;
  font-weight: 500;
  line-height: 1;
}

.btn-secondary::after {
  border: none;
}

/* 文字按钮 */
.btn-text {
  background: transparent;
  color: var(--text-secondary);
  border: none;
  padding: 20rpx;
  font-size: 28rpx;
}

.btn-text::after {
  border: none;
}

/* 标签 */
.tag {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.tag-orange {
  background: rgba(245, 166, 35, 0.15);
  color: var(--color-primary);
}

.tag-green {
  background: rgba(82, 196, 26, 0.15);
  color: var(--color-success);
}

/* 分割线 */
.divider {
  height: 1rpx;
  background: #f0f0f0;
  margin: 20rpx 0;
}

/* 安全区域底部 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}
```

---

## 4.1.4 全局样式 (app.wxss)

```css
/* 引入主题样式 */
@import './styles/theme.wxss';

/* 页面容器 */
.page-container {
  min-height: 100vh;
  background: var(--bg-page);
  padding-bottom: 120rpx;
}

/* 内容区域 */
.content-wrapper {
  padding: 30rpx;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
}

/* 区块标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24rpx;
}

.section-subtitle {
  font-size: 24rpx;
  color: var(--text-hint);
  font-weight: normal;
  margin-left: 12rpx;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 60rpx;
}

.empty-state .icon {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 30rpx;
  opacity: 0.5;
}

.empty-state .text {
  font-size: 28rpx;
  color: var(--text-hint);
}
```

---

## 4.1.5 网络请求封装 (utils/request.js)

```javascript
const app = getApp()

/**
 * 网络请求封装
 * 统一处理请求头、错误、登录态
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const { 
      url, 
      method = 'GET', 
      data, 
      showLoading = true,
      loadingText = '加载中...',
      showError = true 
    } = options
    
    // 显示加载
    if (showLoading) {
      wx.showLoading({ 
        title: loadingText, 
        mask: true 
      })
    }
    
    // 请求头
    const header = {
      'Content-Type': 'application/json',
    }
    
    // 添加认证 Token
    if (app.globalData.token) {
      header['Authorization'] = `Bearer ${app.globalData.token}`
    }
    
    // 完整 URL
    const fullUrl = url.startsWith('http') 
      ? url 
      : app.globalData.apiBaseUrl + url
    
    wx.request({
      url: fullUrl,
      method,
      data,
      header,
      success: (res) => {
        if (showLoading) {
          wx.hideLoading()
        }
        
        // HTTP 状态码处理
        if (res.statusCode === 200) {
          // 业务状态码处理
          if (res.data.code === 0) {
            resolve(res.data.data)
          } else {
            const errorMsg = res.data.message || '请求失败'
            if (showError) {
              wx.showToast({ 
                title: errorMsg, 
                icon: 'none',
                duration: 2000
              })
            }
            reject({ code: res.data.code, message: errorMsg })
          }
        } else if (res.statusCode === 401) {
          // Token 过期，清除登录信息并跳转
          app.clearLoginInfo()
          wx.showToast({ 
            title: '登录已过期，请重新登录', 
            icon: 'none' 
          })
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' })
          }, 1500)
          reject({ code: 401, message: '登录已过期' })
        } else if (res.statusCode === 404) {
          if (showError) {
            wx.showToast({ title: '资源不存在', icon: 'none' })
          }
          reject({ code: 404, message: '资源不存在' })
        } else {
          if (showError) {
            wx.showToast({ title: '服务器错误', icon: 'none' })
          }
          reject({ code: res.statusCode, message: '服务器错误' })
        }
      },
      fail: (err) => {
        if (showLoading) {
          wx.hideLoading()
        }
        if (showError) {
          wx.showToast({ 
            title: '网络连接失败，请检查网络', 
            icon: 'none',
            duration: 2000
          })
        }
        reject({ code: -1, message: '网络连接失败', error: err })
      }
    })
  })
}

/**
 * GET 请求
 */
const get = (url, data, options = {}) => {
  return request({ url, method: 'GET', data, ...options })
}

/**
 * POST 请求  
 */
const post = (url, data, options = {}) => {
  return request({ url, method: 'POST', data, ...options })
}

/**
 * PUT 请求
 */
const put = (url, data, options = {}) => {
  return request({ url, method: 'PUT', data, ...options })
}

/**
 * DELETE 请求
 */
const del = (url, data, options = {}) => {
  return request({ url, method: 'DELETE', data, ...options })
}

module.exports = {
  request,
  get,
  post,
  put,
  del
}
```

---

## 4.1.6 用户服务 (services/userService.js)

```javascript
const { get, post, put } = require('../utils/request')

const userService = {
  /**
   * 微信登录
   * @param {string} code - wx.login 获取的 code
   */
  wechatLogin(code) {
    return post('/auth/wechat-login', { code })
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    return get('/users/me')
  },

  /**
   * 更新用户信息
   * @param {object} data - { nickname, avatar_url, grade }
   */
  updateUser(data) {
    return put('/users/me', data)
  },

  /**
   * 获取用户统计数据
   * 包含 total_readings, streak_days, badge_count 等
   */
  getUserStats() {
    return get('/users/me/stats')
  },

  /**
   * 获取能力雷达图数据
   * 返回各能力维度的分数
   */
  getAbilityRadar() {
    return get('/users/me/abilities')
  },

  /**
   * 获取打卡记录
   * @param {number} year - 年份
   * @param {number} month - 月份
   */
  getCheckins(year, month) {
    return get('/users/me/checkins', { year, month })
  },

  /**
   * 获取用户勋章列表
   * 包含已获得和未获得的勋章
   */
  getBadges() {
    return get('/users/me/badges')
  },

  /**
   * 获取用户勋章详情
   * @param {number} badgeId - 勋章ID
   */
  getBadgeDetail(badgeId) {
    return get(`/users/me/badges/${badgeId}`)
  },
}

module.exports = userService
```

---

## 4.1.7 文章服务 (services/articleService.js)

```javascript
const { get } = require('../utils/request')

const articleService = {
  /**
   * 获取今日推荐文章
   * 根据用户年级智能推荐
   */
  getTodayArticle() {
    return get('/articles/today')
  },

  /**
   * 获取补弱项推荐文章
   * 根据用户薄弱能力推荐
   */
  getWeakPointArticle() {
    return get('/articles/weak-point')
  },

  /**
   * 获取文章详情
   * @param {number} articleId - 文章ID
   */
  getArticleDetail(articleId) {
    return get(`/articles/${articleId}`)
  },

  /**
   * 获取文章题目列表
   * @param {number} articleId - 文章ID
   * @param {boolean} forWeakPoint - 是否为补弱项模式（只返回弱项相关题目）
   */
  getArticleQuestions(articleId, forWeakPoint = false) {
    return get(`/articles/${articleId}/questions`, { 
      for_weak_point: forWeakPoint 
    })
  },

  /**
   * 获取文章列表
   * @param {object} params - { grade, tag_id, page, page_size }
   */
  getArticleList(params = {}) {
    return get('/articles/', params)
  },

  /**
   * 获取标签列表
   */
  getTags() {
    return get('/tags/')
  },

  /**
   * 获取标签分类
   */
  getTagCategories() {
    return get('/tags/categories')
  },
}

module.exports = articleService
```

---

## 4.1.8 进度服务 (services/progressService.js)

```javascript
const { get, post } = require('../utils/request')

const progressService = {
  /**
   * 开始阅读，创建进度记录
   * @param {number} articleId - 文章ID
   */
  startReading(articleId) {
    return post('/progress/start', { article_id: articleId })
  },

  /**
   * 提交单题答案
   * @param {number} progressId - 进度ID
   * @param {number} questionId - 题目ID
   * @param {string} userAnswer - 用户答案
   */
  submitAnswer(progressId, questionId, userAnswer) {
    return post(`/progress/${progressId}/submit`, {
      question_id: questionId,
      user_answer: userAnswer,
    })
  },

  /**
   * 完成阅读
   * @param {number} progressId - 进度ID
   * @param {number} timeSpent - 花费时间（秒）
   */
  completeReading(progressId, timeSpent) {
    return post(`/progress/${progressId}/complete`, {
      time_spent: timeSpent,
    })
  },

  /**
   * 获取进度详情（含答题记录）
   * @param {number} progressId - 进度ID
   */
  getProgressDetail(progressId) {
    return get(`/progress/${progressId}`)
  },

  /**
   * 获取历史记录列表
   * @param {number} page - 页码
   * @param {number} pageSize - 每页数量
   */
  getHistory(page = 1, pageSize = 20) {
    return get('/progress/history', { 
      page, 
      page_size: pageSize 
    })
  },
}

module.exports = progressService
```

---

## 4.1.9 工具函数 (utils/util.js)

```javascript
/**
 * 格式化日期
 * @param {Date|string|number} date 
 * @param {string} format - 格式 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:mm:ss'
 */
const formatDate = (date, format = 'YYYY-MM-DD') => {
  const d = new Date(date)
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化时间显示（如：5分钟前）
 */
const formatTimeAgo = (date) => {
  const now = Date.now()
  const diff = now - new Date(date).getTime()
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  
  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < 7 * day) {
    return `${Math.floor(diff / day)}天前`
  } else {
    return formatDate(date)
  }
}

/**
 * 年级文案映射
 */
const gradeTextMap = {
  'GRADE_1': '1年级',
  'GRADE_2': '2年级',
  'GRADE_3': '3年级',
  'GRADE_4': '4年级',
  'GRADE_5': '5年级',
  'GRADE_6': '6年级',
}

const getGradeText = (grade) => {
  return gradeTextMap[grade] || '未设置'
}

/**
 * 难度文案映射
 */
const getDifficultyText = (level) => {
  const map = {
    1: '简单',
    2: '中等',
    3: '困难',
  }
  return map[level] || '中等'
}

/**
 * 生成难度星星数组
 * @param {number} level - 1-3
 * @returns {Array} - [true, true, false] 表示 2 星
 */
const getDifficultyStars = (level) => {
  return [1, 2, 3].map(i => i <= level)
}

/**
 * 渐变色背景样式
 * 用于按钮等元素
 */
const gradientStyle = {
  primary: 'linear-gradient(135deg, #F5A623 0%, #E8941C 100%)',
  success: 'linear-gradient(135deg, #52C41A 0%, #389E0D 100%)',
}

/**
 * 节流函数
 */
const throttle = (fn, delay = 300) => {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 防抖函数
 */
const debounce = (fn, delay = 300) => {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

module.exports = {
  formatDate,
  formatTimeAgo,
  getGradeText,
  getDifficultyText,
  getDifficultyStars,
  gradientStyle,
  throttle,
  debounce,
}
```

---

## 4.1.10 存储工具 (utils/storage.js)

```javascript
/**
 * 本地存储封装
 */
const storage = {
  /**
   * 设置存储
   */
  set(key, value) {
    try {
      wx.setStorageSync(key, value)
      return true
    } catch (e) {
      console.error('存储失败:', e)
      return false
    }
  },

  /**
   * 获取存储
   */
  get(key, defaultValue = null) {
    try {
      const value = wx.getStorageSync(key)
      return value !== '' ? value : defaultValue
    } catch (e) {
      console.error('读取存储失败:', e)
      return defaultValue
    }
  },

  /**
   * 删除存储
   */
  remove(key) {
    try {
      wx.removeStorageSync(key)
      return true
    } catch (e) {
      console.error('删除存储失败:', e)
      return false
    }
  },

  /**
   * 清除所有存储
   */
  clear() {
    try {
      wx.clearStorageSync()
      return true
    } catch (e) {
      console.error('清除存储失败:', e)
      return false
    }
  },

  // 常用 Key
  keys: {
    TOKEN: 'token',
    USER_INFO: 'userInfo',
    GRADE: 'selectedGrade',
    LAST_RESULT: 'lastResult',
  }
}

module.exports = storage
```

---

## 4.1.11 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 应用配置 | `miniprogram/app.json` | TabBar 3个，橙黄色系 |
| 应用入口 | `miniprogram/app.js` | 全局状态管理 |
| 主题样式 | `miniprogram/styles/theme.wxss` | 完整设计变量 |
| 全局样式 | `miniprogram/app.wxss` | 引入主题 |
| 网络请求 | `miniprogram/utils/request.js` | 统一错误处理 |
| 用户服务 | `miniprogram/services/userService.js` | API 封装完整 |
| 文章服务 | `miniprogram/services/articleService.js` | API 封装完整 |
| 进度服务 | `miniprogram/services/progressService.js` | API 封装完整 |
| 工具函数 | `miniprogram/utils/util.js` | 常用函数 |
| 存储工具 | `miniprogram/utils/storage.js` | 存储封装 |
