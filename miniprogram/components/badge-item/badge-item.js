Component({
  properties: {
    badge: { type: Object, value: {} },
  },

  methods: {
    handleTap() {
      this.triggerEvent('tap', { badge: this.properties.badge })
    }
  }
})
