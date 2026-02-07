const keys = {
  TOKEN: 'token',
  USER_INFO: 'userInfo',
  GRADE: 'grade',
  LAST_RESULT: 'lastResult'
}

const set = (key, value) => {
  try {
    wx.setStorageSync(key, JSON.stringify(value))
    return true
  } catch (e) {
    console.error('Storage set error:', e)
    return false
  }
}

const get = (key, defaultValue = null) => {
  try {
    const value = wx.getStorageSync(key)
    if (!value) return defaultValue
    return JSON.parse(value)
  } catch (e) {
    console.error('Storage get error:', e)
    return defaultValue
  }
}

const remove = (key) => {
  try {
    wx.removeStorageSync(key)
    return true
  } catch (e) {
    console.error('Storage remove error:', e)
    return false
  }
}

const clear = () => {
  try {
    wx.clearStorageSync()
    return true
  } catch (e) {
    console.error('Storage clear error:', e)
    return false
  }
}

module.exports = {
  keys,
  set,
  get,
  remove,
  clear
}
