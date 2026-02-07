const app = getApp()
const userService = require('../../services/userService')

Page({
  data: {
    loading: false,
    agreed: false,
  },

  onLoad() {
    // 如果已登录，直接跳转
    if (app.globalData.isLoggedIn) {
      this.navigateToHome()
    }
  },

  // 勾选协议
  onAgreementChange(e) {
    this.setData({
      agreed: e.detail.value.includes('agree')
    })
  },

  // 微信登录
  async handleLogin() {
    // 检查是否同意协议
    if (!this.data.agreed) {
      wx.showToast({
        title: '请先阅读并同意用户协议',
        icon: 'none'
      })
      return
    }

    if (this.data.loading) return
    
    this.setData({ loading: true })

    try {
      // 1. 获取微信登录 code
      const loginRes = await wx.login()
      const code = loginRes.code

      if (!code) {
        throw new Error('获取登录凭证失败')
      }

      // 2. 调用后端登录接口
      const result = await userService.wechatLogin(code)

      // 3. 保存登录信息
      app.setLoginInfo(result.access_token, {})

      // 4. 获取用户详细信息
      const userInfo = await userService.getCurrentUser()
      app.updateUserInfo(userInfo)

      // 5. 判断是否需要选择年级
      if (result.is_new_user || !userInfo.grade) {
        wx.redirectTo({ 
          url: '/pages/grade-select/grade-select' 
        })
      } else {
        this.navigateToHome()
      }

    } catch (error) {
      console.error('登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 跳转首页
  navigateToHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  // 查看用户协议
  viewUserAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '用户协议内容...',
      showCancel: false
    })
  },

  // 查看隐私政策
  viewPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '隐私政策内容...',
      showCancel: false
    })
  },

  // 显示帮助
  showHelp() {
    wx.showModal({
      title: '帮助',
      content: '如有问题，请联系客服',
      showCancel: false
    })
  },
})
