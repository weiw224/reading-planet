<template>
  <div class="article-edit">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <h2>编辑文章</h2>
      </template>
    </el-page-header>

    <el-card>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        v-loading="loading"
      >
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入文章标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="来源书籍" prop="source_book">
          <el-input
            v-model="formData.source_book"
            placeholder="请输入来源书籍（可选）"
            maxlength="100"
          />
        </el-form-item>

        <el-form-item label="来源章节" prop="source_chapter">
          <el-input
            v-model="formData.source_chapter"
            placeholder="请输入来源章节（可选）"
            maxlength="100"
          />
        </el-form-item>

        <el-form-item label="难度" prop="article_difficulty">
          <el-rate
            v-model="formData.article_difficulty"
            :max="3"
            show-text
            :texts="['简单', '中等', '困难']"
          />
        </el-form-item>

        <el-form-item label="是否摘录" prop="is_excerpt">
          <el-switch
            v-model="formData.is_excerpt"
            active-text="是摘录"
            inactive-text="非摘录"
          />
        </el-form-item>

        <el-form-item label="标签" prop="tag_ids">
          <el-select
            v-model="formData.tag_ids"
            multiple
            placeholder="请选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <el-tag :type="getTagCategoryType(tag.category)" size="small">
                {{ tag.category }}
              </el-tag>
              {{ tag.name }}
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <QuillEditor
            v-model:content="formData.content"
            content-type="html"
            theme="snow"
            placeholder="请输入文章内容"
            style="min-height: 400px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { getArticle, updateArticle, type ArticleCreateParams, type Article } from '@/api/articles'
import { getTagList, type Tag } from '@/api/tags'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const tags = ref<Tag[]>([])
const articleId = ref<number>()

const formData = reactive<ArticleCreateParams>({
  title: '',
  content: '',
  source_book: '',
  source_chapter: '',
  is_excerpt: false,
  article_difficulty: 1,
  tag_ids: [],
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 10, message: '内容至少 10 个字符', trigger: 'blur' },
  ],
  article_difficulty: [
    { required: true, message: '请选择文章难度', trigger: 'change' },
  ],
  tag_ids: [
    { required: true, message: '请至少选择一个标签', trigger: 'change', type: 'array' },
  ],
}

const getTagCategoryType = (category: string) => {
  const map: Record<string, string> = {
    '主题': 'primary',
    '难度': 'warning',
    '类型': 'success',
    '其他': 'info',
  }
  return map[category] || ''
}

const loadArticle = async (id: number) => {
  loading.value = true
  try {
    const article = await getArticle(id)
    articleId.value = article.id
    
    formData.title = article.title
    formData.content = article.content
    formData.source_book = article.source_book || ''
    formData.source_chapter = article.source_chapter || ''
    formData.is_excerpt = article.is_excerpt
    formData.article_difficulty = article.article_difficulty
    formData.tag_ids = article.tags.map(tag => tag.id)
  } catch (error) {
    ElMessage.error('加载文章失败，请稍后重试')
    console.error('Failed to load article:', error)
    goBack()
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  try {
    const data = await getTagList({ page: 1, page_size: 100 })
    tags.value = data.items
  } catch (error) {
    ElMessage.error('加载标签失败，请稍后重试')
    console.error('Failed to load tags:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) {
    return
  }

  try {
    const valid = await formRef.value.validate()
    if (!valid) {
      return
    }
  } catch (error) {
    console.error('Form validation failed:', error)
    return
  }

  if (!articleId.value) {
    ElMessage.error('文章ID不存在')
    return
  }

  submitting.value = true
  try {
    await updateArticle(articleId.value, formData)
    ElMessage.success('文章保存成功')
    goBack()
  } catch (error) {
    ElMessage.error('保存失败，请稍后重试')
    console.error('Failed to update article:', error)
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/articles')
}

onMounted(() => {
  const id = Number(route.params.id)
  if (id) {
    loadArticle(id)
  } else {
    ElMessage.error('无效的文章ID')
    goBack()
  }
  loadTags()
})
</script>

<style lang="scss" scoped>
.article-edit {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;

  h2 {
    margin: 0;
  }
}
</style>
