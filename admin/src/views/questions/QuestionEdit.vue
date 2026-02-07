<template>
  <div class="question-edit">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <h2>编辑题目</h2>
      </template>
    </el-page-header>

    <el-card>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="所属文章" prop="article_id">
          <el-select
            v-model="formData.article_id"
            placeholder="请选择文章"
            style="width: 100%"
            filterable
            clearable
          >
            <el-option
              v-for="article in articles"
              :key="article.id"
              :label="article.title"
              :value="article.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="题目类型" prop="type">
          <el-select
            v-model="formData.type"
            placeholder="请选择题目类型"
            style="width: 100%"
          >
            <el-option label="选择题" value="multiple_choice" />
            <el-option label="填空题" value="fill_in_blank" />
            <el-option label="判断题" value="true_false" />
            <el-option label="简答题" value="short_answer" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="formData.type === 'multiple_choice' || formData.type === 'true_false'"
          label="选项"
          prop="options"
        >
          <div v-for="(option, index) in formData.options" :key="index" class="option-item">
            <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
            <el-input
              v-model="formData.options[index]"
              :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
              maxlength="200"
            />
            <el-button
              type="danger"
              :icon="Delete"
              circle
              size="small"
              @click="removeOption(index)"
              v-if="formData.options.length > 2"
            />
          </div>
          <el-button
            type="primary"
            :icon="Plus"
            @click="addOption"
            v-if="formData.options.length < 8"
            class="add-option-btn"
          >
            添加选项
          </el-button>
        </el-form-item>

        <el-form-item
          v-if="formData.type === 'multiple_choice'"
          label="正确答案"
          prop="correct_answer"
        >
          <el-radio-group v-model="formData.correct_answer">
            <el-radio
              v-for="(option, index) in formData.options"
              :key="index"
              :label="index"
            >
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="formData.type === 'true_false'"
          label="正确答案"
          prop="correct_answer"
        >
          <el-radio-group v-model="formData.correct_answer">
            <el-radio :label="0">正确</el-radio>
            <el-radio :label="1">错误</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="formData.type === 'fill_in_blank' || formData.type === 'short_answer'"
          label="正确答案"
          prop="correct_answer"
        >
          <el-input
            v-model="correctAnswerText"
            type="textarea"
            :rows="2"
            placeholder="请输入正确答案"
            maxlength="200"
            show-word-limit
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getQuestion, updateQuestion, type QuestionCreateParams, type Question } from '@/api/questions'
import { getArticleList, type Article } from '@/api/articles'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const articles = ref<Article[]>([])
const questionId = ref<number>()

const formData = reactive<QuestionCreateParams>({
  content: '',
  article_id: 0,
  type: 'multiple_choice',
  options: ['', ''],
  correct_answer: 0,
})

const correctAnswerText = computed({
  get: () => String(formData.correct_answer),
  set: (value: string) => {
    formData.correct_answer = parseInt(value, 10) || 0
  },
})

const rules: FormRules = {
  content: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { min: 5, max: 500, message: '内容长度在 5 到 500 个字符', trigger: 'blur' },
  ],
  article_id: [
    { required: true, message: '请选择所属文章', trigger: 'change', type: 'number' },
  ],
  type: [
    { required: true, message: '请选择题目类型', trigger: 'change' },
  ],
  options: [
    {
      validator: (rule, value, callback) => {
        if (formData.type === 'multiple_choice' || formData.type === 'true_false') {
          const minOptions = formData.type === 'true_false' ? 2 : 2
          if (value.length < minOptions) {
            callback(new Error(`至少需要 ${minOptions} 个选项`))
            return
          }
          const hasEmpty = value.some((opt: string) => !opt.trim())
          if (hasEmpty) {
            callback(new Error('所有选项都不能为空'))
            return
          }
        }
        callback()
      },
      trigger: 'change',
    },
  ],
  correct_answer: [
    { required: true, message: '请设置正确答案', trigger: 'change', type: 'number' },
  ],
}

const loadQuestion = async (id: number) => {
  loading.value = true
  try {
    const question = await getQuestion(id)
    questionId.value = question.id
    
    formData.content = question.content
    formData.article_id = question.article_id
    formData.type = question.type
    formData.options = question.options.length > 0 ? question.options : ['', '']
    formData.correct_answer = question.correct_answer
  } catch (error) {
    ElMessage.error('加载题目失败，请稍后重试')
    console.error('Failed to load question:', error)
    goBack()
  } finally {
    loading.value = false
  }
}

const loadArticles = async () => {
  try {
    const data = await getArticleList({ page: 1, page_size: 100 })
    articles.value = data.items
  } catch (error) {
    ElMessage.error('加载文章列表失败，请稍后重试')
    console.error('Failed to load articles:', error)
  }
}

const addOption = () => {
  formData.options.push('')
}

const removeOption = (index: number) => {
  formData.options.splice(index, 1)
  if (formData.correct_answer >= formData.options.length) {
    formData.correct_answer = formData.options.length - 1
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

  if (!questionId.value) {
    ElMessage.error('题目ID不存在')
    return
  }

  submitting.value = true
  try {
    const submitData: Partial<QuestionCreateParams> = {
      content: formData.content,
      article_id: formData.article_id,
      type: formData.type,
      options: formData.type === 'multiple_choice' || formData.type === 'true_false'
        ? formData.options
        : [],
      correct_answer: formData.correct_answer,
    }
    await updateQuestion(questionId.value, submitData)
    ElMessage.success('题目保存成功')
    goBack()
  } catch (error) {
    ElMessage.error('保存失败，请稍后重试')
    console.error('Failed to update question:', error)
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/questions')
}

onMounted(() => {
  const id = Number(route.params.id)
  if (id) {
    loadQuestion(id)
  } else {
    ElMessage.error('无效的题目ID')
    goBack()
  }
  loadArticles()
})
</script>

<style lang="scss" scoped>
.question-edit {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;

  h2 {
    margin: 0;
  }
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;

  .option-label {
    min-width: 30px;
    font-weight: bold;
  }
}

.add-option-btn {
  margin-top: 10px;
}
</style>
