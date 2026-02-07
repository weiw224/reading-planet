<template>
  <QuillEditor
    v-model:content="localContent"
    content-type="html"
    :placeholder="placeholder"
    :style="{ minHeight }"
    :toolbar="toolbar"
    @update:content="handleUpdate"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

interface Props {
  modelValue: string
  placeholder?: string
  minHeight?: string
  toolbar?: unknown[]
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入内容...',
  minHeight: '300px',
  toolbar: () => [
    ['bold', 'italic', 'underline', 'strike'],
    ['blockquote', 'code-block'],
    [{ list: 'ordered' }, { list: 'bullet' }],
    [{ indent: '-1' }, { indent: '+1' }],
    [{ size: ['small', false, 'large', 'huge'] }],
    [{ header: [1, 2, 3, 4, 5, 6, false] }],
    [{ color: [] }, { background: [] }],
    [{ align: [] }],
    ['link', 'image', 'clean'],
  ],
})

const emit = defineEmits<{
  update: [value: string]
}>()

const localContent = ref(props.modelValue)

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== localContent.value) {
      localContent.value = newValue
    }
  }
)

const handleUpdate = (content: string): void => {
  emit('update', content)
}
</script>

<style scoped>
:deep(.ql-editor) {
  min-height: v-bind(minHeight);
  font-size: 14px;
}
</style>
