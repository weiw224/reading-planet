Component({
  properties: {
    article: { type: Object, value: {} },
    showBadge: { type: Boolean, value: false },
    badgeText: { type: String, value: '今日推荐' },
  },

  methods: {
    handleTap() {
      this.triggerEvent('tap', { article: this.properties.article })
    },
    
    handleStart() {
      this.triggerEvent('start', { article: this.properties.article })
    }
  }
})
