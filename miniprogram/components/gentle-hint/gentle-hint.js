Component({
  properties: {
    hint: { type: String, value: '' },
    images: { type: Array, value: [] },
  },

  methods: {
    close() {
      this.triggerEvent('close')
    },
    
    preventClose() {
      
    }
  }
})
