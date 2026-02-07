<template>
  <div class="user-detail">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
      <h2>用户详情</h2>
    </div>

    <el-card v-loading="loading" class="user-info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <div class="user-profile">
        <el-avatar :size="80" :src="userDetail?.avatar">
          {{ userDetail?.username.charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="user-basic">
          <h3>{{ userDetail?.nickname || userDetail?.username }}</h3>
          <p>@{{ userDetail?.username }}</p>
          <div class="user-level">
            <el-tag :type="getLevelTagType(userDetail?.level || 1)">
              Lv.{{ userDetail?.level }}
            </el-tag>
            <span class="points">{{ userDetail?.total_points }} 积分</span>
          </div>
        </div>
      </div>
      <el-descriptions :column="2" border class="user-descriptions">
        <el-descriptions-item label="用户ID">{{ userDetail?.id }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userDetail?.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="个人简介" :span="2">
          {{ userDetail?.bio || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(userDetail?.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ formatDate(userDetail?.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-loading="loading" class="stats-card">
      <template #header>
        <div class="card-header">
          <span>阅读统计</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userDetail?.reading_stats?.total_articles_read || 0 }}</div>
            <div class="stat-label">阅读文章数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userDetail?.reading_stats?.total_reading_time || 0 }}</div>
            <div class="stat-label">阅读时长(分钟)</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userDetail?.reading_stats?.total_questions_answered || 0 }}</div>
            <div class="stat-label">答题总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ ((userDetail?.reading_stats?.correct_rate || 0) * 100).toFixed(1) }}%</div>
            <div class="stat-label">正确率</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userDetail?.reading_stats?.current_streak || 0 }}</div>
            <div class="stat-label">当前连续打卡</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ userDetail?.reading_stats?.longest_streak || 0 }}</div>
            <div class="stat-label">最长连续打卡</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-loading="loading" class="badges-card">
      <template #header>
        <div class="card-header">
          <span>获得徽章</span>
        </div>
      </template>
      <div v-if="userDetail?.badges && userDetail.badges.length > 0" class="badges-list">
        <div v-for="badge in userDetail.badges" :key="badge.id" class="badge-item">
          <div class="badge-icon">{{ badge.icon }}</div>
          <div class="badge-info">
            <div class="badge-name">{{ badge.name }}</div>
            <div class="badge-desc">{{ badge.description }}</div>
            <div class="badge-date">获得时间: {{ formatDate(badge.earned_at) }}</div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无徽章" />
    </el-card>

    <el-card v-loading="loading" class="activities-card">
      <template #header>
        <div class="card-header">
          <span>最近活动</span>
        </div>
      </template>
      <div v-if="userDetail?.recent_activities && userDetail.recent_activities.length > 0" class="activities-list">
        <div v-for="activity in userDetail.recent_activities" :key="activity.id" class="activity-item">
          <div class="activity-type">{{ activity.type }}</div>
          <div class="activity-description">{{ activity.description }}</div>
          <div class="activity-time">{{ formatDate(activity.created_at) }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无活动记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getUserDetail, UserDetail } from '@/api/users'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const userDetail = ref<UserDetail | null>(null)

const formatDate = (date: string | undefined) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getLevelTagType = (level: number) => {
  if (level >= 10) return 'danger'
  if (level >= 5) return 'warning'
  if (level >= 3) return 'success'
  return 'info'
}

const loadUserDetail = async () => {
  const userId = Number(route.params.id)
  if (!userId) {
    ElMessage.error('用户ID无效')
    return
  }

  loading.value = true
  try {
    const data = await getUserDetail(userId)
    userDetail.value = data
  } catch (error) {
    ElMessage.error('加载用户详情失败，请稍后重试')
    console.error('Failed to load user detail:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/users')
}

onMounted(() => {
  loadUserDetail()
})
</script>

<style lang="scss" scoped>
.user-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;

  h2 {
    margin: 0;
  }
}

.user-info-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.user-basic {
  flex: 1;

  h3 {
    margin: 0 0 4px 0;
    font-size: 18px;
    color: #303133;
  }

  p {
    margin: 0 0 8px 0;
    color: #909399;
  }

  .user-level {
    display: flex;
    align-items: center;
    gap: 12px;

    .points {
      color: #f56c6c;
      font-weight: 500;
    }
  }
}

.user-descriptions {
  margin-top: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px 0;

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #409eff;
    margin-bottom: 8px;
  }

  .stat-label {
    font-size: 14px;
    color: #909399;
  }
}

.badges-card {
  margin-bottom: 20px;
}

.badges-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.badge-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .badge-icon {
    font-size: 32px;
    flex-shrink: 0;
  }

  .badge-info {
    flex: 1;
    min-width: 0;

    .badge-name {
      font-weight: 600;
      font-size: 16px;
      color: #303133;
      margin-bottom: 4px;
    }

    .badge-desc {
      font-size: 14px;
      color: #606266;
      margin-bottom: 4px;
      line-height: 1.5;
    }

    .badge-date {
      font-size: 12px;
      color: #909399;
    }
  }
}

.activities-card {
  margin-bottom: 20px;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;

  .activity-type {
    flex-shrink: 0;
    padding: 4px 8px;
    background-color: #ecf5ff;
    color: #409eff;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
  }

  .activity-description {
    flex: 1;
    font-size: 14px;
    color: #606266;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .activity-time {
    flex-shrink: 0;
    font-size: 12px;
    color: #909399;
    white-space: nowrap;
  }
}
</style>
