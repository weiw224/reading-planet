const { get, post, put } = require('../utils/request')

const userService = {
  
  wechatLogin(code) {
    return post('/auth/wechat-login', { code })
  },

  
  getCurrentUser() {
    return get('/users/me')
  },

  
  updateUser(data) {
    return put('/users/me', data)
  },

  
  getUserStats() {
    return get('/users/me/stats')
  },

  
  getAbilityRadar() {
    return get('/users/me/abilities')
  },

  
  getCheckins(year, month) {
    return get('/users/me/checkins', { year, month })
  },

  
  getBadges() {
    return get('/users/me/badges')
  },

  
  getBadgeDetail(badgeId) {
    return get(`/users/me/badges/${badgeId}`)
  },
}

module.exports = userService
