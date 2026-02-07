const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hour = d.getHours()
  const minute = d.getMinutes()
  const second = d.getSeconds()

  return format.replace('YYYY', year)
    .replace('MM', formatNumber(month))
    .replace('DD', formatNumber(day))
    .replace('HH', formatNumber(hour))
    .replace('mm', formatNumber(minute))
    .replace('ss', formatNumber(second))
}

const formatTimeAgo = (date) => {
  if (!date) return ''
  
  const now = Date.now()
  const time = new Date(date).getTime()
  const diff = now - time

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const month = 30 * day
  const year = 12 * month

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return Math.floor(diff / minute) + '分钟前'
  } else if (diff < day) {
    return Math.floor(diff / hour) + '小时前'
  } else if (diff < month) {
    return Math.floor(diff / day) + '天前'
  } else if (diff < year) {
    return Math.floor(diff / month) + '个月前'
  } else {
    return Math.floor(diff / year) + '年前'
  }
}

const getGradeText = (grade) => {
  const gradeMap = {
    'GRADE_1': '1年级',
    'GRADE_2': '2年级',
    'GRADE_3': '3年级',
    'GRADE_4': '4年级',
    'GRADE_5': '5年级',
    'GRADE_6': '6年级'
  }
  return gradeMap[grade] || grade
}

const getDifficultyText = (level) => {
  const difficultyMap = {
    1: '简单',
    2: '中等',
    3: '困难'
  }
  return difficultyMap[level] || '未知'
}

const getDifficultyStars = (level) => {
  const stars = []
  for (let i = 1; i <= 3; i++) {
    stars.push(i <= level)
  }
  return stars
}

const gradientStyle = {
  primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  success: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
  warning: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  danger: 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
  info: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  gold: 'linear-gradient(135deg, #f5af19 0%, #f12711 100%)',
  blue: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  purple: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}

const throttle = (fn, delay) => {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

const debounce = (fn, delay) => {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

module.exports = {
  formatDate,
  formatTimeAgo,
  getGradeText,
  getDifficultyText,
  getDifficultyStars,
  gradientStyle,
  throttle,
  debounce
}
