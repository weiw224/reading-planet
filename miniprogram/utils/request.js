const app = getApp()


const request = (options) => {
  return new Promise((resolve, reject) => {
    const { 
      url, 
      method = 'GET', 
      data, 
      showLoading = true,
      loadingText = '加载中...',
      showError = true 
    } = options
    
    if (showLoading) {
      wx.showLoading({ 
        title: loadingText, 
        mask: true 
      })
    }
    
    const header = {
      'Content-Type': 'application/json',
    }
    
    if (app.globalData.token) {
      header['Authorization'] = `Bearer ${app.globalData.token}`
    }
    
    const fullUrl = url.startsWith('http') 
      ? url 
      : app.globalData.apiBaseUrl + url
    
    wx.request({
      url: fullUrl,
      method,
      data,
      header,
      success: (res) => {
        if (showLoading) {
          wx.hideLoading()
        }
        
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data.data)
          } else {
            const errorMsg = res.data.message || '请求失败'
            if (showError) {
              wx.showToast({ 
                title: errorMsg, 
                icon: 'none',
                duration: 2000
              })
            }
            reject({ code: res.data.code, message: errorMsg })
          }
        } else if (res.statusCode === 401) {
          app.clearLoginInfo()
          wx.showToast({ 
            title: '登录已过期，请重新登录', 
            icon: 'none' 
          })
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/login/login' })
          }, 1500)
          reject({ code: 401, message: '登录已过期' })
        } else if (res.statusCode === 404) {
          if (showError) {
            wx.showToast({ title: '资源不存在', icon: 'none' })
          }
          reject({ code: 404, message: '资源不存在' })
        } else {
          if (showError) {
            wx.showToast({ title: '服务器错误', icon: 'none' })
          }
          reject({ code: res.statusCode, message: '服务器错误' })
        }
      },
      fail: (err) => {
        if (showLoading) {
          wx.hideLoading()
        }
        if (showError) {
          wx.showToast({ 
            title: '网络连接失败，请检查网络', 
            icon: 'none',
            duration: 2000
          })
        }
        reject({ code: -1, message: '网络连接失败', error: err })
      }
    })
  })
}


const get = (url, data, options = {}) => {
  return request({ url, method: 'GET', data, ...options })
}


const post = (url, data, options = {}) => {
  return request({ url, method: 'POST', data, ...options })
}


const put = (url, data, options = {}) => {
  return request({ url, method: 'PUT', data, ...options })
}


const del = (url, data, options = {}) => {
  return request({ url, method: 'DELETE', data, ...options })
}

module.exports = {
  request,
  get,
  post,
  put,
  del
}
