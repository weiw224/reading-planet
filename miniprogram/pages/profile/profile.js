const app = getApp()
const userService = require('../../services/userService')
const progressService = require('../../services/progressService')

Page({
  data: {
    userInfo: null,
    userLevel: 1,
    userTitle: '初级小学者',
    
    stats: {
      streakDays: 0,
      totalReadings: 0,
      badgeCount: 0,
    },
    
    badges: [],
    abilityData: [],
    recentHistory: [],
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  async loadData() {
    try {
      const [userInfo, stats, badges, abilities, history] = await Promise.all([
        userService.getCurrentUser(),
        userService.getUserStats(),
        userService.getBadges(),
        userService.getAbilityRadar(),
        progressService.getHistory(1, 5),
      ])

      const { level, title } = this.calculateLevelAndTitle(stats.growth_value)

      const displayBadges = badges.slice(0, 6)

      const abilityData = [
        { label: '细节提取', value: abilities.detail || 0 },
        { label: '中心思想', value: abilities.summary || 0 },
        { label: '词语运用', value: abilities.language || 0 },
        { label: '逻辑推理', value: abilities.reasoning || 0 },
        { label: '人物分析', value: abilities.character || 0 },
      ]

      const recentHistory = history.items.map(item => ({
        ...item,
        date: this.formatDate(item.completed_at),
        time_text: `${Math.floor(item.time_spent / 60)}分钟`,
        has_badge: !!item.badge_earned,
      }))

      this.setData({
        userInfo,
        userLevel: level,
        userTitle: title,
        stats: {
          streakDays: stats.streak_days || 0,
          totalReadings: stats.total_readings || 0,
          badgeCount: stats.badge_count || 0,
        },
        badges: displayBadges,
        abilityData,
        recentHistory,
      })

      app.updateUserInfo(userInfo)

    } catch (error) {
      console.error('加载个人中心数据失败:', error)
    }
  },

  calculateLevelAndTitle(growthValue) {
    const level = Math.floor((growthValue || 0) / 50) + 1
    
    const titles = {
      1: '初级小学者',
      5: '阅读新秀',
      10: '阅读达人',
      15: '阅读高手',
      20: '阅读大师',
      30: '阅读之星',
    }

    let title = '初级小学者'
    for (const [minLevel, t] of Object.entries(titles).reverse()) {
      if (level >= parseInt(minLevel)) {
        title = t
        break
      }
    }

    return { level: Math.min(level, 99), title }
  },

  formatDate(dateStr) {
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}-${day.toString().padStart(2, '0')}`
  },

  editProfile() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },

  viewAllBadges() {
    wx.navigateTo({ url: '/pages/badges/badges' })
  },

  onBadgeTap(e) {
    const badge = e.detail.badge
    if (badge.is_unlocked) {
      wx.showModal({
        title: badge.name,
        content: `${badge.description}\n获得日期：${badge.unlocked_at || ''}`,
        showCancel: false,
      })
    } else {
      wx.showModal({
        title: badge.name,
        content: `解锁条件：${badge.unlock_condition}`,
        confirmText: '去完成',
        success: (res) => {
          if (res.confirm) {
            wx.switchTab({ url: '/pages/index/index' })
          }
        }
      })
    }
  },

  async goWeakPoint() {
    try {
      const article = await require('../../services/articleService').getWeakPointArticle()
      if (article) {
        wx.navigateTo({
          url: `/pages/article/article?id=${article.id}&mode=weak`
        })
      } else {
        wx.showToast({ title: '暂无推荐', icon: 'none' })
      }
    } catch (error) {
      wx.showToast({ title: '获取推荐失败', icon: 'none' })
    }
  },

  viewAllHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  viewHistoryDetail(e) {
    const progressId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/result/result?progressId=${progressId}&readonly=1`
    })
  },

  openSettings() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },

  showNotifications() {
    wx.showToast({ title: '暂无通知', icon: 'none' })
  },
})
