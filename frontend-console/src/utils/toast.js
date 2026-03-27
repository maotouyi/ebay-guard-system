import { ref } from 'vue'

export const toasts = ref([])

let toastId = 0

export const useToast = () => {
  const showToast = (message, type = 'success', duration = 3000) => {
    const id = toastId++
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index > -1) toasts.value.splice(index, 1)
  }

  const success = (msg) => showToast(msg, 'success')
  const error = (msg) => showToast(msg, 'error')
  const warning = (msg) => showToast(msg, 'warning')
  const info = (msg) => showToast(msg, 'info')

  return { success, error, warning, info }
}