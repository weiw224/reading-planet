# Phase 4.2b: 微信小程序 - 首页

> **前置依赖**: Phase 4.1, Phase 4.2a  
> **本文件范围**: 首页（今日成就、日历、今日推荐）  
> **参考原型**: `首页_(每日练习与日历)`

---

## 4.2b.1 页面配置 (index.json)

```json
{
  "navigationBarTitleText": "首页",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black",
  "usingComponents": {
    "today-stats": "/components/today-stats/today-stats",
    "calendar": "/components/calendar/calendar",
    "article-card": "/components/article-card/article-card"
  }
}
```

---

## 4.2b.2 页面结构 (index.wxml)

```xml
<!-- 首页 - 参考原型: 首页_(每日练习与日历) -->
<view class="page-index">
  <!-- 顶部导航栏 -->
  <view class="nav-bar">
    <!-- 用户头像 -->
    <view class="user-avatar" bindtap="goToProfile">
      <image 
        src="{{userInfo.avatar_url || '/images/default-avatar.png'}}" 
        mode="aspectFill"
      />
    </view>
    
    <!-- 页面标题 -->
    <text class="nav-title">首页</text>
    
    <!-- 通知图标 -->
    <view class="notify-icon" bindtap="showNotifications">
      <image src="/images/icons/bell.png" mode="aspectFit" />
      <view class="notify-badge" wx:if="{{notifyCount > 0}}"></view>
    </view>
  </view>

  <!-- 主内容区 -->
  <scroll-view 
    class="main-content" 
    scroll-y 
    enhanced
    show-scrollbar="{{false}}"
    refresher-enabled
    refresher-triggered="{{refreshing}}"
    bindrefresherrefresh="onPullDownRefresh"
  >
    <!-- 今日成就卡片 -->
    <view class="section stats-section">
      <today-stats 
        badge-count="{{stats.badgeCount}}"
        growth-value="{{stats.growthValue}}"
        streak-days="{{stats.streakDays}}"
        rank-percent="{{stats.rankPercent}}"
      />
    </view>

    <!-- 今日推荐区域 -->
    <view class="section recommend-section">
      <view class="section-header">
        <text class="section-title">今天来练阅读思维吧！</text>
      </view>
      
      <article-card 
        wx:if="{{todayArticle}}"
        article="{{todayArticle}}"
        show-badge="{{true}}"
        badge-text="今日推荐"
        bind:start="startReading"
      />
      
      <!-- 无推荐时的状态 -->
      <view class="empty-recommend" wx:if="{{!todayArticle && !loading}}">
        <image src="/images/empty-article.png" mode="aspectFit" />
        <text>今日推荐已完成，明天再来吧~</text>
      </view>
    </view>

    <!-- 学习月历 -->
    <view class="section calendar-section">
      <view class="section-header">
        <text class="section-title">学习月历</text>
        <view class="month-info" bindtap="showMonthPicker">
          <text>{{currentMonth}}月进度 {{monthProgress}}</text>
          <image src="/images/icons/arrow-right.png" mode="aspectFit" />
        </view>
      </view>
      
      <calendar 
        year="{{currentYear}}"
        month="{{currentMonth}}"
        checkin-days="{{checkinDays}}"
        today="{{today}}"
      />
    </view>

    <!-- 激励卡片 -->
    <view class="motivation-card" wx:if="{{motivationText}}">
      <view class="motivation-icon">
        <image src="/images/icons/smile.png" mode="aspectFit" />
      </view>
      <view class="motivation-content">
        <text class="motivation-title">{{motivationTitle}}</text>
        <text class="motivation-desc">{{motivationText}}</text>
      </view>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </scroll-view>
</view>
```

---

## 4.2b.3 页面样式 (index.wxss)

```css
/* 首页样式 - 橙黄暖色调 */
.page-index {
  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  padding-top: calc(20rpx + var(--status-bar-height, 44px));
  background: var(--bg-page);
}

.user-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  overflow: hidden;
  border: 4rpx solid #fff;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.user-avatar image {
  width: 100%;
  height: 100%;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.notify-icon {
  position: relative;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notify-icon image {
  width: 48rpx;
  height: 48rpx;
}

.notify-badge {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  width: 16rpx;
  height: 16rpx;
  background: #FF4D4F;
  border-radius: 50%;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 0 30rpx;
}

/* 区块样式 */
.section {
  margin-bottom: 30rpx;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.month-info {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #888;
}

.month-info image {
  width: 24rpx;
  height: 24rpx;
  margin-left: 8rpx;
}

/* 空状态 */
.empty-recommend {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
  background: #fff;
  border-radius: 24rpx;
}

.empty-recommend image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
  opacity: 0.5;
}

.empty-recommend text {
  font-size: 28rpx;
  color: #999;
}

/* 激励卡片 */
.motivation-card {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background: linear-gradient(135deg, #F5A623 0%, #FFB84D 100%);
  border-radius: 24rpx;
  margin-bottom: 30rpx;
}

.motivation-icon {
  width: 80rpx;
  height: 80rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.motivation-icon image {
  width: 48rpx;
  height: 48rpx;
}

.motivation-content {
  flex: 1;
}

.motivation-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.motivation-desc {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 底部占位 */
.bottom-placeholder {
  height: 40rpx;
}
```

---

## 4.2b.4 页面逻辑 (index.js)

```javascript
const app = getApp()
const userService = require('../../services/userService')
const articleService = require('../../services/articleService')

Page({
  data: {
    loading: true,
    refreshing: false,
    userInfo: null,
    notifyCount: 0,
    
    // 统计数据
    stats: {
      badgeCount: 0,
      growthValue: 0,
      streakDays: 0,
      rankPercent: 0,
    },
    
    // 今日推荐
    todayArticle: null,
    
    // 日历数据
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    today: new Date().getDate(),
    checkinDays: [],
    monthProgress: '0/30',
    
    // 激励文案
    motivationTitle: '',
    motivationText: '',
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    // 每次显示时刷新数据
    if (!this.data.loading) {
      this.loadData()
    }
  },

  // 下拉刷新
  async onPullDownRefresh() {
    this.setData({ refreshing: true })
    await this.loadData()
    this.setData({ refreshing: false })
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true })

    try {
      // 并行请求数据
      const [userInfo, stats, todayArticle, checkins] = await Promise.all([
        userService.getCurrentUser(),
        userService.getUserStats(),
        articleService.getTodayArticle().catch(() => null),
        userService.getCheckins(this.data.currentYear, this.data.currentMonth),
      ])

      // 更新用户信息
      app.updateUserInfo(userInfo)

      // 计算月进度
      const totalDays = new Date(
        this.data.currentYear, 
        this.data.currentMonth, 
        0
      ).getDate()
      const checkedDays = checkins.length

      // 生成激励文案
      const motivation = this.generateMotivation(stats.streak_days)

      this.setData({
        userInfo,
        stats: {
          badgeCount: stats.badge_count || 0,
          growthValue: stats.growth_value || 0,
          streakDays: stats.streak_days || 0,
          rankPercent: stats.rank_percent || 0,
        },
        todayArticle,
        checkinDays: checkins.map(c => c.day),
        monthProgress: `${checkedDays}/${totalDays}`,
        motivationTitle: motivation.title,
        motivationText: motivation.text,
        loading: false,
      })

    } catch (error) {
      console.error('加载首页数据失败:', error)
      this.setData({ loading: false })
    }
  },

  // 生成激励文案
  generateMotivation(streakDays) {
    if (streakDays >= 7) {
      return {
        title: '太厉害了！',
        text: `你已经连续阅读${streakDays}天，是阅读小能手！`,
      }
    } else if (streakDays >= 3) {
      return {
        title: '继续保持！',
        text: `再读${7 - streakDays}天即可领取本周"阅读小达人"勋章`,
      }
    } else if (streakDays >= 1) {
      return {
        title: '加油！',
        text: `再读${3 - streakDays}天即可获得"三日小达人"勋章`,
      }
    } else {
      return {
        title: '开始阅读吧！',
        text: '每天阅读一篇，积累成长值，解锁更多勋章',
      }
    }
  },

  // 开始阅读
  startReading(e) {
    const article = e.detail || this.data.todayArticle
    if (!article) return

    wx.navigateTo({
      url: `/pages/article/article?id=${article.id}`
    })
  },

  // 跳转个人中心
  goToProfile() {
    wx.switchTab({ url: '/pages/profile/profile' })
  },

  // 显示通知
  showNotifications() {
    wx.showToast({
      title: '暂无新通知',
      icon: 'none'
    })
  },

  // 显示月份选择
  showMonthPicker() {
    // 可以实现月份选择器
    wx.showToast({
      title: '查看历史月份',
      icon: 'none'
    })
  },
})
```

---

## 4.2b.5 验收标准

### 视觉验收

- [ ] 页面背景为米黄色 (#FFF8E7)
- [ ] 顶部导航包含用户头像、标题、通知图标
- [ ] "今日成就"卡片样式与原型一致
- [ ] 今日推荐卡片包含封面图、标题、年级、字数、时间
- [ ] "今日推荐"标签显示在卡片左上角
- [ ] 日历组件样式正确，已打卡日期有对勾
- [ ] 激励卡片为橙色渐变背景

### 功能验收

- [ ] 下拉刷新正常工作
- [ ] 点击今日推荐卡片跳转文章页
- [ ] 点击头像跳转个人中心
- [ ] 统计数据正确显示
- [ ] 日历打卡数据正确

### 性能验收

- [ ] 首次加载时间 < 2秒
- [ ] 下拉刷新流畅

---

## 4.2b.6 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 首页配置 | `pages/index/index.json` |
| 首页结构 | `pages/index/index.wxml` |
| 首页样式 | `pages/index/index.wxss` |
| 首页逻辑 | `pages/index/index.js` |
