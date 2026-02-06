# Phase 4.2d: 微信小程序 - 答题页

> **前置依赖**: Phase 4.1, Phase 4.2c  
> **本文件范围**: 答题页（多种题型）  
> **参考原型**: `interactive_quiz_question_*`, `互动练习题_*`, `温柔提示引导图卡`

---

## 4.2d.1 页面配置 (quiz.json)

```json
{
  "navigationBarTitleText": "互动练习题",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black",
  "usingComponents": {
    "quiz-choice": "/components/quiz-choice/quiz-choice",
    "quiz-matching": "/components/quiz-matching/quiz-matching",
    "quiz-sorting": "/components/quiz-sorting/quiz-sorting",
    "quiz-fill": "/components/quiz-fill/quiz-fill",
    "gentle-hint": "/components/gentle-hint/gentle-hint",
    "article-popup": "/components/article-popup/article-popup"
  }
}
```

---

## 4.2d.2 页面结构 (quiz.wxml)

```xml
<!-- 答题页 - 参考原型: interactive_quiz_question -->
<view class="page-quiz">
  <!-- 顶部导航 -->
  <view class="nav-bar">
    <view class="nav-left" bindtap="handleClose">
      <image src="/images/icons/close.png" mode="aspectFit" />
    </view>
    
    <view class="nav-center">
      <text class="quiz-title">{{currentQuestion.type_text}}</text>
    </view>
    
    <view class="nav-right">
      <!-- 火焰积分 -->
      <view class="score-badge">
        <image src="/images/icons/fire.png" mode="aspectFit" />
        <text>{{totalScore}}</text>
      </view>
    </view>
  </view>

  <!-- 进度条区域 -->
  <view class="progress-section">
    <text class="progress-text">第 {{currentIndex + 1}} / {{questions.length}} 题</text>
    
    <!-- 猫头鹰引导角色 -->
    <view class="mascot-owl">
      <image src="/images/mascots/owl.png" mode="aspectFit" />
    </view>
    
    <!-- 进度条 -->
    <view class="progress-bar">
      <view 
        class="progress-fill" 
        style="width: {{progressPercent}}%"
      ></view>
      <view 
        class="progress-pending" 
        style="width: {{100 - progressPercent}}%"
      ></view>
    </view>
  </view>

  <!-- 题目内容区 -->
  <view class="question-content">
    <!-- 选择题 -->
    <quiz-choice
      wx:if="{{currentQuestion.type === 'CHOICE'}}"
      question="{{currentQuestion}}"
      selected-answer="{{selectedAnswer}}"
      show-result="{{showResult}}"
      bind:select="onSelectAnswer"
    />

    <!-- 判断题 -->
    <quiz-choice
      wx:if="{{currentQuestion.type === 'JUDGMENT'}}"
      question="{{currentQuestion}}"
      selected-answer="{{selectedAnswer}}"
      show-result="{{showResult}}"
      is-judgment="{{true}}"
      bind:select="onSelectAnswer"
    />

    <!-- 连线题 -->
    <quiz-matching
      wx:if="{{currentQuestion.type === 'MATCHING'}}"
      question="{{currentQuestion}}"
      connections="{{connections}}"
      show-result="{{showResult}}"
      bind:connect="onConnect"
    />

    <!-- 排序题 -->
    <quiz-sorting
      wx:if="{{currentQuestion.type === 'SORTING'}}"
      question="{{currentQuestion}}"
      sorted-items="{{sortedItems}}"
      show-result="{{showResult}}"
      bind:sort="onSort"
    />

    <!-- 填空题 -->
    <quiz-fill
      wx:if="{{currentQuestion.type === 'FILL'}}"
      question="{{currentQuestion}}"
      fill-answer="{{fillAnswer}}"
      show-result="{{showResult}}"
      bind:input="onFillInput"
    />

    <!-- 简答题 -->
    <view class="short-answer" wx:if="{{currentQuestion.type === 'SHORT_ANSWER'}}">
      <view class="question-text">{{currentQuestion.content}}</view>
      <textarea 
        class="answer-input"
        placeholder="请输入你的答案..."
        value="{{shortAnswer}}"
        bindinput="onShortAnswerInput"
        maxlength="500"
        disabled="{{showResult}}"
      />
      <view class="char-count">{{shortAnswer.length}}/500</view>
    </view>
  </view>

  <!-- 底部操作栏 -->
  <view class="bottom-bar safe-area-bottom">
    <!-- 温柔提示按钮 -->
    <view class="btn-hint" bindtap="showHint">
      <image src="/images/icons/hint-bulb.png" mode="aspectFit" />
      <text>温柔提示</text>
    </view>

    <!-- 查看原文按钮 -->
    <view class="btn-article" bindtap="showArticle">
      <image src="/images/icons/book-open.png" mode="aspectFit" />
      <text>查看原文</text>
    </view>

    <!-- 确认/下一题按钮 -->
    <button 
      class="btn-confirm {{canSubmit ? '' : 'disabled'}}"
      bindtap="handleConfirm"
      disabled="{{!canSubmit}}"
      loading="{{submitting}}"
    >
      <text>{{showResult ? (isLastQuestion ? '完成练习' : '下一题') : '确认答案'}}</text>
      <image 
        wx:if="{{showResult && !isLastQuestion}}"
        src="/images/icons/arrow-right-white.png" 
        mode="aspectFit" 
      />
    </button>
  </view>

  <!-- 温柔提示弹窗 -->
  <gentle-hint
    wx:if="{{showHintPopup}}"
    hint="{{currentQuestion.hint}}"
    images="{{currentQuestion.hint_images}}"
    bind:close="closeHint"
  />

  <!-- 查看原文弹窗 -->
  <article-popup
    wx:if="{{showArticlePopup}}"
    article="{{article}}"
    highlight-text="{{currentQuestion.excerpt}}"
    bind:close="closeArticle"
  />
</view>
```

---

## 4.2d.3 页面样式 (quiz.wxss)

```css
/* 答题页样式 - 橙黄暖色调 */
.page-quiz {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFFBF0 0%, #FFF8E7 100%);
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  padding-top: calc(20rpx + var(--status-bar-height, 44px));
}

.nav-left, .nav-right {
  width: 100rpx;
}

.nav-left {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.nav-left image {
  width: 56rpx;
  height: 56rpx;
  padding: 8rpx;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.nav-center {
  flex: 1;
  text-align: center;
}

.quiz-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

.nav-right {
  display: flex;
  justify-content: flex-end;
}

.score-badge {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.score-badge image {
  width: 36rpx;
  height: 36rpx;
  margin-right: 8rpx;
}

.score-badge text {
  font-size: 28rpx;
  font-weight: 600;
  color: #F5A623;
}

/* 进度区域 */
.progress-section {
  padding: 20rpx 30rpx;
  position: relative;
}

.progress-text {
  font-size: 26rpx;
  color: #888;
}

.mascot-owl {
  position: absolute;
  right: 30rpx;
  top: 0;
  width: 80rpx;
  height: 80rpx;
}

.mascot-owl image {
  width: 100%;
  height: 100%;
}

/* 进度条 */
.progress-bar {
  display: flex;
  height: 12rpx;
  border-radius: 6rpx;
  overflow: hidden;
  margin-top: 16rpx;
}

.progress-fill {
  background: linear-gradient(90deg, #F5A623 0%, #FFB84D 100%);
  border-radius: 6rpx;
  transition: width 0.3s ease;
}

.progress-pending {
  background: #FEE4B3;
}

/* 题目内容区 */
.question-content {
  flex: 1;
  padding: 20rpx 30rpx;
  overflow-y: auto;
}

/* 简答题 */
.short-answer {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.question-text {
  font-size: 34rpx;
  font-weight: 500;
  color: #333;
  line-height: 1.6;
  margin-bottom: 30rpx;
}

.answer-input {
  width: 100%;
  height: 300rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
  padding: 20rpx;
  font-size: 30rpx;
  line-height: 1.6;
  box-sizing: border-box;
}

.char-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  margin-top: 12rpx;
}

/* 底部操作栏 */
.bottom-bar {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx 30rpx;
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  gap: 20rpx;
}

.btn-hint, .btn-article {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12rpx 16rpx;
}

.btn-hint image, .btn-article image {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 4rpx;
}

.btn-hint text, .btn-article text {
  font-size: 20rpx;
  color: #666;
}

.btn-confirm {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  background: #F5A623;
  border-radius: 44rpx;
  border: none;
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.btn-confirm::after {
  border: none;
}

.btn-confirm.disabled {
  background: #ccc;
}

.btn-confirm image {
  width: 32rpx;
  height: 32rpx;
  margin-left: 8rpx;
}

/* 答案反馈样式 */
.answer-feedback {
  margin-top: 30rpx;
  padding: 24rpx;
  border-radius: 16rpx;
}

.answer-feedback.correct {
  background: rgba(82, 196, 26, 0.1);
  border: 2rpx solid #52C41A;
}

.answer-feedback.wrong {
  background: rgba(255, 77, 79, 0.1);
  border: 2rpx solid #FF4D4F;
}

.feedback-title {
  display: flex;
  align-items: center;
  font-size: 30rpx;
  font-weight: 600;
  margin-bottom: 12rpx;
}

.feedback-title.correct {
  color: #52C41A;
}

.feedback-title.wrong {
  color: #FF4D4F;
}

.feedback-title image {
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
}

.feedback-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}
```

---

## 4.2d.4 页面逻辑 (quiz.js)

```javascript
const app = getApp()
const articleService = require('../../services/articleService')
const progressService = require('../../services/progressService')

Page({
  data: {
    progressId: null,
    articleId: null,
    article: null,
    questions: [],
    currentIndex: 0,
    currentQuestion: null,
    
    // 答案状态
    selectedAnswer: '',      // 选择题答案
    connections: [],         // 连线题连接
    sortedItems: [],         // 排序题顺序
    fillAnswer: '',          // 填空题答案
    shortAnswer: '',         // 简答题答案
    
    // UI 状态
    showResult: false,
    showHintPopup: false,
    showArticlePopup: false,
    submitting: false,
    
    // 统计
    totalScore: 0,
    correctCount: 0,
  },

  // 计算属性
  computed: {
    progressPercent() {
      if (!this.data.questions.length) return 0
      return ((this.data.currentIndex + 1) / this.data.questions.length) * 100
    },
    canSubmit() {
      if (this.data.showResult) return true
      const q = this.data.currentQuestion
      if (!q) return false
      
      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          return !!this.data.selectedAnswer
        case 'MATCHING':
          return this.data.connections.length > 0
        case 'SORTING':
          return this.data.sortedItems.length > 0
        case 'FILL':
          return !!this.data.fillAnswer.trim()
        case 'SHORT_ANSWER':
          return !!this.data.shortAnswer.trim()
        default:
          return false
      }
    },
    isLastQuestion() {
      return this.data.currentIndex >= this.data.questions.length - 1
    }
  },

  onLoad(options) {
    const { progressId, articleId } = options
    
    if (!progressId || !articleId) {
      wx.showToast({ title: '参数错误', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }

    this.setData({ progressId, articleId })
    this.loadData()
  },

  // 加载数据
  async loadData() {
    wx.showLoading({ title: '加载中...' })

    try {
      const [article, questions] = await Promise.all([
        articleService.getArticleDetail(this.data.articleId),
        articleService.getArticleQuestions(this.data.articleId),
      ])

      // 题型文案映射
      const typeTextMap = {
        'CHOICE': '选择题',
        'JUDGMENT': '判断题',
        'MATCHING': '连线题',
        'SORTING': '排序题',
        'FILL': '填空题',
        'SHORT_ANSWER': '简答题',
      }

      // 处理题目
      const processedQuestions = questions.map(q => ({
        ...q,
        type_text: typeTextMap[q.type] || '练习题',
      }))

      this.setData({
        article,
        questions: processedQuestions,
        currentQuestion: processedQuestions[0],
      })

      this.updateComputed()

    } catch (error) {
      console.error('加载题目失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  // 更新计算属性
  updateComputed() {
    const progressPercent = this.data.questions.length 
      ? ((this.data.currentIndex + 1) / this.data.questions.length) * 100 
      : 0

    let canSubmit = false
    if (this.data.showResult) {
      canSubmit = true
    } else if (this.data.currentQuestion) {
      const q = this.data.currentQuestion
      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          canSubmit = !!this.data.selectedAnswer
          break
        case 'MATCHING':
          canSubmit = this.data.connections.length > 0
          break
        case 'SORTING':
          canSubmit = this.data.sortedItems.length > 0
          break
        case 'FILL':
          canSubmit = !!this.data.fillAnswer.trim()
          break
        case 'SHORT_ANSWER':
          canSubmit = !!this.data.shortAnswer.trim()
          break
      }
    }

    const isLastQuestion = this.data.currentIndex >= this.data.questions.length - 1

    this.setData({ 
      progressPercent, 
      canSubmit,
      isLastQuestion 
    })
  },

  // 选择答案（选择题/判断题）
  onSelectAnswer(e) {
    if (this.data.showResult) return
    this.setData({ selectedAnswer: e.detail.answer })
    this.updateComputed()
  },

  // 连线（连线题）
  onConnect(e) {
    if (this.data.showResult) return
    this.setData({ connections: e.detail.connections })
    this.updateComputed()
  },

  // 排序（排序题）
  onSort(e) {
    if (this.data.showResult) return
    this.setData({ sortedItems: e.detail.items })
    this.updateComputed()
  },

  // 填空输入
  onFillInput(e) {
    this.setData({ fillAnswer: e.detail.value })
    this.updateComputed()
  },

  // 简答输入
  onShortAnswerInput(e) {
    this.setData({ shortAnswer: e.detail.value })
    this.updateComputed()
  },

  // 确认答案 / 下一题
  async handleConfirm() {
    if (this.data.showResult) {
      // 已显示结果，进入下一题或完成
      if (this.data.isLastQuestion) {
        await this.completeQuiz()
      } else {
        this.goToNextQuestion()
      }
    } else {
      // 提交答案
      await this.submitAnswer()
    }
  },

  // 提交答案
  async submitAnswer() {
    if (this.data.submitting) return
    this.setData({ submitting: true })

    try {
      const q = this.data.currentQuestion
      let userAnswer = ''

      switch (q.type) {
        case 'CHOICE':
        case 'JUDGMENT':
          userAnswer = this.data.selectedAnswer
          break
        case 'MATCHING':
          userAnswer = JSON.stringify(this.data.connections)
          break
        case 'SORTING':
          userAnswer = JSON.stringify(this.data.sortedItems)
          break
        case 'FILL':
          userAnswer = this.data.fillAnswer
          break
        case 'SHORT_ANSWER':
          userAnswer = this.data.shortAnswer
          break
      }

      // 调用后端提交
      const result = await progressService.submitAnswer(
        this.data.progressId,
        q.id,
        userAnswer
      )

      // 更新得分
      if (result.is_correct) {
        this.setData({
          totalScore: this.data.totalScore + result.score,
          correctCount: this.data.correctCount + 1,
        })
      }

      // 显示结果
      this.setData({ 
        showResult: true,
        currentQuestion: {
          ...this.data.currentQuestion,
          userAnswer,
          isCorrect: result.is_correct,
          correctAnswer: result.correct_answer,
          analysis: result.analysis,
        }
      })
      this.updateComputed()

    } catch (error) {
      console.error('提交答案失败:', error)
      wx.showToast({ title: '提交失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  // 下一题
  goToNextQuestion() {
    const nextIndex = this.data.currentIndex + 1
    const nextQuestion = this.data.questions[nextIndex]

    this.setData({
      currentIndex: nextIndex,
      currentQuestion: nextQuestion,
      selectedAnswer: '',
      connections: [],
      sortedItems: [],
      fillAnswer: '',
      shortAnswer: '',
      showResult: false,
    })
    this.updateComputed()
  },

  // 完成练习
  async completeQuiz() {
    wx.showLoading({ title: '计算成绩...' })

    try {
      // 计算用时
      const startTime = app.globalData.currentProgress?.startTime || Date.now()
      const timeSpent = Math.floor((Date.now() - startTime) / 1000)

      // 调用完成接口
      const result = await progressService.completeReading(
        this.data.progressId,
        timeSpent
      )

      // 清除当前进度
      app.clearCurrentProgress()

      // 跳转结果页
      wx.redirectTo({
        url: `/pages/result/result?progressId=${this.data.progressId}`
      })

    } catch (error) {
      console.error('完成练习失败:', error)
      wx.showToast({ title: '提交失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  // 显示温柔提示
  showHint() {
    this.setData({ showHintPopup: true })
  },

  // 关闭温柔提示
  closeHint() {
    this.setData({ showHintPopup: false })
  },

  // 显示原文
  showArticle() {
    this.setData({ showArticlePopup: true })
  },

  // 关闭原文
  closeArticle() {
    this.setData({ showArticlePopup: false })
  },

  // 关闭/退出
  handleClose() {
    wx.showModal({
      title: '确认退出',
      content: '退出后当前答题进度将丢失，确定要退出吗？',
      confirmText: '继续答题',
      cancelText: '退出',
      success: (res) => {
        if (res.cancel) {
          app.clearCurrentProgress()
          wx.navigateBack()
        }
      }
    })
  },
})
```

---

## 4.2d.5 验收标准

### 视觉验收

- [ ] 顶部显示题型文字和火焰积分
- [ ] 进度条显示正确，有猫头鹰引导角色
- [ ] 选择题选项样式正确（圆形字母标识）
- [ ] 选中状态为黄色高亮
- [ ] 底部有温柔提示、查看原文、确认答案三个按钮
- [ ] 答案反馈显示正确/错误状态

### 功能验收

- [ ] 选择题选择后可确认
- [ ] 提交答案调用后端接口
- [ ] 显示答案解析
- [ ] 下一题正确切换
- [ ] 温柔提示弹窗正常显示
- [ ] 查看原文弹窗正常显示
- [ ] 最后一题完成后跳转结果页

---

## 4.2d.6 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 答题页配置 | `pages/quiz/quiz.json` |
| 答题页结构 | `pages/quiz/quiz.wxml` |
| 答题页样式 | `pages/quiz/quiz.wxss` |
| 答题页逻辑 | `pages/quiz/quiz.js` |
