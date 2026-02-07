Component({
  properties: {
    year: { type: Number, value: new Date().getFullYear() },
    month: { type: Number, value: new Date().getMonth() + 1 },
    checkinDays: { type: Array, value: [] },
    today: { type: Number, value: new Date().getDate() },
  },

  data: {
    weekdays: ['周一', '周二', '周三', '周四', '周五', '周六'],
    daysArray: [],
  },

  observers: {
    'year, month, checkinDays, today': function() {
      this.generateDays()
    }
  },

  lifetimes: {
    attached() {
      this.generateDays()
    }
  },

  methods: {
    generateDays() {
      const { year, month, checkinDays, today } = this.properties
      
      const firstDay = new Date(year, month - 1, 1).getDay()
      const startOffset = firstDay === 0 ? 6 : firstDay - 1
      
      const daysInMonth = new Date(year, month, 0).getDate()
      
      const currentYear = new Date().getFullYear()
      const currentMonth = new Date().getMonth() + 1
      const isCurrentMonth = year === currentYear && month === currentMonth
      
      const daysArray = []
      
      for (let i = 0; i < startOffset; i++) {
        daysArray.push({ isEmpty: true })
      }
      
      for (let day = 1; day <= daysInMonth; day++) {
        daysArray.push({
          day,
          isEmpty: false,
          isToday: isCurrentMonth && day === today,
          isChecked: checkinDays.includes(day),
          isFuture: isCurrentMonth && day > today,
        })
      }
      
      this.setData({ daysArray })
    }
  }
})
