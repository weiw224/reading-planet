<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>
    
    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      type="error"
      :title="error"
      :closable="false"
      show-icon
      class="error-alert"
    />
    
    <!-- 加载中 -->
    <el-empty v-if="loading && !error" description="加载中...">
      <el-icon class="is-loading"><Loading /></el-icon>
    </el-empty>
    
    <!-- 统计卡片 -->
    <el-row v-if="!loading && !error" :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card users">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card articles">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.published_articles }}</div>
            <div class="stat-label">已发布文章</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card readings">
          <div class="stat-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_readings }}</div>
            <div class="stat-label">总阅读量</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card checkins">
          <div class="stat-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.checkins_today }}</div>
            <div class="stat-label">今日打卡</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 更多统计 -->
    <el-row v-if="!loading && !error" :gutter="20" class="more-stats">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>活跃用户</span>
          </template>
          <div class="active-users">
            <div class="active-item">
              <span class="label">今日活跃</span>
              <span class="value">{{ stats.active_users_today }}</span>
            </div>
            <div class="active-item">
              <span class="label">本周活跃</span>
              <span class="value">{{ stats.active_users_week }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>内容统计</span>
          </template>
          <div class="content-stats">
            <div class="content-item">
              <span class="label">文章总数</span>
              <span class="value">{{ stats.total_articles }}</span>
            </div>
            <div class="content-item">
              <span class="label">题目总数</span>
              <span class="value">{{ stats.total_questions }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

 <script setup lang="ts">
 import { ref, onMounted } from 'vue'
 import { ElMessage } from 'element-plus'
 import { User, Document, Reading, Calendar, Loading } from '@element-plus/icons-vue'
 import { getDashboardStats, DashboardStats } from '@/api/dashboard'
 import { useAppStore } from '@/stores/app'

 const appStore = useAppStore()
 const loading = ref(false)
 const error = ref<string | null>(null)

 const stats = ref<DashboardStats>({
   total_users: 0,
   active_users_today: 0,
   active_users_week: 0,
   total_articles: 0,
   published_articles: 0,
   total_questions: 0,
   total_readings: 0,
   checkins_today: 0,
 })

 onMounted(async () => {
   loading.value = true
   error.value = null
   appStore.showLoading('加载仪表盘数据...')
   
   try {
     stats.value = await getDashboardStats()
   } catch (err) {
     console.error('获取仪表盘数据失败:', err)
     error.value = '加载仪表盘数据失败，请稍后重试'
     ElMessage.error('获取仪表盘数据失败')
   } finally {
     loading.value = false
     appStore.hideLoading()
   }
 })
</script>

 <style lang="scss" scoped>
 .dashboard {
   padding: 20px;
 }

 .page-title {
   margin-bottom: 24px;
   font-size: 24px;
   color: #333;
 }

 .error-alert {
   margin-bottom: 24px;
 }

 .el-icon.is-loading {
   font-size: 48px;
   animation: rotating 2s linear infinite;
 }

 @keyframes rotating {
   from {
     transform: rotate(0deg);
   }
   to {
     transform: rotate(360deg);
   }
 }

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  &.users .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
  &.articles .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
  &.readings .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
  &.checkins .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  
  .el-icon {
    font-size: 28px;
    color: white;
  }
}

.stat-content {
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #333;
  }
  
  .stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 4px;
  }
}

.more-stats {
  .active-users, .content-stats {
    display: flex;
    justify-content: space-around;
    padding: 20px 0;
  }
  
  .active-item, .content-item {
    text-align: center;
    
    .label {
      display: block;
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
    }
    
    .value {
      font-size: 32px;
      font-weight: 600;
      color: #409EFF;
    }
  }
}
</style>
