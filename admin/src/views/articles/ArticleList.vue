<template>
  <div class="article-list">
    <div class="page-header">
      <h2>文章管理</h2>
      <el-button type="primary" @click="goToCreate">
        <el-icon><Plus /></el-icon>
        创建文章
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索标题" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="source_book" label="来源" width="150" />
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column label="难度" width="100">
          <template #default="{ row }">
            <el-rate :model-value="row.article_difficulty" disabled :max="3" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="100" />
        <el-table-column label="AI生成" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_ai_generated" type="info">AI</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="goToEdit(row.id)">
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              size="small"
              type="success"
              @click="handlePublish(row)"
            >
              发布
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getArticleList, deleteArticle, publishArticle, Article } from '@/api/articles'

const router = useRouter()

const list = ref<Article[]>([])
const loading = ref(false)

const filters = reactive({
  status: '',
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    published: 'success',
    archived: '',
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    published: '已发布',
    archived: '已归档',
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await getArticleList({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined,
    })
    list.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载数据失败，请稍后重试')
    console.error('Failed to load articles:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.keyword = ''
  pagination.page = 1
  loadData()
}

const handlePublish = async (row: Article) => {
  try {
    await ElMessageBox.confirm('确定要发布这篇文章吗？', '提示')
    await publishArticle(row.id)
    ElMessage.success('发布成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败，请稍后重试')
      console.error('Failed to publish article:', error)
    }
  }
}

const handleDelete = async (row: Article) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？删除后无法恢复！', '警告', { type: 'warning' })
    await deleteArticle(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
      console.error('Failed to delete article:', error)
    }
  }
}

const goToCreate = () => {
  router.push('/articles/create')
}

const goToEdit = (id: number) => {
  router.push(`/articles/${id}/edit`)
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.article-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
  }
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
