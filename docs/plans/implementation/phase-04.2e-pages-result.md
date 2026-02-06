# Phase 4.2e: 微信小程序 - 结果页

> **前置依赖**: Phase 4.1, Phase 4.2d  
> **本文件范围**: 练习结果页  
> **参考原型**: `practice_results_&_badge_unlock`

---

## 4.2e.1 页面配置 (result.json)

```json
{
  "navigationBarTitleText": "完成练习",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black",
  "usingComponents": {
    "radar-chart": "/components/radar-chart/radar-chart",
    "badge-popup": "/components/badge-popup/badge-popup"
  }
}
```

---

## 4.2e.2 页面结构 (result.wxml)

```xml
<!-- 结果页 - 参考原型: practice_results_&_badge_unlock -->
<view class="page-result">
  <!-- 顶部导航 -->
  <view class="nav-bar">
    <view class="nav-left" bindtap="goBack">
      <image src="/images/icons/arrow-left.png" mode="aspectFit" />
    </view>
    <text class="nav-title">完成练习</text>
    <view class="nav-right"></view>
  </view>

  <!-- 主内容区 -->
  <scroll-view class="main-content" scroll-y enhanced show-scrollbar="{{false}}">
    <!-- 成绩展示 -->
    <view class="score-section">
      <text class="congrats-text">太棒了！</text>
      
      <!-- 星星评级 -->
      <view class="stars-rating">
        <image 
          wx:for="{{[1,2,3]}}" 
          wx:key="*this"
          src="{{item <= starCount ? '/images/icons/star-filled.png' : '/images/icons/star-empty.png'}}"
          mode="aspectFit"
          class="star-icon {{item <= starCount ? 'active' : ''}}"
        />
      </view>

      <!-- 鼓励语 -->
      <view class="encourage-card">
        <image class="avatar" src="{{userInfo.avatar_url || '/images/default-avatar.png'}}" mode="aspectFill" />
        <text class="encourage-text">{{encourageText}}</text>
      </view>
    </view>

    <!-- 勋章解锁 -->
    <view class="badge-section" wx:if="{{newBadge}}">
      <view class="badge-card" bindtap="showBadgeDetail">
        <view class="badge-glow"></view>
        <view class="badge-icon-wrapper">
          <image class="badge-icon" src="{{newBadge.icon_url}}" mode="aspectFit" />
        </view>
        <view class="badge-info">
          <text class="unlock-label">解锁新勋章！</text>
          <text class="badge-name">{{newBadge.name}}</text>
          <text class="badge-desc">{{newBadge.description}}</text>
        </view>
        <view class="sparkles">
          <image src="/images/icons/sparkle.png" mode="aspectFit" />
        </view>
      </view>
    </view>

    <!-- 用时与正确率 -->
    <view class="stats-section">
      <view class="stat-item">
        <image src="/images/icons/clock.png" mode="aspectFit" />
        <text class="stat-label">用时对比</text>
        <text class="stat-value">{{timeSpentText}}</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <image src="/images/icons/target.png" mode="aspectFit" />
        <text class="stat-label">正确率</text>
        <text class="stat-value">{{accuracy}}%</text>
      </view>
    </view>

    <!-- 能力分布 -->
    <view class="ability-section">
      <text class="section-title">能力分布</text>
      <view class="radar-wrapper">
        <radar-chart 
          data="{{abilityData}}"
          size="{{400}}"
        />
      </view>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </scroll-view>

  <!-- 底部操作栏 -->
  <view class="bottom-bar safe-area-bottom">
    <button class="btn-again" bindtap="readAgain">
      <image src="/images/icons/refresh.png" mode="aspectFit" />
      <text>再来一篇</text>
    </button>
    
    <view class="secondary-actions">
      <view class="action-item" bindtap="viewBadges">
        <image src="/images/icons/badge.png" mode="aspectFit" />
        <text>查看勋章收藏</text>
      </view>
      <view class="action-item" bindtap="goHome">
        <text>今天到此为止</text>
      </view>
    </view>
  </view>

  <!-- 勋章详情弹窗 -->
  <badge-popup
    wx:if="{{showBadgePopup}}"
    badge="{{newBadge}}"
    bind:close="closeBadgePopup"
    bind:share="shareBadge"
  />
</view>
```

---

## 4.2e.3 页面样式 (result.wxss)

```css
/* 结果页样式 - 橙黄暖色调 */
.page-result {
  min-height: 100vh;
  background: var(--bg-page);
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
  width: 72rpx;
  height: 72rpx;
}

.nav-left {
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-left image {
  width: 44rpx;
  height: 44rpx;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 0 30rpx;
}

/* 成绩展示 */
.score-section {
  text-align: center;
  padding: 40rpx 0;
}

.congrats-text {
  font-size: 52rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 30rpx;
}

/* 星星评级 */
.stars-rating {
  display: flex;
  justify-content: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.star-icon {
  width: 80rpx;
  height: 80rpx;
  transition: transform 0.3s ease;
}

.star-icon.active {
  animation: starPop 0.5s ease forwards;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* 鼓励卡片 */
.encourage-card {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 24rpx 30rpx;
  border-radius: 50rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
  margin: 0 20rpx;
}

.encourage-card .avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.encourage-text {
  font-size: 28rpx;
  color: #666;
  flex: 1;
}

/* 勋章解锁 */
.badge-section {
  margin: 30rpx 0;
}

.badge-card {
  position: relative;
  background: linear-gradient(135deg, #FFF9EE 0%, #FFF5E0 100%);
  border: 2rpx dashed #F5A623;
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.badge-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300rpx;
  height: 300rpx;
  background: radial-gradient(circle, rgba(245, 166, 35, 0.2) 0%, transparent 70%);
}

.badge-icon-wrapper {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #F5A623 0%, #FFB84D 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
  flex-shrink: 0;
  box-shadow: 0 8rpx 24rpx rgba(245, 166, 35, 0.3);
}

.badge-icon {
  width: 64rpx;
  height: 64rpx;
}

.badge-info {
  flex: 1;
}

.unlock-label {
  display: block;
  font-size: 24rpx;
  color: #F5A623;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.badge-name {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 8rpx;
}

.badge-desc {
  display: block;
  font-size: 24rpx;
  color: #888;
}

.sparkles {
  position: absolute;
  top: 20rpx;
  right: 30rpx;
}

.sparkles image {
  width: 48rpx;
  height: 48rpx;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 用时与正确率 */
.stats-section {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin: 30rpx 0;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-item image {
  width: 40rpx;
  height: 40rpx;
  margin-bottom: 12rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #888;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 44rpx;
  font-weight: 700;
  color: #333;
}

.stat-divider {
  width: 2rpx;
  height: 80rpx;
  background: #f0f0f0;
}

/* 能力分布 */
.ability-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.radar-wrapper {
  display: flex;
  justify-content: center;
  padding: 20rpx 0;
}

/* 底部占位 */
.bottom-placeholder {
  height: 280rpx;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx 30rpx 30rpx;
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.btn-again {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 96rpx;
  background: #F5A623;
  border-radius: 48rpx;
  border: none;
  font-size: 34rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20rpx;
}

.btn-again::after {
  border: none;
}

.btn-again image {
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
}

.secondary-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40rpx;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  border: 2rpx solid #F5A623;
  border-radius: 40rpx;
  background: #fff;
}

.action-item image {
  width: 32rpx;
  height: 32rpx;
  margin-right: 8rpx;
}

.action-item text {
  font-size: 26rpx;
  color: #F5A623;
}

.action-item:last-child {
  border-color: #ddd;
}

.action-item:last-child text {
  color: #888;
}
```

---

## 4.2e.4 页面逻辑 (result.js)

```javascript
const app = getApp()
const progressService = require('../../services/progressService')
const articleService = require('../../services/articleService')

Page({
  data: {
    progressId: null,
    progressDetail: null,
    userInfo: null,
    
    // 成绩数据
    starCount: 0,
    accuracy: 0,
    timeSpentText: '',
    encourageText: '',
    
    // 勋章
    newBadge: null,
    showBadgePopup: false,
    
    // 能力雷达图
    abilityData: [],
  },

  onLoad(options) {
    const { progressId } = options
    if (!progressId) {
      wx.showToast({ title: '数据错误', icon: 'none' })
      setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 1500)
      return
    }

    this.setData({ 
      progressId,
      userInfo: app.globalData.userInfo 
    })
    this.loadResult(progressId)
  },

  // 加载结果
  async loadResult(progressId) {
    wx.showLoading({ title: '加载中...' })

    try {
      const detail = await progressService.getProgressDetail(progressId)
      
      // 计算星级（基于正确率）
      const accuracy = detail.correct_count / detail.total_questions * 100
      let starCount = 1
      if (accuracy >= 90) starCount = 3
      else if (accuracy >= 70) starCount = 2

      // 格式化用时
      const minutes = Math.floor(detail.time_spent / 60)
      const seconds = detail.time_spent % 60
      const timeSpentText = `${minutes}:${seconds.toString().padStart(2, '0')}`

      // 生成鼓励语
      const encourageText = this.generateEncourageText(accuracy, detail.streak_days)

      // 能力数据
      const abilityData = [
        { label: '主旨概括', value: detail.abilities?.summary || 0 },
        { label: '推理判断', value: detail.abilities?.reasoning || 0 },
        { label: '语言运用', value: detail.abilities?.language || 0 },
        { label: '人物分析', value: detail.abilities?.character || 0 },
        { label: '细节观察', value: detail.abilities?.detail || 0 },
      ]

      this.setData({
        progressDetail: detail,
        starCount,
        accuracy: Math.round(accuracy),
        timeSpentText,
        encourageText,
        newBadge: detail.new_badge || null,
        abilityData,
      })

      // 如果有新勋章，延迟显示弹窗
      if (detail.new_badge) {
        setTimeout(() => {
          this.setData({ showBadgePopup: true })
        }, 1000)
      }

    } catch (error) {
      console.error('加载结果失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  // 生成鼓励语
  generateEncourageText(accuracy, streakDays) {
    if (accuracy >= 90) {
      return '今天的小进步好可爱！继续保持哦～'
    } else if (accuracy >= 70) {
      return '做得不错，再接再厉！'
    } else {
      return '没关系，多读多练就会进步！'
    }
  },

  // 显示勋章详情
  showBadgeDetail() {
    if (this.data.newBadge) {
      this.setData({ showBadgePopup: true })
    }
  },

  // 关闭勋章弹窗
  closeBadgePopup() {
    this.setData({ showBadgePopup: false })
  },

  // 分享勋章
  shareBadge() {
    // 触发分享
    this.setData({ showBadgePopup: false })
  },

  // 再来一篇
  async readAgain() {
    try {
      // 获取新的推荐文章
      const article = await articleService.getTodayArticle()
      if (article) {
        wx.redirectTo({
          url: `/pages/article/article?id=${article.id}`
        })
      } else {
        wx.showToast({ 
          title: '今日文章已读完', 
          icon: 'none' 
        })
      }
    } catch (error) {
      wx.showToast({ 
        title: '获取文章失败', 
        icon: 'none' 
      })
    }
  },

  // 查看勋章收藏
  viewBadges() {
    wx.navigateTo({ url: '/pages/badges/badges' })
  },

  // 返回首页
  goHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  // 返回
  goBack() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  // 分享
  onShareAppMessage() {
    return {
      title: `我在阅读星球完成了今日阅读，正确率${this.data.accuracy}%！`,
      path: '/pages/index/index',
    }
  },
})
```

---

## 4.2e.5 验收标准

### 视觉验收

- [ ] "太棒了！" 大标题显示
- [ ] 三颗星星根据成绩正确显示（亮/暗）
- [ ] 鼓励语卡片包含用户头像
- [ ] 勋章解锁卡片样式正确（渐变背景、虚线边框）
- [ ] 用时和正确率统计卡片显示
- [ ] 能力雷达图正确渲染
- [ ] 底部"再来一篇"按钮为橙色

### 功能验收

- [ ] 正确加载进度结果
- [ ] 星级计算正确
- [ ] 新勋章弹窗自动显示
- [ ] 点击勋章卡片显示详情
- [ ] "再来一篇"获取新文章
- [ ] "查看勋章收藏"跳转正确
- [ ] "今天到此为止"返回首页

---

## 4.2e.6 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 结果页配置 | `pages/result/result.json` |
| 结果页结构 | `pages/result/result.wxml` |
| 结果页样式 | `pages/result/result.wxss` |
| 结果页逻辑 | `pages/result/result.js` |
