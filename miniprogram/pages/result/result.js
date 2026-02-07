const app = getApp()
const progressService = require('../../services/progressService')
const articleService = require('../../services/articleService')

Page({
  data: {
    progressId: null,
    progressDetail: null,
    userInfo: null,
    
    starCount: 0,
    accuracy: 0,
    timeSpentText: '',
    encourageText: '',
    
    newBadge: null,
    showBadgePopup: false,
    
    abilityData: [],
  },

  onLoad(options) {
    const { progressId } = options
    if (!progressId) {
      wx.showToast({ title: '数据错误', icon: 'none' })
      setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 1500)
      return
    }

    this.setData({ 
      progressId,
      userInfo: app.globalData.userInfo 
    })
    this.loadResult(progressId)
  },

  async loadResult(progressId) {
    wx.showLoading({ title: '加载中...' })

    try {
      const detail = await progressService.getProgressDetail(progressId)
      
      const accuracy = detail.correct_count / detail.total_questions * 100
      let starCount = 1
      if (accuracy >= 90) starCount = 3
      else if (accuracy >= 70) starCount = 2

      const minutes = Math.floor(detail.time_spent / 60)
      const seconds = detail.time_spent % 60
      const timeSpentText = `${minutes}:${seconds.toString().padStart(2, '0')}`

      const encourageText = this.generateEncourageText(accuracy, detail.streak_days)

      const abilityData = [
        { label: '主旨概括', value: detail.abilities?.summary || 0 },
        { label: '推理判断', value: detail.abilities?.reasoning || 0 },
        { label: '语言运用', value: detail.abilities?.language || 0 },
        { label: '人物分析', value: detail.abilities?.character || 0 },
        { label: '细节观察', value: detail.abilities?.detail || 0 },
      ]

      this.setData({
        progressDetail: detail,
        starCount,
        accuracy: Math.round(accuracy),
        timeSpentText,
        encourageText,
        newBadge: detail.new_badge || null,
        abilityData,
      })

      if (detail.new_badge) {
        setTimeout(() => {
          this.setData({ showBadgePopup: true })
        }, 1000)
      }

    } catch (error) {
      console.error('加载结果失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  generateEncourageText(accuracy, streakDays) {
    if (accuracy >= 90) {
      return '今天的小进步好可爱！继续保持哦～'
    } else if (accuracy >= 70) {
      return '做得不错，再接再厉！'
    } else {
      return '没关系，多读多练就会进步！'
    }
  },

  showBadgeDetail() {
    if (this.data.newBadge) {
      this.setData({ showBadgePopup: true })
    }
  },

  closeBadgePopup() {
    this.setData({ showBadgePopup: false })
  },

  shareBadge() {
    this.setData({ showBadgePopup: false })
  },

  async readAgain() {
    try {
      const article = await articleService.getTodayArticle()
      if (article) {
        wx.redirectTo({
          url: `/pages/article/article?id=${article.id}`
        })
      } else {
        wx.showToast({ 
          title: '今日文章已读完', 
          icon: 'none' 
        })
      }
    } catch (error) {
      wx.showToast({ 
        title: '获取文章失败', 
        icon: 'none' 
      })
    }
  },

  viewBadges() {
    wx.navigateTo({ url: '/pages/badges/badges' })
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  goBack() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  onShareAppMessage() {
    return {
      title: `我在阅读星球完成了今日阅读，正确率${this.data.accuracy}%！`,
      path: '/pages/index/index',
    }
  },
})
