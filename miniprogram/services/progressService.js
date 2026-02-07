const { get, post } = require('../utils/request')

const progressService = {
  
  startReading(articleId) {
    return post('/progress/start', { article_id: articleId })
  },

  
  submitAnswer(progressId, questionId, userAnswer) {
    return post(`/progress/${progressId}/submit`, {
      question_id: questionId,
      user_answer: userAnswer,
    })
  },

  
  completeReading(progressId, timeSpent) {
    return post(`/progress/${progressId}/complete`, {
      time_spent: timeSpent,
    })
  },

  
  getProgressDetail(progressId) {
    return get(`/progress/${progressId}`)
  },

  
  getHistory(page = 1, pageSize = 20) {
    return get('/progress/history', { 
      page, 
      page_size: pageSize 
    })
  },
}

module.exports = progressService
