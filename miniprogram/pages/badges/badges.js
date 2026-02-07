const userService = require('../../services/userService')

Page({
  data: {
    unlockedBadges: [],
    lockedBadges: [],
    unlockedCount: 0,
    lockedCount: 0,
  },

  onLoad() {
    this.loadBadges()
  },

  async loadBadges() {
    try {
      const badges = await userService.getBadges()
      
      const unlockedBadges = badges.filter(b => b.is_unlocked)
      const lockedBadges = badges.filter(b => !b.is_unlocked)
      
      this.setData({
        unlockedBadges,
        lockedBadges,
        unlockedCount: unlockedBadges.length,
        lockedCount: lockedBadges.length,
      })
    } catch (error) {
      console.error('加载勋章失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  goBack() {
    wx.navigateBack()
  },

  showBadgeDetail(e) {
    const badge = e.currentTarget.dataset.badge
    wx.showModal({
      title: badge.name,
      content: `${badge.description}\n获得日期：${badge.unlocked_at || ''}`,
      showCancel: false,
    })
  },

  showLockCondition(e) {
    const badge = e.currentTarget.dataset.badge
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
  },
})
