import { ref, computed } from 'vue'

export function usePagination(defaultPageSize = 10) {
  const currentPage = ref(1)
  const pageSize = ref(defaultPageSize)
  const total = ref(0)
  const pageSizeOptions = ref([10, 20, 50, 100])

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
  }

  const setTotal = (totalValue: number) => {
    total.value = totalValue
  }

  const reset = () => {
    currentPage.value = 1
    pageSize.value = defaultPageSize
    total.value = 0
  }

  return {
    currentPage,
    pageSize,
    total,
    pageSizeOptions,
    totalPages,
    setCurrentPage,
    setPageSize,
    setTotal,
    reset,
  }
}
