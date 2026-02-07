<template>
  <div class="tag-list">
    <div class="page-header">
      <h2>标签管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建标签
      </el-button>
    </div>

    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.color" :color="row.color" size="small">
              {{ row.category }}
            </el-tag>
            <el-tag v-else :type="getCategoryType(row.category)" size="small">
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
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
          <el-input v-model="form.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
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
import { getTagList, createTag, updateTag, deleteTag, type Tag, type TagCreateParams } from '@/api/tags'

const list = ref<Tag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const categories = ['主题', '难度', '类型', '其他']

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const form = reactive<TagCreateParams & { id?: number }>({
  name: '',
  category: '',
  description: '',
  color: '',
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => editingId.value ? '编辑标签' : '创建标签')

const getCategoryType = (category: string) => {
  const map: Record<string, string> = {
    '主题': 'primary',
    '难度': 'warning',
    '类型': 'success',
    '其他': 'info'
  }
  return map[category] || ''
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await getTagList({
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    list.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载数据失败，请稍后重试')
    console.error('Failed to load tags:', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingId.value = null
  dialogVisible.value = true
}

const handleEdit = (row: Tag) => {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    category: row.category,
    description: row.description || '',
    color: row.color || '',
  })
  dialogVisible.value = true
}

const handleDelete = async (row: Tag) => {
  try {
    await ElMessageBox.confirm('确定要删除这个标签吗？删除后无法恢复！', '警告', { type: 'warning' })
    await deleteTag(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
      console.error('Failed to delete tag:', error)
    }
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    category: '',
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
      category: form.category,
      description: form.description || undefined,
      color: form.color || undefined,
    }

    if (editingId.value) {
      await updateTag(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createTag(data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(editingId.value ? '更新失败，请稍后重试' : '创建失败，请稍后重试')
    console.error('Failed to save tag:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.tag-list {
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

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style>
