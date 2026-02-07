Component({
  properties: {
    data: { type: Array, value: [] },
    size: { type: Number, value: 400 },
  },

  data: {
    ctx: null,
    canvasWidth: 0,
    canvasHeight: 0,
  },

  observers: {
    'data': function(data) {
      if (data && data.length > 0) {
        this.drawRadar()
      }
    }
  },

  lifetimes: {
    attached() {
      this.initCanvas()
    }
  },

  methods: {
    initCanvas() {
      const query = this.createSelectorQuery()
      query.select('#radarCanvas')
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res[0]) return
          
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          
          const dpr = wx.getSystemInfoSync().pixelRatio
          canvas.width = res[0].width * dpr
          canvas.height = res[0].height * dpr
          ctx.scale(dpr, dpr)
          
          this.setData({
            ctx,
            canvasWidth: res[0].width,
            canvasHeight: res[0].height,
          })
          
          this.drawRadar()
        })
    },

    drawRadar() {
      const { ctx, canvasWidth, canvasHeight, data } = this.data
      if (!ctx || !data || data.length === 0) return

      const centerX = canvasWidth / 2
      const centerY = canvasHeight / 2
      const radius = Math.min(centerX, centerY) * 0.7
      const count = data.length
      const angleStep = (Math.PI * 2) / count

      ctx.clearRect(0, 0, canvasWidth, canvasHeight)

      ctx.strokeStyle = '#e0e0e0'
      ctx.lineWidth = 1
      
      for (let level = 1; level <= 5; level++) {
        const r = (radius / 5) * level
        ctx.beginPath()
        for (let i = 0; i <= count; i++) {
          const angle = i * angleStep - Math.PI / 2
          const x = centerX + r * Math.cos(angle)
          const y = centerY + r * Math.sin(angle)
          if (i === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        }
        ctx.closePath()
        ctx.stroke()
      }

      for (let i = 0; i < count; i++) {
        const angle = i * angleStep - Math.PI / 2
        ctx.beginPath()
        ctx.moveTo(centerX, centerY)
        ctx.lineTo(
          centerX + radius * Math.cos(angle),
          centerY + radius * Math.sin(angle)
        )
        ctx.stroke()
      }

      ctx.fillStyle = 'rgba(245, 166, 35, 0.3)'
      ctx.strokeStyle = '#F5A623'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      data.forEach((item, i) => {
        const angle = i * angleStep - Math.PI / 2
        const value = Math.min(item.value / 100, 1)
        const x = centerX + radius * value * Math.cos(angle)
        const y = centerY + radius * value * Math.sin(angle)
        
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      ctx.fillStyle = '#666'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      data.forEach((item, i) => {
        const angle = i * angleStep - Math.PI / 2
        const labelRadius = radius + 20
        const x = centerX + labelRadius * Math.cos(angle)
        const y = centerY + labelRadius * Math.sin(angle)
        ctx.fillText(item.label, x, y)
      })
    }
  }
})
