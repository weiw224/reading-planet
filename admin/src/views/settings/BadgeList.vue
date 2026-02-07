<template>
  <div class="badge-list">
    <div class="page-header">
      <h2>勋章管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建勋章
      </el-button>
    </div>

    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="图标" width="80">
          <template #default="{ row }">
            <div class="icon-preview" :style="{ backgroundColor: row.color || '#f5f7fa' }">
              {{ row.icon }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="颜色" width="100">
          <template #default="{ row }">
            <div v-if="row.color" class="color-preview" :style="{ backgroundColor: row.color }" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">
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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入勋章名称" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-select v-model="form.icon" placeholder="请选择图标" style="width: 100%">
            <el-option
              v-for="icon in iconPresets"
              :key="icon"
              :label="icon"
              :value="icon"
            >
              <div class="icon-option">
                <span class="icon-preview-small">{{ icon }}</span>
                <span>{{ icon }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getBadgeList, createBadge, updateBadge, deleteBadge, type Badge, type BadgeCreateParams } from '@/api/badges'

const list = ref<Badge[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const iconPresets = ['🏆', '🥇', '🏅', '⭐', '🔥', '💎', '💪', '🎯', '🌟', '🎨', '🚀', '💡', '🎖️', '🏅']

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const form = reactive<BadgeCreateParams & { id?: number }>({
  name: '',
  icon: '',
  description: '',
  color: '',
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入勋章名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  icon: [
    { required: true, message: '请选择图标', trigger: 'change' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => editingId.value ? '编辑勋章' : '创建勋章')

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await getBadgeList({
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    list.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载数据失败，请稍后重试')
    console.error('Failed to load badges:', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingId.value = null
  dialogVisible.value = true
}

const handleEdit = (row: Badge) => {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    icon: row.icon,
    description: row.description || '',
    color: row.color || '',
  })
  dialogVisible.value = true
}

const handleDelete = async (row: Badge) => {
  try {
    await ElMessageBox.confirm('确定要删除这个勋章吗？删除后无法恢复！', '警告', { type: 'warning' })
    await deleteBadge(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
      console.error('Failed to delete badge:', error)
    }
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    icon: '',
    description: '',
    color: '',
  })
  editingId.value = null
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      name: form.name,
      icon: form.icon,
      description: form.description || undefined,
      color: form.color || undefined,
    }

    if (editingId.value) {
      await updateBadge(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createBadge(data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(editingId.value ? '更新失败，请稍后重试' : '创建失败，请稍后重试')
    console.error('Failed to save badge:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.badge-list {
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

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.icon-preview {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 20px;
  border: 1px solid #dcdfe6;
}

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.icon-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-preview-small {
  font-size: 20px;
}
</style>
