<template>
  <div class="question-list">
    <div class="page-header">
      <h2>题目管理</h2>
      <el-button type="primary" @click="goToCreate">
        <el-icon><Plus /></el-icon>
        创建题目
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="题目类型">
          <el-select v-model="filters.question_type" clearable placeholder="全部">
            <el-option label="选择题" value="multiple_choice" />
            <el-option label="填空题" value="fill_in_blank" />
            <el-option label="判断题" value="true_false" />
            <el-option label="简答题" value="short_answer" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索题目内容" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="content" label="题目内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="article_id" label="文章ID" width="100" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="选项" min-width="200">
          <template #default="{ row }">
            <span v-if="row.options && row.options.length">{{ row.options.join(', ') }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="correct_answer" label="正确答案" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="goToEdit(row.id)">
              编辑
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
import { getQuestionList, deleteQuestion, Question } from '@/api/questions'

const router = useRouter()

const list = ref<Question[]>([])
const loading = ref(false)

const filters = reactive({
  question_type: '',
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    multiple_choice: '选择题',
    fill_in_blank: '填空题',
    true_false: '判断题',
    short_answer: '简答题',
  }
  return map[type] || type
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await getQuestionList({
      page: pagination.page,
      page_size: pagination.pageSize,
      question_type: filters.question_type || undefined,
    })
    list.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载数据失败，请稍后重试')
    console.error('Failed to load questions:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.question_type = ''
  filters.keyword = ''
  pagination.page = 1
  loadData()
}

const handleDelete = async (row: Question) => {
  try {
    await ElMessageBox.confirm('确定要删除这道题目吗？删除后无法恢复！', '警告', { type: 'warning' })
    await deleteQuestion(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
      console.error('Failed to delete question:', error)
    }
  }
}

const goToCreate = () => {
  router.push('/questions/create')
}

const goToEdit = (id: number) => {
  router.push(`/questions/${id}/edit`)
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.question-list {
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
