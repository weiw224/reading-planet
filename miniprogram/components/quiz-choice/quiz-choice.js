Component({
  properties: {
    question: { type: Object, value: {} },
    selectedAnswer: { type: String, value: '' },
    showResult: { type: Boolean, value: false },
    isJudgment: { type: Boolean, value: false },
  },

  data: {
    options: [],
  },

  observers: {
    'question, isJudgment': function(question, isJudgment) {
      if (isJudgment) {
        this.setData({
          options: [
            { key: 'A', text: '正确' },
            { key: 'B', text: '错误' },
          ]
        })
      } else if (question.options) {
        const options = Object.entries(question.options).map(([key, text]) => ({
          key, text
        }))
        this.setData({ options })
      }
    }
  },

  methods: {
    selectOption(e) {
      if (this.properties.showResult) return
      
      const key = e.currentTarget.dataset.key
      this.triggerEvent('select', { answer: key })
    }
  }
})
