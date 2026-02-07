<template>
  <el-select
    v-model="selectedAbility"
    :placeholder="placeholder"
    style="width: 100%"
    @change="handleChange"
  >
    <el-option
      v-for="ability in abilities"
      :key="ability"
      :label="ability"
      :value="ability"
    />
  </el-select>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择能力'
})

const emit = defineEmits<Emits>()

const abilities = ['理解', '应用', '分析', '评价'] as const
const selectedAbility = ref<string>('')

const handleChange = (value: string) => {
  emit('update:modelValue', value)
  emit('change', value)
}

watch(() => props.modelValue, (newValue) => {
  selectedAbility.value = newValue
}, { immediate: true })
</script>
