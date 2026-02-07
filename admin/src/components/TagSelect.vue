<template>
  <el-select
    v-model="selectedTags"
    multiple
    :placeholder="placeholder"
    :disabled="loading"
    style="width: 100%"
    @change="handleChange"
  >
    <el-option
      v-for="tag in tags"
      :key="tag.id"
      :label="tag.name"
      :value="tag.id"
    >
      <div class="tag-option">
        <el-tag v-if="tag.color" :color="tag.color" size="small">
          {{ tag.category }}
        </el-tag>
        <el-tag v-else :type="getTagCategoryType(tag.category)" size="small">
          {{ tag.category }}
        </el-tag>
        <span>{{ tag.name }}</span>
      </div>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getTagList, type Tag } from '@/api/tags'

interface Props {
  modelValue: number[]
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: number[]): void
  (e: 'change', value: number[]): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择标签'
})

const emit = defineEmits<Emits>()

const tags = ref<Tag[]>([])
const loading = ref(false)
const selectedTags = ref<number[]>([])

const getTagCategoryType = (category: string) => {
  const map: Record<string, string> = {
    '主题': 'primary',
    '难度': 'warning',
    '类型': 'success',
    '其他': 'info'
  }
  return map[category] || ''
}

const loadTags = async () => {
  loading.value = true
  try {
    const data = await getTagList({ page: 1, page_size: 100 })
    tags.value = data.items
  } catch (error) {
    ElMessage.error('加载标签失败，请稍后重试')
    console.error('Failed to load tags:', error)
  } finally {
    loading.value = false
  }
}

const handleChange = (value: number[]) => {
  emit('update:modelValue', value)
  emit('change', value)
}

watch(() => props.modelValue, (newValue) => {
  selectedTags.value = [...newValue]
}, { immediate: true })

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-option {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
