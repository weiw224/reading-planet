const { get } = require('../utils/request')

const articleService = {
  
  getTodayArticle() {
    return get('/articles/today')
  },

  
  getWeakPointArticle() {
    return get('/articles/weak-point')
  },

  
  getArticleDetail(articleId) {
    return get(`/articles/${articleId}`)
  },

  
  getArticleQuestions(articleId, forWeakPoint = false) {
    return get(`/articles/${articleId}/questions`, { 
      for_weak_point: forWeakPoint 
    })
  },

  
  getArticleList(params = {}) {
    return get('/articles/', params)
  },

  
  getTags() {
    return get('/tags/')
  },

  
  getTagCategories() {
    return get('/tags/categories')
  },
}

module.exports = articleService
