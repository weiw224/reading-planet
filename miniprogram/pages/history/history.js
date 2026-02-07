const progressService = require('../../services/progressService')

Page({
  data: {
    historyList: [],
    page: 1,
    pageSize: 10,
    loading: false,
    hasMore: true,
  },

  onLoad() {
    this.loadHistory()
  },

  onShow() {
    if (this.data.page === 1) {
      this.loadHistory()
    }
  },

  async loadHistory() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    try {
      const result = await progressService.getHistory(this.data.page, this.data.pageSize)
      
      const historyList = result.items.map(item => ({
        ...item,
        date_text: this.formatDate(item.completed_at),
        tags: item.article_tags || [],
      }))

      this.setData({
        historyList: this.data.page === 1 ? historyList : [...this.data.historyList, ...historyList],
        hasMore: historyList.length >= this.data.pageSize,
        loading: false,
      })
    } catch (error) {
      console.error('加载历史记录失败:', error)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  loadMore() {
    if (!this.data.loading && this.data.hasMore) {
      this.setData({ page: this.data.page + 1 }, () => {
        this.loadHistory()
      })
    }
  },

  formatDate(dateStr) {
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}`
  },

  viewDetail(e) {
    const progressId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/result/result?progressId=${progressId}&readonly=1`
    })
  },

  goBack() {
    wx.navigateBack()
  },

  goReading() {
    wx.switchTab({ url: '/pages/index/index' })
  },
})
