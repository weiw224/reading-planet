const app = getApp()
const articleService = require('../../services/articleService')
const progressService = require('../../services/progressService')

Page({
  data: {
    progressId: null,
    articleId: null,
    article: null,
    questions: [],
    currentIndex: 0,
    currentQuestion: null,
    
    selectedAnswer: '',
    connections: [],
    sortedItems: [],
    fillAnswer: '',
    shortAnswer: '',
    
    showResult: false,
    showHintPopup: false,
    showArticlePopup: false,
    submitting: false,
    
    totalScore: 0,
    correctCount: 0,
  },

  computed: {
    progressPercent() {
      if (!this.data.questions.length) return 0
      return ((this.data.currentIndex + 1) / this.data.questions.length) * 100
    },
    canSubmit() {
      if (this.data.showResult) return true
      const q = this.data.currentQuestion
      if (!q) return false
      
      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          return !!this.data.selectedAnswer
        case 'MATCHING':
          return this.data.connections.length > 0
        case 'SORTING':
          return this.data.sortedItems.length > 0
        case 'FILL':
          return !!this.data.fillAnswer.trim()
        case 'SHORT_ANSWER':
          return !!this.data.shortAnswer.trim()
        default:
          return false
      }
    },
    isLastQuestion() {
      return this.data.currentIndex >= this.data.questions.length - 1
    }
  },

  onLoad(options) {
    const { progressId, articleId } = options
    
    if (!progressId || !articleId) {
      wx.showToast({ title: '参数错误', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }

    this.setData({ progressId, articleId })
    this.loadData()
  },

  async loadData() {
    wx.showLoading({ title: '加载中...' })

    try {
      const [article, questions] = await Promise.all([
        articleService.getArticleDetail(this.data.articleId),
        articleService.getArticleQuestions(this.data.articleId),
      ])

      const typeTextMap = {
        'CHOICE': '选择题',
        'JUDGMENT': '判断题',
        'MATCHING': '连线题',
        'SORTING': '排序题',
        'FILL': '填空题',
        'SHORT_ANSWER': '简答题',
      }

      const processedQuestions = questions.map(q => ({
        ...q,
        type_text: typeTextMap[q.type] || '练习题',
      }))

      this.setData({
        article,
        questions: processedQuestions,
        currentQuestion: processedQuestions[0],
      })

      this.updateComputed()

    } catch (error) {
      console.error('加载题目失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  updateComputed() {
    const progressPercent = this.data.questions.length 
      ? ((this.data.currentIndex + 1) / this.data.questions.length) * 100 
      : 0

    let canSubmit = false
    if (this.data.showResult) {
      canSubmit = true
    } else if (this.data.currentQuestion) {
      const q = this.data.currentQuestion
      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          canSubmit = !!this.data.selectedAnswer
          break
        case 'MATCHING':
          canSubmit = this.data.connections.length > 0
          break
        case 'SORTING':
          canSubmit = this.data.sortedItems.length > 0
          break
        case 'FILL':
          canSubmit = !!this.data.fillAnswer.trim()
          break
        case 'SHORT_ANSWER':
          canSubmit = !!this.data.shortAnswer.trim()
          break
      }
    }

    const isLastQuestion = this.data.currentIndex >= this.data.questions.length - 1

    this.setData({ 
      progressPercent, 
      canSubmit,
      isLastQuestion 
    })
  },

  onSelectAnswer(e) {
    if (this.data.showResult) return
    this.setData({ selectedAnswer: e.detail.answer })
    this.updateComputed()
  },

  onConnect(e) {
    if (this.data.showResult) return
    this.setData({ connections: e.detail.connections })
    this.updateComputed()
  },

  onSort(e) {
    if (this.data.showResult) return
    this.setData({ sortedItems: e.detail.items })
    this.updateComputed()
  },

  onFillInput(e) {
    this.setData({ fillAnswer: e.detail.value })
    this.updateComputed()
  },

  onShortAnswerInput(e) {
    this.setData({ shortAnswer: e.detail.value })
    this.updateComputed()
  },

  async handleConfirm() {
    if (this.data.showResult) {
      if (this.data.isLastQuestion) {
        await this.completeQuiz()
      } else {
        this.goToNextQuestion()
      }
    } else {
      await this.submitAnswer()
    }
  },

  async submitAnswer() {
    if (this.data.submitting) return
    this.setData({ submitting: true })

    try {
      const q = this.data.currentQuestion
      let userAnswer = ''

      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          userAnswer = this.data.selectedAnswer
          break
        case 'MATCHING':
          userAnswer = JSON.stringify(this.data.connections)
          break
        case 'SORTING':
          userAnswer = JSON.stringify(this.data.sortedItems)
          break
        case 'FILL':
          userAnswer = this.data.fillAnswer
          break
        case 'SHORT_ANSWER':
          userAnswer = this.data.shortAnswer
          break
      }

      const result = await progressService.submitAnswer(
        this.data.progressId,
        q.id,
        userAnswer
      )

      if (result.is_correct) {
        this.setData({
          totalScore: this.data.totalScore + result.score,
          correctCount: this.data.correctCount + 1,
        })
      }

      this.setData({ 
        showResult: true,
        currentQuestion: {
          ...this.data.currentQuestion,
          userAnswer,
          isCorrect: result.is_correct,
          correctAnswer: result.correct_answer,
          analysis: result.analysis,
        }
      })
      this.updateComputed()

    } catch (error) {
      console.error('提交答案失败:', error)
      wx.showToast({ title: '提交失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  goToNextQuestion() {
    const nextIndex = this.data.currentIndex + 1
    const nextQuestion = this.data.questions[nextIndex]

    this.setData({
      currentIndex: nextIndex,
      currentQuestion: nextQuestion,
      selectedAnswer: '',
      connections: [],
      sortedItems: [],
      fillAnswer: '',
      shortAnswer: '',
      showResult: false,
    })
    this.updateComputed()
  },

  async completeQuiz() {
    wx.showLoading({ title: '计算成绩...' })

    try {
      const startTime = app.globalData.currentProgress?.startTime || Date.now()
      const timeSpent = Math.floor((Date.now() - startTime) / 1000)

      const result = await progressService.completeReading(
        this.data.progressId,
        timeSpent
      )

      app.clearCurrentProgress()

      wx.redirectTo({
        url: `/pages/result/result?progressId=${this.data.progressId}`
      })

    } catch (error) {
      console.error('完成练习失败:', error)
      wx.showToast({ title: '提交失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  showHint() {
    this.setData({ showHintPopup: true })
  },

  closeHint() {
    this.setData({ showHintPopup: false })
  },

  showArticle() {
    this.setData({ showArticlePopup: true })
  },

  closeArticle() {
    this.setData({ showArticlePopup: false })
  },

  handleClose() {
    wx.showModal({
      title: '确认退出',
      content: '退出后当前答题进度将丢失，确定要退出吗？',
      confirmText: '继续答题',
      cancelText: '退出',
      success: (res) => {
        if (res.cancel) {
          app.clearCurrentProgress()
          wx.navigateBack()
        }
      }
    })
  },
})
