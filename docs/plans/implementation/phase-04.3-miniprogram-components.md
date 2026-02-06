# Phase 4.3: 微信小程序 - 自定义组件库

> **前置依赖**: Phase 4.1  
> **本文件范围**: 可复用的自定义组件

---

## 4.3.1 组件索引

| 组件 | 用途 | 使用页面 |
|-----|------|---------|
| `today-stats` | 今日成就统计卡片 | 首页 |
| `calendar` | 日历打卡组件 | 首页 |
| `article-card` | 文章推荐卡片 | 首页、练习页 |
| `quiz-choice` | 选择题/判断题组件 | 答题页 |
| `gentle-hint` | 温柔提示弹窗 | 答题页 |
| `article-popup` | 查看原文弹窗 | 答题页 |
| `radar-chart` | 能力雷达图 | 结果页、个人中心 |
| `badge-item` | 勋章展示项 | 个人中心 |
| `badge-popup` | 勋章详情弹窗 | 结果页 |

---

## 4.3.2 今日成就统计 (today-stats)

### 组件配置 (today-stats.json)

```json
{
  "component": true
}
```

### 组件结构 (today-stats.wxml)

```xml
<!-- 今日成就统计卡片 - 参考原型首页顶部 -->
<view class="today-stats">
  <view class="stats-header">
    <text class="title">今日成就</text>
    <view class="rank-badge" wx:if="{{rankPercent > 0}}">
      <text>已超越 {{rankPercent}}% 同学</text>
    </view>
  </view>
  
  <view class="stats-grid">
    <!-- 勋章数 -->
    <view class="stat-item">
      <view class="stat-icon badge">
        <image src="/images/icons/trophy.png" mode="aspectFit" />
      </view>
      <text class="stat-value">{{badgeCount}}</text>
      <text class="stat-label">获得勋章</text>
    </view>
    
    <!-- 成长值 -->
    <view class="stat-item">
      <view class="stat-icon growth">
        <image src="/images/icons/sparkle.png" mode="aspectFit" />
      </view>
      <text class="stat-value">{{growthValue}}</text>
      <text class="stat-label">成长值</text>
    </view>
    
    <!-- 连续天数 -->
    <view class="stat-item">
      <view class="stat-icon streak">
        <image src="/images/icons/fire.png" mode="aspectFit" />
      </view>
      <text class="stat-value">{{streakDays}}</text>
      <text class="stat-label">连续天数</text>
    </view>
  </view>
</view>
```

### 组件样式 (today-stats.wxss)

```css
.today-stats {
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%);
  border-radius: 24rpx;
  padding: 30rpx;
}

.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.stats-header .title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.rank-badge {
  background: linear-gradient(90deg, #F5A623 0%, #FFB84D 100%);
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.rank-badge text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 500;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  background: #fff;
  padding: 24rpx 16rpx;
  border-radius: 16rpx;
  margin: 0 8rpx;
}

.stat-icon {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 12rpx;
}

.stat-icon image {
  width: 100%;
  height: 100%;
}

.stat-value {
  font-size: 44rpx;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 22rpx;
  color: #888;
  margin-top: 4rpx;
}
```

### 组件逻辑 (today-stats.js)

```javascript
Component({
  properties: {
    badgeCount: { type: Number, value: 0 },
    growthValue: { type: Number, value: 0 },
    streakDays: { type: Number, value: 0 },
    rankPercent: { type: Number, value: 0 },
  },
})
```

---

## 4.3.3 日历打卡组件 (calendar)

### 组件结构 (calendar.wxml)

```xml
<!-- 日历打卡组件 -->
<view class="calendar">
  <!-- 星期标题 -->
  <view class="weekdays">
    <text wx:for="{{weekdays}}" wx:key="*this">{{item}}</text>
  </view>
  
  <!-- 日期网格 -->
  <view class="days-grid">
    <view 
      class="day-item {{item.isToday ? 'today' : ''}} {{item.isChecked ? 'checked' : ''}} {{item.isFuture ? 'future' : ''}} {{item.isEmpty ? 'empty' : ''}}"
      wx:for="{{daysArray}}"
      wx:key="index"
    >
      <block wx:if="{{!item.isEmpty}}">
        <!-- 已打卡 -->
        <view class="check-circle" wx:if="{{item.isChecked}}">
          <image src="/images/icons/check.png" mode="aspectFit" />
        </view>
        
        <!-- 今天 -->
        <view class="today-circle" wx:elif="{{item.isToday}}">
          <text>{{item.day}}</text>
        </view>
        
        <!-- 未来日期（锁定） -->
        <view class="future-icon" wx:elif="{{item.isFuture}}">
          <image src="/images/icons/lock-small.png" mode="aspectFit" />
        </view>
        
        <!-- 过去未打卡 -->
        <text class="day-text" wx:else>{{item.day}}</text>
      </block>
      
      <!-- 日期数字（底部） -->
      <text class="day-number" wx:if="{{!item.isEmpty}}">{{item.day}}</text>
    </view>
  </view>
</view>
```

### 组件样式 (calendar.wxss)

```css
.calendar {
  background: #fff;
  border-radius: 20rpx;
  padding: 20rpx;
}

.weekdays {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16rpx;
}

.weekdays text {
  width: 80rpx;
  text-align: center;
  font-size: 24rpx;
  color: #888;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8rpx;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80rpx;
  position: relative;
}

.day-item.empty {
  visibility: hidden;
}

/* 已打卡样式 */
.check-circle {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #52C41A 0%, #389E0D 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-circle image {
  width: 28rpx;
  height: 28rpx;
}

/* 今天样式 */
.today-circle {
  width: 56rpx;
  height: 56rpx;
  border: 3rpx dashed #F5A623;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.today-circle text {
  font-size: 28rpx;
  font-weight: 600;
  color: #F5A623;
}

/* 未来日期（锁定） */
.future-icon {
  width: 56rpx;
  height: 56rpx;
  background: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.future-icon image {
  width: 28rpx;
  height: 28rpx;
  opacity: 0.5;
}

/* 普通日期 */
.day-text {
  font-size: 28rpx;
  color: #666;
}

/* 日期数字（已打卡时显示在下方） */
.day-number {
  position: absolute;
  bottom: 0;
  font-size: 18rpx;
  color: #999;
}

.day-item.checked .day-number {
  display: none;
}
```

### 组件逻辑 (calendar.js)

```javascript
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
      
      // 获取本月第一天是星期几（0=周日）
      const firstDay = new Date(year, month - 1, 1).getDay()
      // 转换为周一开始（0=周一）
      const startOffset = firstDay === 0 ? 6 : firstDay - 1
      
      // 获取本月天数
      const daysInMonth = new Date(year, month, 0).getDate()
      
      // 当前日期信息
      const currentYear = new Date().getFullYear()
      const currentMonth = new Date().getMonth() + 1
      const isCurrentMonth = year === currentYear && month === currentMonth
      
      const daysArray = []
      
      // 填充前面的空白
      for (let i = 0; i < startOffset; i++) {
        daysArray.push({ isEmpty: true })
      }
      
      // 填充日期
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
```

---

## 4.3.4 文章推荐卡片 (article-card)

### 组件结构 (article-card.wxml)

```xml
<!-- 文章推荐卡片 -->
<view class="article-card" bindtap="handleTap">
  <!-- 封面图 -->
  <view class="cover-wrapper">
    <image class="cover" src="{{article.cover_url}}" mode="aspectFill" />
    <view class="badge" wx:if="{{showBadge}}">
      <text>{{badgeText}}</text>
    </view>
  </view>
  
  <!-- 内容区 -->
  <view class="content">
    <text class="title">《{{article.title}}》</text>
    <view class="meta">
      <text class="grade">{{article.grade_text}}</text>
      <text class="dot">·</text>
      <text class="word-count">{{article.word_count}}字</text>
      <text class="dot">·</text>
      <text class="time">{{article.estimated_time}}分钟</text>
    </view>
    <view class="stars">
      <image 
        wx:for="{{[1,2,3,4,5]}}" 
        wx:key="*this"
        src="{{item <= article.rating ? '/images/icons/star-filled-small.png' : '/images/icons/star-empty-small.png'}}"
        mode="aspectFit"
      />
    </view>
  </view>
  
  <!-- 开始按钮 -->
  <button class="btn-start" catchtap="handleStart">开始练习</button>
</view>
```

### 组件样式 (article-card.wxss)

```css
.article-card {
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.cover-wrapper {
  position: relative;
  width: 100%;
  height: 300rpx;
}

.cover {
  width: 100%;
  height: 100%;
}

.badge {
  position: absolute;
  left: 20rpx;
  bottom: 20rpx;
  background: #FF6B35;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.badge text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 500;
}

.content {
  padding: 24rpx 30rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.meta {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #F5A623;
  margin-bottom: 12rpx;
}

.dot {
  margin: 0 8rpx;
  color: #ddd;
}

.stars {
  display: flex;
  gap: 4rpx;
}

.stars image {
  width: 28rpx;
  height: 28rpx;
}

.btn-start {
  margin: 0 30rpx 24rpx;
  height: 80rpx;
  background: rgba(245, 166, 35, 0.15);
  border: none;
  border-radius: 40rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: #F5A623;
}

.btn-start::after {
  border: none;
}
```

### 组件逻辑 (article-card.js)

```javascript
Component({
  properties: {
    article: { type: Object, value: {} },
    showBadge: { type: Boolean, value: false },
    badgeText: { type: String, value: '今日推荐' },
  },

  methods: {
    handleTap() {
      this.triggerEvent('tap', { article: this.properties.article })
    },
    
    handleStart() {
      this.triggerEvent('start', { article: this.properties.article })
    }
  }
})
```

---

## 4.3.5 选择题组件 (quiz-choice)

### 组件结构 (quiz-choice.wxml)

```xml
<!-- 选择题/判断题组件 -->
<view class="quiz-choice">
  <!-- 题目卡片 -->
  <view class="question-card">
    <text class="question-text">{{question.content}}</text>
    
    <!-- 题目配图 -->
    <image 
      wx:if="{{question.image_url}}" 
      class="question-image"
      src="{{question.image_url}}" 
      mode="aspectFit"
    />
  </view>

  <!-- 选项列表 -->
  <view class="options-list">
    <view 
      class="option-item {{item.key === selectedAnswer ? 'selected' : ''}} {{showResult ? (item.key === question.correct_answer ? 'correct' : (item.key === selectedAnswer ? 'wrong' : '')) : ''}}"
      wx:for="{{options}}"
      wx:key="key"
      bindtap="selectOption"
      data-key="{{item.key}}"
    >
      <view class="option-letter {{item.key === selectedAnswer ? 'selected' : ''}}">
        <text>{{item.key}}</text>
      </view>
      <text class="option-text">{{item.text}}</text>
      
      <!-- 正确/错误图标 -->
      <image 
        wx:if="{{showResult && item.key === question.correct_answer}}"
        class="result-icon"
        src="/images/icons/check-circle-green.png" 
        mode="aspectFit"
      />
      <image 
        wx:if="{{showResult && item.key === selectedAnswer && item.key !== question.correct_answer}}"
        class="result-icon"
        src="/images/icons/close-circle-red.png" 
        mode="aspectFit"
      />
    </view>
  </view>

  <!-- 答案反馈 -->
  <view class="feedback {{question.isCorrect ? 'correct' : 'wrong'}}" wx:if="{{showResult}}">
    <view class="feedback-header">
      <image src="{{question.isCorrect ? '/images/icons/check-circle-green.png' : '/images/icons/close-circle-red.png'}}" mode="aspectFit" />
      <text>{{question.isCorrect ? '回答正确！' : '回答错误'}}</text>
    </view>
    <text class="feedback-analysis" wx:if="{{question.analysis}}">{{question.analysis}}</text>
  </view>
</view>
```

### 组件样式 (quiz-choice.wxss)

```css
.quiz-choice {
  padding: 0;
}

.question-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.question-text {
  font-size: 34rpx;
  font-weight: 500;
  color: #333;
  line-height: 1.6;
}

.question-image {
  width: 100%;
  max-height: 400rpx;
  margin-top: 24rpx;
  border-radius: 16rpx;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.option-item {
  display: flex;
  align-items: center;
  background: #fff;
  border: 3rpx solid #eee;
  border-radius: 50rpx;
  padding: 24rpx 30rpx;
  transition: all 0.2s ease;
}

.option-item.selected {
  border-color: #F5A623;
  background: #FFFBF5;
}

.option-item.correct {
  border-color: #52C41A;
  background: #F6FFED;
}

.option-item.wrong {
  border-color: #FF4D4F;
  background: #FFF2F0;
}

.option-letter {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.option-letter.selected {
  background: #F5A623;
}

.option-letter text {
  font-size: 28rpx;
  font-weight: 600;
  color: #666;
}

.option-letter.selected text {
  color: #fff;
}

.option-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.result-icon {
  width: 44rpx;
  height: 44rpx;
  margin-left: 16rpx;
}

.feedback {
  margin-top: 30rpx;
  padding: 24rpx;
  border-radius: 16rpx;
}

.feedback.correct {
  background: #F6FFED;
  border: 2rpx solid #52C41A;
}

.feedback.wrong {
  background: #FFF2F0;
  border: 2rpx solid #FF4D4F;
}

.feedback-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.feedback-header image {
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
}

.feedback-header text {
  font-size: 30rpx;
  font-weight: 600;
}

.feedback.correct .feedback-header text {
  color: #52C41A;
}

.feedback.wrong .feedback-header text {
  color: #FF4D4F;
}

.feedback-analysis {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}
```

### 组件逻辑 (quiz-choice.js)

```javascript
Component({
  properties: {
    question: { type: Object, value: {} },
    selectedAnswer: { type: String, value: '' },
    showResult: { type: Boolean, value: false },
    isJudgment: { type: Boolean, value: false },
  },

  data: {
    options: [],
  },

  observers: {
    'question, isJudgment': function(question, isJudgment) {
      if (isJudgment) {
        this.setData({
          options: [
            { key: 'A', text: '正确' },
            { key: 'B', text: '错误' },
          ]
        })
      } else if (question.options) {
        // 解析选项
        const options = Object.entries(question.options).map(([key, text]) => ({
          key, text
        }))
        this.setData({ options })
      }
    }
  },

  methods: {
    selectOption(e) {
      if (this.properties.showResult) return
      
      const key = e.currentTarget.dataset.key
      this.triggerEvent('select', { answer: key })
    }
  }
})
```

---

## 4.3.6 温柔提示弹窗 (gentle-hint)

### 组件结构 (gentle-hint.wxml)

```xml
<!-- 温柔提示弹窗 - 参考原型: 温柔提示引导图卡 -->
<view class="gentle-hint-mask" catchtap="close">
  <view class="gentle-hint-popup" catchtap="preventClose">
    <!-- 拖动条 -->
    <view class="drag-bar"></view>
    
    <!-- 关闭按钮 -->
    <view class="close-btn" bindtap="close">
      <image src="/images/icons/close.png" mode="aspectFit" />
    </view>
    
    <!-- 标题 -->
    <text class="popup-title">温柔提示</text>
    
    <!-- 提示图片 -->
    <view class="hint-images" wx:if="{{images.length > 0}}">
      <view class="image-item" wx:for="{{images}}" wx:key="index">
        <image src="{{item.url}}" mode="aspectFill" />
        <text class="image-caption">{{item.caption}}</text>
      </view>
    </view>
    
    <!-- 提示文字 -->
    <view class="hint-text-wrapper">
      <view class="hint-icon">
        <image src="/images/icons/sparkle-orange.png" mode="aspectFit" />
      </view>
      <text class="hint-text">{{hint}}</text>
    </view>
    
    <!-- 确认按钮 -->
    <button class="btn-confirm" bindtap="close">我明白了</button>
  </view>
</view>
```

### 组件样式 (gentle-hint.wxss)

```css
.gentle-hint-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 1000;
}

.gentle-hint-popup {
  width: 100%;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 30rpx 40rpx 60rpx;
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
}

.drag-bar {
  width: 80rpx;
  height: 8rpx;
  background: #ddd;
  border-radius: 4rpx;
  margin: 0 auto 30rpx;
}

.close-btn {
  position: absolute;
  top: 30rpx;
  right: 30rpx;
  width: 60rpx;
  height: 60rpx;
  background: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn image {
  width: 28rpx;
  height: 28rpx;
}

.popup-title {
  text-align: center;
  font-size: 36rpx;
  font-weight: 700;
  color: #F5A623;
  margin-bottom: 30rpx;
  display: block;
}

.hint-images {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.image-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-item image {
  width: 100%;
  height: 200rpx;
  border-radius: 16rpx;
}

.image-caption {
  font-size: 24rpx;
  color: #F5A623;
  margin-top: 12rpx;
  text-align: center;
}

.hint-text-wrapper {
  background: #FFF9EE;
  border-radius: 16rpx;
  padding: 24rpx 30rpx;
  display: flex;
  align-items: flex-start;
  margin-bottom: 30rpx;
}

.hint-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.hint-icon image {
  width: 100%;
  height: 100%;
}

.hint-text {
  font-size: 30rpx;
  color: #666;
  line-height: 1.6;
}

.btn-confirm {
  width: 100%;
  height: 96rpx;
  background: #F5A623;
  border-radius: 48rpx;
  border: none;
  font-size: 34rpx;
  font-weight: 600;
  color: #fff;
}

.btn-confirm::after {
  border: none;
}
```

### 组件逻辑 (gentle-hint.js)

```javascript
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
      // 阻止冒泡
    }
  }
})
```

---

## 4.3.7 能力雷达图 (radar-chart)

### 组件结构 (radar-chart.wxml)

```xml
<!-- 能力雷达图 -->
<canvas 
  type="2d" 
  id="radarCanvas" 
  class="radar-canvas"
  style="width: {{size}}rpx; height: {{size}}rpx;"
></canvas>
```

### 组件样式 (radar-chart.wxss)

```css
.radar-canvas {
  display: block;
}
```

### 组件逻辑 (radar-chart.js)

```javascript
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

      // 清除画布
      ctx.clearRect(0, 0, canvasWidth, canvasHeight)

      // 绘制背景网格
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

      // 绘制轴线
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

      // 绘制数据区域
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

      // 绘制标签
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
```

---

## 4.3.8 验收标准

### 每个组件

- [ ] 组件独立可复用
- [ ] 属性和事件定义完整
- [ ] 样式与原型一致
- [ ] 在各页面中正常工作

---

## 4.3.9 交付物清单

| 组件 | 文件路径 |
|------|----------|
| 今日成就 | `components/today-stats/*` |
| 日历 | `components/calendar/*` |
| 文章卡片 | `components/article-card/*` |
| 选择题 | `components/quiz-choice/*` |
| 温柔提示 | `components/gentle-hint/*` |
| 能力雷达图 | `components/radar-chart/*` |
| 勋章项 | `components/badge-item/*` |
| 勋章弹窗 | `components/badge-popup/*` |
| 原文弹窗 | `components/article-popup/*` |
