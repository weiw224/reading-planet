# Phase 4.2a: 微信小程序 - 登录页与年级选择页

> **前置依赖**: Phase 4.1 (核心配置)  
> **本文件范围**: 登录页、年级选择页

---

## 4.2a.1 登录页 (pages/login)

### 页面配置 (login.json)

```json
{
  "navigationBarTitleText": "",
  "navigationStyle": "custom",
  "backgroundColor": "#FFF8E7"
}
```

### 页面结构 (login.wxml)

```xml
<!-- 登录页 - 参考原型: 微信登录界面 -->
<view class="page-login">
  <!-- 背景装饰 -->
  <view class="bg-decoration"></view>
  
  <!-- 主内容区 -->
  <view class="login-content">
    <!-- 顶部帮助图标 -->
    <view class="help-icon" bindtap="showHelp">
      <image src="/images/icons/help.png" mode="aspectFit" />
    </view>
    
    <!-- 吉祥物图片 - 考拉 -->
    <view class="mascot-wrapper">
      <image 
        class="mascot-image" 
        src="/images/mascots/koala.png" 
        mode="aspectFit"
      />
    </view>
    
    <!-- 欢迎文案 -->
    <view class="welcome-text">
      <text class="title">欢迎来到阅读星球</text>
      <text class="subtitle">开启你的奇幻阅读之旅</text>
    </view>
    
    <!-- 登录按钮 -->
    <view class="login-section">
      <button 
        class="btn-login" 
        bindtap="handleLogin"
        loading="{{loading}}"
      >
        <image 
          class="wechat-icon" 
          src="/images/icons/wechat.png" 
          mode="aspectFit"
          wx:if="{{!loading}}"
        />
        <text>微信一键登录</text>
      </button>
    </view>
    
    <!-- 用户协议 -->
    <view class="agreement-section">
      <checkbox-group bindchange="onAgreementChange">
        <label class="agreement-label">
          <checkbox 
            value="agree" 
            checked="{{agreed}}"
            color="#F5A623"
          />
          <text class="agreement-text">我已阅读并同意</text>
          <text class="agreement-link" bindtap="viewUserAgreement">用户协议</text>
          <text class="agreement-text">和</text>
          <text class="agreement-link" bindtap="viewPrivacyPolicy">隐私政策</text>
        </label>
      </checkbox-group>
    </view>
  </view>
</view>
```

### 页面样式 (login.wxss)

```css
/* 登录页样式 - 橙黄暖色调 */
.page-login {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E7 0%, #FFF5E0 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
  background: radial-gradient(circle at 50% 0%, rgba(245, 166, 35, 0.1) 0%, transparent 70%);
}

/* 帮助图标 */
.help-icon {
  position: absolute;
  top: 100rpx;
  right: 40rpx;
  width: 60rpx;
  height: 60rpx;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.help-icon image {
  width: 32rpx;
  height: 32rpx;
}

/* 主内容区 */
.login-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 60rpx 80rpx;
  width: 100%;
  box-sizing: border-box;
}

/* 吉祥物 */
.mascot-wrapper {
  width: 500rpx;
  height: 500rpx;
  margin-top: 60rpx;
  margin-bottom: 40rpx;
}

.mascot-image {
  width: 100%;
  height: 100%;
  border-radius: 40rpx;
}

/* 欢迎文案 */
.welcome-text {
  text-align: center;
  margin-bottom: 100rpx;
}

.welcome-text .title {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 16rpx;
}

.welcome-text .subtitle {
  display: block;
  font-size: 28rpx;
  color: #888;
}

/* 登录按钮区域 */
.login-section {
  width: 100%;
  padding: 0 20rpx;
}

.btn-login {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100rpx;
  background: #F5A623;
  border-radius: 50rpx;
  border: none;
  font-size: 34rpx;
  font-weight: 600;
  color: #fff;
}

.btn-login::after {
  border: none;
}

.btn-login:active {
  background: #E8941C;
}

.wechat-icon {
  width: 44rpx;
  height: 44rpx;
  margin-right: 16rpx;
}

/* 用户协议 */
.agreement-section {
  margin-top: 40rpx;
}

.agreement-label {
  display: flex;
  align-items: center;
  font-size: 24rpx;
}

.agreement-text {
  color: #999;
}

.agreement-link {
  color: #F5A623;
}

checkbox {
  transform: scale(0.8);
  margin-right: 8rpx;
}
```

### 页面逻辑 (login.js)

```javascript
const app = getApp()
const userService = require('../../services/userService')

Page({
  data: {
    loading: false,
    agreed: false,
  },

  onLoad() {
    // 如果已登录，直接跳转
    if (app.globalData.isLoggedIn) {
      this.navigateToHome()
    }
  },

  // 勾选协议
  onAgreementChange(e) {
    this.setData({
      agreed: e.detail.value.includes('agree')
    })
  },

  // 微信登录
  async handleLogin() {
    // 检查是否同意协议
    if (!this.data.agreed) {
      wx.showToast({
        title: '请先阅读并同意用户协议',
        icon: 'none'
      })
      return
    }

    if (this.data.loading) return
    
    this.setData({ loading: true })

    try {
      // 1. 获取微信登录 code
      const loginRes = await wx.login()
      const code = loginRes.code

      if (!code) {
        throw new Error('获取登录凭证失败')
      }

      // 2. 调用后端登录接口
      const result = await userService.wechatLogin(code)

      // 3. 保存登录信息
      app.setLoginInfo(result.access_token, {})

      // 4. 获取用户详细信息
      const userInfo = await userService.getCurrentUser()
      app.updateUserInfo(userInfo)

      // 5. 判断是否需要选择年级
      if (result.is_new_user || !userInfo.grade) {
        wx.redirectTo({ 
          url: '/pages/grade-select/grade-select' 
        })
      } else {
        this.navigateToHome()
      }

    } catch (error) {
      console.error('登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 跳转首页
  navigateToHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  // 查看用户协议
  viewUserAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '用户协议内容...',
      showCancel: false
    })
  },

  // 查看隐私政策
  viewPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '隐私政策内容...',
      showCancel: false
    })
  },

  // 显示帮助
  showHelp() {
    wx.showModal({
      title: '帮助',
      content: '如有问题，请联系客服',
      showCancel: false
    })
  },
})
```

---

## 4.2a.2 年级选择页 (pages/grade-select)

### 页面配置 (grade-select.json)

```json
{
  "navigationBarTitleText": "选择年级",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black"
}
```

### 页面结构 (grade-select.wxml)

```xml
<!-- 年级选择页 -->
<view class="page-grade-select">
  <!-- 顶部提示 -->
  <view class="header-section">
    <image 
      class="header-icon" 
      src="/images/mascots/owl.png" 
      mode="aspectFit"
    />
    <view class="header-text">
      <text class="title">选择你的年级</text>
      <text class="subtitle">我们将为你推荐合适难度的阅读内容</text>
    </view>
  </view>

  <!-- 年级列表 -->
  <view class="grade-list">
    <view 
      class="grade-item {{selectedGrade === item.value ? 'selected' : ''}}"
      wx:for="{{gradeList}}"
      wx:key="value"
      bindtap="selectGrade"
      data-grade="{{item.value}}"
    >
      <view class="grade-info">
        <image class="grade-icon" src="{{item.icon}}" mode="aspectFit" />
        <text class="grade-name">{{item.name}}</text>
      </view>
      <view class="check-icon" wx:if="{{selectedGrade === item.value}}">
        <image src="/images/icons/check-circle.png" mode="aspectFit" />
      </view>
    </view>
  </view>

  <!-- 底部按钮 -->
  <view class="bottom-section safe-area-bottom">
    <button 
      class="btn-confirm {{selectedGrade ? '' : 'disabled'}}"
      bindtap="confirmGrade"
      disabled="{{!selectedGrade || loading}}"
      loading="{{loading}}"
    >
      开始阅读之旅
    </button>
  </view>
</view>
```

### 页面样式 (grade-select.wxss)

```css
.page-grade-select {
  min-height: 100vh;
  background: var(--bg-page);
  padding-bottom: 180rpx;
}

/* 顶部区域 */
.header-section {
  display: flex;
  align-items: center;
  padding: 40rpx 30rpx;
  background: #fff;
  margin-bottom: 30rpx;
}

.header-icon {
  width: 100rpx;
  height: 100rpx;
  margin-right: 24rpx;
}

.header-text .title {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.header-text .subtitle {
  display: block;
  font-size: 26rpx;
  color: #888;
}

/* 年级列表 */
.grade-list {
  padding: 0 30rpx;
}

.grade-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 30rpx;
  background: #fff;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
  border: 4rpx solid transparent;
  transition: all 0.2s ease;
}

.grade-item.selected {
  border-color: #F5A623;
  background: #FFF9EE;
}

.grade-info {
  display: flex;
  align-items: center;
}

.grade-icon {
  width: 60rpx;
  height: 60rpx;
  margin-right: 24rpx;
}

.grade-name {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
}

.check-icon {
  width: 48rpx;
  height: 48rpx;
}

.check-icon image {
  width: 100%;
  height: 100%;
}

/* 底部按钮 */
.bottom-section {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx 40rpx 40rpx;
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
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

.btn-confirm.disabled {
  background: #ccc;
}
```

### 页面逻辑 (grade-select.js)

```javascript
const app = getApp()
const userService = require('../../services/userService')

Page({
  data: {
    loading: false,
    selectedGrade: '',
    gradeList: [
      { value: 'GRADE_1', name: '一年级', icon: '/images/icons/grade-1.png' },
      { value: 'GRADE_2', name: '二年级', icon: '/images/icons/grade-2.png' },
      { value: 'GRADE_3', name: '三年级', icon: '/images/icons/grade-3.png' },
      { value: 'GRADE_4', name: '四年级', icon: '/images/icons/grade-4.png' },
      { value: 'GRADE_5', name: '五年级', icon: '/images/icons/grade-5.png' },
      { value: 'GRADE_6', name: '六年级', icon: '/images/icons/grade-6.png' },
    ],
  },

  // 选择年级
  selectGrade(e) {
    const grade = e.currentTarget.dataset.grade
    this.setData({ selectedGrade: grade })
  },

  // 确认年级
  async confirmGrade() {
    if (!this.data.selectedGrade || this.data.loading) return

    this.setData({ loading: true })

    try {
      // 更新用户年级
      await userService.updateUser({
        grade: this.data.selectedGrade
      })

      // 更新本地用户信息
      const userInfo = app.globalData.userInfo || {}
      userInfo.grade = this.data.selectedGrade
      app.updateUserInfo(userInfo)

      // 提示成功
      wx.showToast({
        title: '设置成功',
        icon: 'success'
      })

      // 跳转首页
      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' })
      }, 1000)

    } catch (error) {
      console.error('设置年级失败:', error)
      wx.showToast({
        title: '设置失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },
})
```

---

## 4.2a.3 验收标准

### 登录页

- [ ] 页面样式与原型一致（米黄背景、考拉吉祥物）
- [ ] 微信一键登录按钮可点击
- [ ] 未勾选协议时提示
- [ ] 登录成功后正确跳转
- [ ] 新用户跳转年级选择页
- [ ] 老用户直接进入首页

### 年级选择页

- [ ] 6个年级选项完整显示
- [ ] 选中状态高亮
- [ ] 确认按钮状态联动
- [ ] 保存年级成功
- [ ] 跳转首页正常

---

## 4.2a.4 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 登录页配置 | `pages/login/login.json` |
| 登录页结构 | `pages/login/login.wxml` |
| 登录页样式 | `pages/login/login.wxss` |
| 登录页逻辑 | `pages/login/login.js` |
| 年级选择配置 | `pages/grade-select/grade-select.json` |
| 年级选择结构 | `pages/grade-select/grade-select.wxml` |
| 年级选择样式 | `pages/grade-select/grade-select.wxss` |
| 年级选择逻辑 | `pages/grade-select/grade-select.js` |
