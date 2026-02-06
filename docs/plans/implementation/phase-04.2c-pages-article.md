# Phase 4.2c: 微信小程序 - 文章阅读页

> **前置依赖**: Phase 4.1, Phase 4.2b  
> **本文件范围**: 文章阅读页  
> **参考原型**: `article_reading_view`

---

## 4.2c.1 页面配置 (article.json)

```json
{
  "navigationBarTitleText": "阅读进行中",
  "navigationBarBackgroundColor": "#FFF8E7",
  "navigationBarTextStyle": "black",
  "usingComponents": {}
}
```

---

## 4.2c.2 页面结构 (article.wxml)

```xml
<!-- 文章阅读页 - 参考原型: article_reading_view -->
<view class="page-article">
  <!-- 自定义导航栏 -->
  <view class="nav-bar">
    <view class="nav-left" bindtap="goBack">
      <image src="/images/icons/arrow-left.png" mode="aspectFit" />
    </view>
    
    <view class="nav-center">
      <view class="category-tag">{{article.category}}</view>
      <text class="nav-title">阅读进行中</text>
    </view>
    
    <view class="nav-right" bindtap="showMore">
      <image src="/images/icons/more.png" mode="aspectFit" />
    </view>
  </view>

  <!-- 文章信息条 -->
  <view class="article-meta">
    <text>{{article.grade_text}}</text>
    <text class="divider">|</text>
    <text>{{article.word_count}}字</text>
    <text class="divider">|</text>
    <text>建议用时{{article.estimated_time}}分</text>
    <text class="divider">|</text>
    <text>难度：</text>
    <view class="stars">
      <text 
        wx:for="{{[1,2,3]}}" 
        wx:key="*this"
        class="star {{item <= article.difficulty ? 'active' : ''}}"
      >★</text>
    </view>
    <text wx:if="{{article.has_challenge}}">(含挑战题)</text>
  </view>

  <!-- 文章内容 -->
  <scroll-view 
    class="article-content" 
    scroll-y
    enhanced
    show-scrollbar="{{false}}"
  >
    <!-- 封面图 -->
    <view class="cover-wrapper">
      <image 
        class="cover-image" 
        src="{{article.cover_url}}" 
        mode="aspectFill"
      />
      <view class="fullscreen-icon" bindtap="viewFullImage">
        <image src="/images/icons/fullscreen.png" mode="aspectFit" />
      </view>
    </view>

    <!-- 标题区 -->
    <view class="title-section">
      <text class="article-title">{{article.title}}</text>
      <view class="author-info">
        <text class="category-label">{{article.tags[0]}}</text>
        <text class="author">· 作者：{{article.author}}</text>
      </view>
    </view>

    <!-- 正文内容 -->
    <view class="content-body">
      <block wx:for="{{paragraphs}}" wx:key="index">
        <!-- 普通段落 -->
        <view class="paragraph" wx:if="{{!item.isHighlight}}">
          <image 
            class="paragraph-icon" 
            src="/images/icons/leaf.png" 
            mode="aspectFit"
          />
          <text class="paragraph-text" user-select>{{item.text}}</text>
        </view>
        
        <!-- 知识扩展高亮块 -->
        <view class="highlight-block" wx:if="{{item.isHighlight}}">
          <image 
            class="highlight-icon" 
            src="/images/icons/lightbulb.png" 
            mode="aspectFit"
          />
          <text class="highlight-text">"{{item.text}}"</text>
        </view>
      </block>
    </view>

    <!-- 阅读提示 -->
    <view class="read-tip">
      <image src="/images/icons/lock.png" mode="aspectFit" />
      <text>阅读全文即可解锁答题环节</text>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </scroll-view>

  <!-- 底部操作栏 -->
  <view class="bottom-bar safe-area-bottom">
    <button 
      class="btn-start-quiz"
      bindtap="startQuiz"
      loading="{{starting}}"
    >
      <image src="/images/icons/unlock.png" mode="aspectFit" />
      <text>开始答题</text>
    </button>
  </view>
</view>
```

---

## 4.2c.3 页面样式 (article.wxss)

```css
/* 文章阅读页样式 */
.page-article {
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
  background: var(--bg-page);
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

.nav-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.category-tag {
  font-size: 22rpx;
  color: #F5A623;
  background: rgba(245, 166, 35, 0.15);
  padding: 4rpx 16rpx;
  border-radius: 12rpx;
  margin-bottom: 4rpx;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

/* 文章信息条 */
.article-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  padding: 16rpx 30rpx;
  font-size: 24rpx;
  color: #888;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
}

.article-meta .divider {
  margin: 0 12rpx;
  color: #ddd;
}

.stars {
  display: inline-flex;
}

.star {
  font-size: 24rpx;
  color: #ddd;
}

.star.active {
  color: #F5A623;
}

/* 文章内容区 */
.article-content {
  flex: 1;
  padding: 0 30rpx;
}

/* 封面图 */
.cover-wrapper {
  position: relative;
  width: 100%;
  height: 400rpx;
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 20rpx;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.fullscreen-icon {
  position: absolute;
  right: 20rpx;
  bottom: 20rpx;
  width: 60rpx;
  height: 60rpx;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-icon image {
  width: 32rpx;
  height: 32rpx;
}

/* 标题区 */
.title-section {
  padding: 30rpx 0;
}

.article-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  line-height: 1.4;
  display: block;
  margin-bottom: 16rpx;
}

.author-info {
  display: flex;
  align-items: center;
}

.category-label {
  font-size: 24rpx;
  color: #F5A623;
}

.author {
  font-size: 24rpx;
  color: #888;
  margin-left: 8rpx;
}

/* 正文内容 */
.content-body {
  padding-bottom: 40rpx;
}

.paragraph {
  display: flex;
  align-items: flex-start;
  margin-bottom: 32rpx;
}

.paragraph-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 16rpx;
  margin-top: 8rpx;
  flex-shrink: 0;
}

.paragraph-text {
  font-size: 34rpx;
  line-height: 1.8;
  color: #333;
  text-align: justify;
}

/* 知识扩展高亮块 */
.highlight-block {
  background: linear-gradient(135deg, #FFF9EE 0%, #FFF5E0 100%);
  border-left: 6rpx solid #F5A623;
  padding: 24rpx 30rpx;
  margin: 30rpx 0;
  border-radius: 0 16rpx 16rpx 0;
}

.highlight-icon {
  width: 36rpx;
  height: 36rpx;
  margin-bottom: 12rpx;
}

.highlight-text {
  font-size: 30rpx;
  line-height: 1.7;
  color: #D48806;
  font-style: italic;
}

/* 阅读提示 */
.read-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  color: #999;
  font-size: 26rpx;
}

.read-tip image {
  width: 32rpx;
  height: 32rpx;
  margin-right: 12rpx;
}

/* 底部占位 */
.bottom-placeholder {
  height: 160rpx;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx 40rpx 40rpx;
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.btn-start-quiz {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 96rpx;
  background: linear-gradient(90deg, #FEE4B3 0%, #FFFFFF 100%);
  border: 2rpx solid #F5A623;
  border-radius: 48rpx;
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

.btn-start-quiz::after {
  border: none;
}

.btn-start-quiz image {
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
}
```

---

## 4.2c.4 页面逻辑 (article.js)

```javascript
const app = getApp()
const articleService = require('../../services/articleService')
const progressService = require('../../services/progressService')

Page({
  data: {
    articleId: null,
    article: null,
    paragraphs: [],
    loading: true,
    starting: false,
  },

  onLoad(options) {
    const articleId = options.id
    if (!articleId) {
      wx.showToast({ title: '文章不存在', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }

    this.setData({ articleId })
    this.loadArticle(articleId)
  },

  // 加载文章详情
  async loadArticle(articleId) {
    this.setData({ loading: true })

    try {
      const article = await articleService.getArticleDetail(articleId)
      
      // 解析段落
      const paragraphs = this.parseParagraphs(article.content)
      
      // 年级文案映射
      const gradeTextMap = {
        'GRADE_1': '1年级', 'GRADE_2': '2年级', 'GRADE_3': '3年级',
        'GRADE_4': '4年级', 'GRADE_5': '5年级', 'GRADE_6': '6年级',
      }

      this.setData({
        article: {
          ...article,
          grade_text: gradeTextMap[article.grade] || article.grade,
          estimated_time: Math.ceil(article.word_count / 100), // 假设每分钟100字
          has_challenge: article.difficulty >= 3,
        },
        paragraphs,
        loading: false,
      })

      // 更新导航栏标题
      wx.setNavigationBarTitle({ title: article.title })

    } catch (error) {
      console.error('加载文章失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ loading: false })
    }
  },

  // 解析段落（识别高亮块）
  parseParagraphs(content) {
    if (!content) return []
    
    // 按换行分割
    const lines = content.split('\n').filter(line => line.trim())
    
    return lines.map(line => {
      // 检测是否是高亮内容（用【】包裹）
      const highlightMatch = line.match(/^【(.+)】$/)
      if (highlightMatch) {
        return {
          text: highlightMatch[1],
          isHighlight: true
        }
      }
      return {
        text: line,
        isHighlight: false
      }
    })
  },

  // 开始答题
  async startQuiz() {
    if (this.data.starting) return

    this.setData({ starting: true })

    try {
      // 创建阅读进度记录
      const progress = await progressService.startReading(this.data.articleId)
      
      // 保存到全局状态
      app.setCurrentProgress(progress.id, this.data.articleId)

      // 跳转答题页
      wx.navigateTo({
        url: `/pages/quiz/quiz?progressId=${progress.id}&articleId=${this.data.articleId}`
      })

    } catch (error) {
      console.error('开始答题失败:', error)
      wx.showToast({ title: '开始答题失败', icon: 'none' })
    } finally {
      this.setData({ starting: false })
    }
  },

  // 返回
  goBack() {
    wx.navigateBack()
  },

  // 查看大图
  viewFullImage() {
    if (this.data.article?.cover_url) {
      wx.previewImage({
        urls: [this.data.article.cover_url]
      })
    }
  },

  // 更多操作
  showMore() {
    wx.showActionSheet({
      itemList: ['分享给朋友', '收藏文章', '举报问题'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            // 分享
            break
          case 1:
            wx.showToast({ title: '已收藏', icon: 'success' })
            break
          case 2:
            wx.showToast({ title: '感谢反馈', icon: 'none' })
            break
        }
      }
    })
  },

  // 分享
  onShareAppMessage() {
    return {
      title: this.data.article?.title || '阅读星球',
      path: `/pages/article/article?id=${this.data.articleId}`,
      imageUrl: this.data.article?.cover_url
    }
  },
})
```

---

## 4.2c.5 验收标准

### 视觉验收

- [ ] 顶部显示分类标签（如"科普知识"）
- [ ] 信息条显示年级、字数、用时、难度星星
- [ ] 封面图圆角显示，有全屏查看按钮
- [ ] 正文段落前有叶子图标
- [ ] 知识扩展块为黄色高亮样式
- [ ] 底部"开始答题"按钮样式正确

### 功能验收

- [ ] 正确加载文章内容
- [ ] 点击封面可查看大图
- [ ] 点击开始答题创建进度并跳转
- [ ] 支持分享功能
- [ ] 返回按钮正常工作

---

## 4.2c.6 交付物清单

| 交付物 | 文件路径 |
|--------|----------|
| 文章页配置 | `pages/article/article.json` |
| 文章页结构 | `pages/article/article.wxml` |
| 文章页样式 | `pages/article/article.wxss` |
| 文章页逻辑 | `pages/article/article.js` |
