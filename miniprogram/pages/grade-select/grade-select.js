const app = getApp()
const userService = require('../../services/userService')

Page({
  data: {
    loading: false,
    selectedGrade: '',
    gradeList: [
      { value: 'GRADE_1', name: '一年级', icon: '/images/icons/grade-1.png' },
      { value: 'GRADE_2', name: '二年级', icon: '/images/icons/grade-2.png' },
      { value: 'GRADE_3', name: '三年级', icon: '/images/icons/grade-3.png' },
      { value: 'GRADE_4', name: '四年级', icon: '/images/icons/grade-4.png' },
      { value: 'GRADE_5', name: '五年级', icon: '/images/icons/grade-5.png' },
      { value: 'GRADE_6', name: '六年级', icon: '/images/icons/grade-6.png' },
    ],
  },

  // 选择年级
  selectGrade(e) {
    const grade = e.currentTarget.dataset.grade
    this.setData({ selectedGrade: grade })
  },

  // 确认年级
  async confirmGrade() {
    if (!this.data.selectedGrade || this.data.loading) return

    this.setData({ loading: true })

    try {
      // 更新用户年级
      await userService.updateUser({
        grade: this.data.selectedGrade
      })

      // 更新本地用户信息
      const userInfo = app.globalData.userInfo || {}
      userInfo.grade = this.data.selectedGrade
      app.updateUserInfo(userInfo)

      // 提示成功
      wx.showToast({
        title: '设置成功',
        icon: 'success'
      })

      // 跳转首页
      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' })
      }, 1000)

    } catch (error) {
      console.error('设置年级失败:', error)
      wx.showToast({
        title: '设置失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },
})
