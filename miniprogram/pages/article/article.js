const app = getApp()
const articleService = require('../../services/articleService')
const progressService = require('../../services/progressService')

Page({
  data: {
    articleId: null,
    article: null,
    paragraphs: [],
    loading: true,
    starting: false,
  },

  onLoad(options) {
    const articleId = options.id
    if (!articleId) {
      wx.showToast({ title: '文章不存在', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }

    this.setData({ articleId })
    this.loadArticle(articleId)
  },

  async loadArticle(articleId) {
    this.setData({ loading: true })

    try {
      const article = await articleService.getArticleDetail(articleId)
      
      const paragraphs = this.parseParagraphs(article.content)
      
      const gradeTextMap = {
        'GRADE_1': '1年级', 'GRADE_2': '2年级', 'GRADE_3': '3年级',
        'GRADE_4': '4年级', 'GRADE_5': '5年级', 'GRADE_6': '6年级',
      }

      this.setData({
        article: {
          ...article,
          grade_text: gradeTextMap[article.grade] || article.grade,
          estimated_time: Math.ceil(article.word_count / 100),
          has_challenge: article.difficulty >= 3,
        },
        paragraphs,
        loading: false,
      })

      wx.setNavigationBarTitle({ title: article.title })

    } catch (error) {
      console.error('加载文章失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ loading: false })
    }
  },

  parseParagraphs(content) {
    if (!content) return []
    
    const lines = content.split('\n').filter(line => line.trim())
    
    return lines.map(line => {
      const highlightMatch = line.match(/^【(.+)】$/)
      if (highlightMatch) {
        return {
          text: highlightMatch[1],
          isHighlight: true
        }
      }
      return {
        text: line,
        isHighlight: false
      }
    })
  },

  async startQuiz() {
    if (this.data.starting) return

    this.setData({ starting: true })

    try {
      const progress = await progressService.startReading(this.data.articleId)
      
      app.setCurrentProgress(progress.id, this.data.articleId)

      wx.navigateTo({
        url: `/pages/quiz/quiz?progressId=${progress.id}&articleId=${this.data.articleId}`
      })

    } catch (error) {
      console.error('开始答题失败:', error)
      wx.showToast({ title: '开始答题失败', icon: 'none' })
    } finally {
      this.setData({ starting: false })
    }
  },

  goBack() {
    wx.navigateBack()
  },

  viewFullImage() {
    if (this.data.article?.cover_url) {
      wx.previewImage({
        urls: [this.data.article.cover_url]
      })
    }
  },

  showMore() {
    wx.showActionSheet({
      itemList: ['分享给朋友', '收藏文章', '举报问题'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            break
          case 1:
            wx.showToast({ title: '已收藏', icon: 'success' })
            break
          case 2:
            wx.showToast({ title: '感谢反馈', icon: 'none' })
            break
        }
      }
    })
  },

  onShareAppMessage() {
    return {
      title: this.data.article?.title || '阅读星球',
      path: `/pages/article/article?id=${this.data.articleId}`,
      imageUrl: this.data.article?.cover_url
    }
  },
})
