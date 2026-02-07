import { ElMessage, ElMessageBox } from 'element-plus'

export function useMessage() {
  const success = (message: string, duration = 3000) => {
    ElMessage({
      message,
      type: 'success',
      duration,
    })
  }

  const error = (message: string, duration = 3000) => {
    ElMessage({
      message,
      type: 'error',
      duration,
    })
  }

  const warning = (message: string, duration = 3000) => {
    ElMessage({
      message,
      type: 'warning',
      duration,
    })
  }

  const info = (message: string, duration = 3000) => {
    ElMessage({
      message,
      type: 'info',
      duration,
    })
  }

  const confirm = (message: string, title = '确认') => {
    return ElMessageBox.confirm(message, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  }

  return {
    success,
    error,
    warning,
    info,
    confirm,
  }
}
