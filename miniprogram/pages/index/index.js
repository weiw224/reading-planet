const app = getApp()
const userService = require('../../services/userService')
const articleService = require('../../services/articleService')

Page({
  data: {
    loading: true,
    refreshing: false,
    userInfo: null,
    notifyCount: 0,
    
    // 统计数据
    stats: {
      badgeCount: 0,
      growthValue: 0,
      streakDays: 0,
      rankPercent: 0,
    },
    
    // 今日推荐
    todayArticle: null,
    
    // 日历数据
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    today: new Date().getDate(),
    checkinDays: [],
    monthProgress: '0/30',
    
    // 激励文案
    motivationTitle: '',
    motivationText: '',
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    // 每次显示时刷新数据
    if (!this.data.loading) {
      this.loadData()
    }
  },

  // 下拉刷新
  async onPullDownRefresh() {
    this.setData({ refreshing: true })
    await this.loadData()
    this.setData({ refreshing: false })
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true })

    try {
      // 并行请求数据
      const [userInfo, stats, todayArticle, checkins] = await Promise.all([
        userService.getCurrentUser(),
        userService.getUserStats(),
        articleService.getTodayArticle().catch(() => null),
        userService.getCheckins(this.data.currentYear, this.data.currentMonth),
      ])

      // 更新用户信息
      app.updateUserInfo(userInfo)

      // 计算月进度
      const totalDays = new Date(
        this.data.currentYear, 
        this.data.currentMonth, 
        0
      ).getDate()
      const checkedDays = checkins.length

      // 生成激励文案
      const motivation = this.generateMotivation(stats.streak_days)

      this.setData({
        userInfo,
        stats: {
          badgeCount: stats.badge_count || 0,
          growthValue: stats.growth_value || 0,
          streakDays: stats.streak_days || 0,
          rankPercent: stats.rank_percent || 0,
        },
        todayArticle,
        checkinDays: checkins.map(c => c.day),
        monthProgress: `${checkedDays}/${totalDays}`,
        motivationTitle: motivation.title,
        motivationText: motivation.text,
        loading: false,
      })

    } catch (error) {
      console.error('加载首页数据失败:', error)
      this.setData({ loading: false })
    }
  },

  // 生成激励文案
  generateMotivation(streakDays) {
    if (streakDays >= 7) {
      return {
        title: '太厉害了！',
        text: `你已经连续阅读${streakDays}天，是阅读小能手！`,
      }
    } else if (streakDays >= 3) {
      return {
        title: '继续保持！',
        text: `再读${7 - streakDays}天即可领取本周"阅读小达人"勋章`,
      }
    } else if (streakDays >= 1) {
      return {
        title: '加油！',
        text: `再读${3 - streakDays}天即可获得"三日小达人"勋章`,
      }
    } else {
      return {
        title: '开始阅读吧！',
        text: '每天阅读一篇，积累成长值，解锁更多勋章',
      }
    }
  },

  // 开始阅读
  startReading(e) {
    const article = e.detail || this.data.todayArticle
    if (!article) return

    wx.navigateTo({
      url: `/pages/article/article?id=${article.id}`
    })
  },

  // 跳转个人中心
  goToProfile() {
    wx.switchTab({ url: '/pages/profile/profile' })
  },

  // 显示通知
  showNotifications() {
    wx.showToast({
      title: '暂无新通知',
      icon: 'none'
    })
  },

  // 显示月份选择
  showMonthPicker() {
    // 可以实现月份选择器
    wx.showToast({
      title: '查看历史月份',
      icon: 'none'
    })
  },
})
