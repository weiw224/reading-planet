# Phase 4.2f: 微信小程序 - 个人中心

> **前置依赖**: Phase 4.1  
> **本文件范围**: 个人中心、勋章墙、历史记录  
> **参考原型**: `个人主页_(能力与历史)_*`

---

## 4.2f.1 个人中心页 (pages/profile)

### 页面配置 (profile.json)

```json
{
  "navigationBarTitleText": "个人主页",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black",
  "usingComponents": {
    "radar-chart": "/components/radar-chart/radar-chart",
    "badge-item": "/components/badge-item/badge-item"
  }
}
```

### 页面结构 (profile.wxml)

```xml
<!-- 个人中心 - 参考原型: 个人主页_(能力与历史) -->
<view class="page-profile">
  <!-- 顶部导航 -->
  <view class="nav-bar">
    <view class="nav-left" bindtap="openSettings">
      <image src="/images/icons/settings.png" mode="aspectFit" />
    </view>
    <text class="nav-title">个人主页</text>
    <view class="nav-right" bindtap="showNotifications">
      <image src="/images/icons/bell.png" mode="aspectFit" />
    </view>
  </view>

  <scroll-view class="main-content" scroll-y enhanced show-scrollbar="{{false}}">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="user-avatar-wrapper">
        <image 
          class="user-avatar" 
          src="{{userInfo.avatar_url || '/images/default-avatar.png'}}" 
          mode="aspectFill"
        />
        <view class="level-badge">Lv.{{userLevel}}</view>
      </view>
      
      <text class="user-nickname">{{userInfo.nickname || '小书虫'}}</text>
      <text class="user-title">称号：{{userTitle}}</text>
      
      <view class="streak-info">
        <image src="/images/icons/calendar-check.png" mode="aspectFit" />
        <text>已坚持阅读 {{stats.streakDays}} 天</text>
      </view>
      
      <button class="btn-edit" bindtap="editProfile">编辑资料</button>
    </view>

    <!-- 我的勋章墙 -->
    <view class="section badge-section">
      <view class="section-header">
        <text class="section-title">我的勋章墙</text>
        <view class="view-all" bindtap="viewAllBadges">
          <text>全部</text>
          <image src="/images/icons/arrow-right.png" mode="aspectFit" />
        </view>
      </view>
      
      <view class="badge-grid">
        <badge-item
          wx:for="{{badges}}"
          wx:key="id"
          badge="{{item}}"
          bind:tap="onBadgeTap"
        />
      </view>
    </view>

    <!-- 能力雷达图 -->
    <view class="section ability-section">
      <text class="section-title">能力雷达图</text>
      <view class="radar-wrapper">
        <radar-chart 
          data="{{abilityData}}"
          size="{{400}}"
        />
      </view>
      
      <button class="btn-weak-point" bindtap="goWeakPoint">
        <image src="/images/icons/trend-up.png" mode="aspectFit" />
        <text>去补弱项！</text>
      </button>
    </view>

    <!-- 最近练习 -->
    <view class="section history-section">
      <view class="section-header">
        <text class="section-title">最近练习</text>
        <view class="view-all" bindtap="viewAllHistory">
          <text>查看全部</text>
          <image src="/images/icons/arrow-right.png" mode="aspectFit" />
        </view>
      </view>
      
      <view class="history-list">
        <view 
          class="history-item"
          wx:for="{{recentHistory}}"
          wx:key="id"
          bindtap="viewHistoryDetail"
          data-id="{{item.id}}"
        >
          <view class="history-date">{{item.date}}</view>
          <view class="history-content">
            <text class="history-title">《{{item.article_title}}》</text>
            <view class="history-stats">
              <text class="score">{{item.score}}分</text>
              <text class="time">{{item.time_text}}</text>
            </view>
          </view>
          <view class="history-icons">
            <image 
              src="/images/icons/book.png" 
              mode="aspectFit"
              class="icon-book"
            />
            <image 
              wx:if="{{item.has_badge}}"
              src="/images/icons/badge-small.png" 
              mode="aspectFit"
              class="icon-badge"
            />
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-history" wx:if="{{recentHistory.length === 0}}">
        <image src="/images/empty-history.png" mode="aspectFit" />
        <text>还没有阅读记录，快去开始吧！</text>
      </view>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </scroll-view>
</view>
```

### 页面样式 (profile.wxss)

```css
/* 个人中心样式 */
.page-profile {
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-left image, .nav-right image {
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

/* 用户信息卡片 */
.user-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.user-avatar-wrapper {
  position: relative;
  margin-bottom: 20rpx;
}

.user-avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  border: 6rpx solid #fff;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
}

.level-badge {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #52C41A 0%, #389E0D 100%);
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  white-space: nowrap;
}

.user-nickname {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 8rpx;
}

.user-title {
  font-size: 26rpx;
  color: #F5A623;
  margin-bottom: 20rpx;
}

.streak-info {
  display: flex;
  align-items: center;
  color: #F5A623;
  font-size: 26rpx;
  margin-bottom: 24rpx;
}

.streak-info image {
  width: 32rpx;
  height: 32rpx;
  margin-right: 8rpx;
}

.btn-edit {
  width: 100%;
  height: 80rpx;
  background: #fff;
  border: 2rpx solid #eee;
  border-radius: 40rpx;
  font-size: 30rpx;
  color: #666;
}

.btn-edit::after {
  border: none;
}

/* 区块样式 */
.section {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.view-all {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: #F5A623;
}

.view-all image {
  width: 24rpx;
  height: 24rpx;
  margin-left: 4rpx;
}

/* 勋章网格 */
.badge-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

/* 能力雷达图 */
.radar-wrapper {
  display: flex;
  justify-content: center;
  padding: 20rpx 0;
}

.btn-weak-point {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  background: #F5A623;
  border-radius: 44rpx;
  border: none;
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  margin-top: 20rpx;
}

.btn-weak-point::after {
  border: none;
}

.btn-weak-point image {
  width: 36rpx;
  height: 36rpx;
  margin-right: 12rpx;
}

/* 历史记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
}

.history-date {
  font-size: 24rpx;
  color: #888;
  margin-right: 20rpx;
  white-space: nowrap;
}

.history-content {
  flex: 1;
  min-width: 0;
}

.history-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-stats {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.history-stats .score {
  font-size: 26rpx;
  color: #F5A623;
  font-weight: 600;
}

.history-stats .time {
  font-size: 24rpx;
  color: #999;
}

.history-icons {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.history-icons image {
  width: 40rpx;
  height: 40rpx;
}

/* 空状态 */
.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.empty-history image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
  opacity: 0.5;
}

.empty-history text {
  font-size: 26rpx;
  color: #999;
}

/* 底部占位 */
.bottom-placeholder {
  height: 40rpx;
}
```

### 页面逻辑 (profile.js)

```javascript
const app = getApp()
const userService = require('../../services/userService')
const progressService = require('../../services/progressService')

Page({
  data: {
    userInfo: null,
    userLevel: 1,
    userTitle: '初级小学者',
    
    stats: {
      streakDays: 0,
      totalReadings: 0,
      badgeCount: 0,
    },
    
    badges: [],
    abilityData: [],
    recentHistory: [],
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    // 每次显示时刷新
    this.loadData()
  },

  // 加载数据
  async loadData() {
    try {
      const [userInfo, stats, badges, abilities, history] = await Promise.all([
        userService.getCurrentUser(),
        userService.getUserStats(),
        userService.getBadges(),
        userService.getAbilityRadar(),
        progressService.getHistory(1, 5),
      ])

      // 计算等级和称号
      const { level, title } = this.calculateLevelAndTitle(stats.growth_value)

      // 处理勋章（只显示前6个）
      const displayBadges = badges.slice(0, 6)

      // 能力数据
      const abilityData = [
        { label: '细节提取', value: abilities.detail || 0 },
        { label: '中心思想', value: abilities.summary || 0 },
        { label: '词语运用', value: abilities.language || 0 },
        { label: '逻辑推理', value: abilities.reasoning || 0 },
        { label: '人物分析', value: abilities.character || 0 },
      ]

      // 处理历史记录
      const recentHistory = history.items.map(item => ({
        ...item,
        date: this.formatDate(item.completed_at),
        time_text: `${Math.floor(item.time_spent / 60)}分钟`,
        has_badge: !!item.badge_earned,
      }))

      this.setData({
        userInfo,
        userLevel: level,
        userTitle: title,
        stats: {
          streakDays: stats.streak_days || 0,
          totalReadings: stats.total_readings || 0,
          badgeCount: stats.badge_count || 0,
        },
        badges: displayBadges,
        abilityData,
        recentHistory,
      })

      app.updateUserInfo(userInfo)

    } catch (error) {
      console.error('加载个人中心数据失败:', error)
    }
  },

  // 计算等级和称号
  calculateLevelAndTitle(growthValue) {
    // 等级规则：每50成长值升一级
    const level = Math.floor((growthValue || 0) / 50) + 1
    
    // 称号映射
    const titles = {
      1: '初级小学者',
      5: '阅读新秀',
      10: '阅读达人',
      15: '阅读高手',
      20: '阅读大师',
      30: '阅读之星',
    }

    let title = '初级小学者'
    for (const [minLevel, t] of Object.entries(titles).reverse()) {
      if (level >= parseInt(minLevel)) {
        title = t
        break
      }
    }

    return { level: Math.min(level, 99), title }
  },

  // 格式化日期
  formatDate(dateStr) {
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}-${day.toString().padStart(2, '0')}`
  },

  // 编辑资料
  editProfile() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },

  // 查看全部勋章
  viewAllBadges() {
    wx.navigateTo({ url: '/pages/badges/badges' })
  },

  // 勋章点击
  onBadgeTap(e) {
    const badge = e.detail.badge
    if (badge.is_unlocked) {
      // 显示勋章详情
      wx.showModal({
        title: badge.name,
        content: `${badge.description}\n获得日期：${badge.unlocked_at || ''}`,
        showCancel: false,
      })
    } else {
      // 显示解锁条件
      wx.showModal({
        title: badge.name,
        content: `解锁条件：${badge.unlock_condition}`,
        confirmText: '去完成',
        success: (res) => {
          if (res.confirm) {
            wx.switchTab({ url: '/pages/index/index' })
          }
        }
      })
    }
  },

  // 去补弱项
  async goWeakPoint() {
    try {
      const article = await require('../../services/articleService').getWeakPointArticle()
      if (article) {
        wx.navigateTo({
          url: `/pages/article/article?id=${article.id}&mode=weak`
        })
      } else {
        wx.showToast({ title: '暂无推荐', icon: 'none' })
      }
    } catch (error) {
      wx.showToast({ title: '获取推荐失败', icon: 'none' })
    }
  },

  // 查看全部历史
  viewAllHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  // 查看历史详情
  viewHistoryDetail(e) {
    const progressId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/result/result?progressId=${progressId}&readonly=1`
    })
  },

  // 打开设置
  openSettings() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },

  // 显示通知
  showNotifications() {
    wx.showToast({ title: '暂无通知', icon: 'none' })
  },
})
```

---

## 4.2f.2 勋章墙页 (pages/badges)

### 页面结构 (badges.wxml)

```xml
<!-- 勋章墙页面 -->
<view class="page-badges">
  <view class="nav-bar">
    <view class="nav-left" bindtap="goBack">
      <image src="/images/icons/arrow-left.png" mode="aspectFit" />
    </view>
    <text class="nav-title">我的勋章</text>
    <view class="nav-right"></view>
  </view>

  <scroll-view class="main-content" scroll-y>
    <!-- 已获得勋章 -->
    <view class="section">
      <text class="section-title">已获得 ({{unlockedCount}})</text>
      <view class="badge-grid">
        <view 
          class="badge-card unlocked"
          wx:for="{{unlockedBadges}}"
          wx:key="id"
          bindtap="showBadgeDetail"
          data-badge="{{item}}"
        >
          <image class="badge-icon" src="{{item.icon_url}}" mode="aspectFit" />
          <text class="badge-name">{{item.name}}</text>
          <text class="badge-status">已解锁</text>
        </view>
      </view>
    </view>

    <!-- 待解锁勋章 -->
    <view class="section">
      <text class="section-title">待解锁 ({{lockedCount}})</text>
      <view class="badge-grid">
        <view 
          class="badge-card locked"
          wx:for="{{lockedBadges}}"
          wx:key="id"
          bindtap="showLockCondition"
          data-badge="{{item}}"
        >
          <view class="badge-icon-wrapper">
            <image class="badge-icon" src="{{item.icon_url}}" mode="aspectFit" />
            <image class="lock-icon" src="/images/icons/lock.png" mode="aspectFit" />
          </view>
          <text class="badge-name">{{item.name}}</text>
          <text class="badge-condition">{{item.short_condition}}</text>
        </view>
      </view>
    </view>
  </scroll-view>
</view>
```

### 页面样式 (badges.wxss)

```css
.page-badges {
  min-height: 100vh;
  background: var(--bg-page);
}

.main-content {
  padding: 30rpx;
}

.section {
  margin-bottom: 40rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
  display: block;
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.badge-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.06);
}

.badge-card.unlocked .badge-icon {
  width: 100rpx;
  height: 100rpx;
}

.badge-card.locked {
  opacity: 0.7;
}

.badge-icon-wrapper {
  position: relative;
}

.badge-card.locked .badge-icon {
  width: 100rpx;
  height: 100rpx;
  filter: grayscale(100%);
}

.lock-icon {
  position: absolute;
  right: -10rpx;
  bottom: -10rpx;
  width: 36rpx;
  height: 36rpx;
}

.badge-name {
  font-size: 26rpx;
  font-weight: 500;
  color: #333;
  margin-top: 16rpx;
  text-align: center;
}

.badge-status {
  font-size: 22rpx;
  color: #F5A623;
  margin-top: 8rpx;
}

.badge-condition {
  font-size: 20rpx;
  color: #999;
  margin-top: 8rpx;
  text-align: center;
}
```

---

## 4.2f.3 历史记录页 (pages/history)

### 页面结构 (history.wxml)

```xml
<!-- 历史记录页面 -->
<view class="page-history">
  <view class="nav-bar">
    <view class="nav-left" bindtap="goBack">
      <image src="/images/icons/arrow-left.png" mode="aspectFit" />
    </view>
    <text class="nav-title">阅读历史</text>
    <view class="nav-right"></view>
  </view>

  <scroll-view 
    class="main-content" 
    scroll-y
    bindscrolltolower="loadMore"
    lower-threshold="100"
  >
    <view class="history-list">
      <view 
        class="history-item"
        wx:for="{{historyList}}"
        wx:key="id"
        bindtap="viewDetail"
        data-id="{{item.id}}"
      >
        <view class="item-left">
          <image class="cover" src="{{item.article_cover}}" mode="aspectFill" />
        </view>
        <view class="item-content">
          <text class="title">《{{item.article_title}}》</text>
          <view class="meta">
            <text class="date">{{item.date_text}}</text>
            <text class="score">得分：{{item.score}}分</text>
          </view>
          <view class="tags">
            <text class="tag" wx:for="{{item.tags}}" wx:key="*this">{{item}}</text>
          </view>
        </view>
        <view class="item-right">
          <text class="accuracy">{{item.accuracy}}%</text>
          <text class="accuracy-label">正确率</text>
        </view>
      </view>
    </view>

    <view class="loading-more" wx:if="{{loading}}">
      <text>加载中...</text>
    </view>

    <view class="no-more" wx:if="{{!hasMore && historyList.length > 0}}">
      <text>没有更多了</text>
    </view>

    <view class="empty-state" wx:if="{{!loading && historyList.length === 0}}">
      <image src="/images/empty-history.png" mode="aspectFit" />
      <text>还没有阅读记录</text>
      <button class="btn-start" bindtap="goReading">开始阅读</button>
    </view>
  </scroll-view>
</view>
```

---

## 4.2f.4 验收标准

### 个人中心

- [ ] 用户头像、昵称、等级正确显示
- [ ] 称号根据等级变化
- [ ] 连续阅读天数正确
- [ ] 勋章网格显示前6个
- [ ] 能力雷达图正确渲染
- [ ] "去补弱项"按钮可点击
- [ ] 最近练习列表正确显示

### 勋章墙

- [ ] 已解锁勋章彩色显示
- [ ] 未解锁勋章灰色+锁图标
- [ ] 点击显示详情或条件

### 历史记录

- [ ] 列表正确加载
- [ ] 下拉加载更多
- [ ] 空状态正确显示

---

## 4.2f.5 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 个人中心 | `pages/profile/profile.*` |
| 勋章墙 | `pages/badges/badges.*` |
| 历史记录 | `pages/history/history.*` |
