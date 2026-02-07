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
