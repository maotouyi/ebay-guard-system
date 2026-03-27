<template>
  <div class="p-8 space-y-8">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter">数据大盘</h1>
        <p class="text-gray-400 mt-2">实时监控引擎 · 累计拦截 {{ stats.total_alerts || 0 }} 次异常</p>
      </div>
      <button @click="refreshAll" :disabled="refreshing" class="flex items-center gap-2 bg-white/5 hover:bg-white/10 backdrop-blur-xl px-6 py-3 rounded-2xl border border-white/10 transition-all disabled:opacity-50">
        <RefreshCw :class="{ 'animate-spin': refreshing }" class="w-5 h-5" />
        {{ refreshing ? '同步中...' : '立即刷新' }}
      </button>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-3xl rounded-full"></div>
        <div class="text-6xl font-bold text-white relative z-10">{{ stats.active_tasks || 0 }}</div>
        <div class="text-gray-400 mt-2 relative z-10">活跃监控任务</div>
      </div>
      <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-3xl rounded-full"></div>
        <div class="text-6xl font-bold text-white relative z-10">{{ stats.total_clients || 0 }}</div>
        <div class="text-gray-400 mt-2 relative z-10">服务客户数</div>
      </div>
      <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-red-500/10 blur-3xl rounded-full"></div>
        <div class="text-6xl font-bold text-white relative z-10">{{ stats.total_alerts || 0 }}</div>
        <div class="text-gray-400 mt-2 relative z-10">累计报警拦截</div>
      </div>
    </div>

    <div class="bg-[#0a0a0a] border border-white/10 rounded-3xl overflow-hidden shadow-2xl h-[450px] flex flex-col">
      <div class="bg-[#111] px-6 py-4 border-b border-white/5 flex items-center justify-between font-mono text-xs">
        <span class="text-green-500">root@ebay-guard-engine:~# tail -f /var/log/hunter.log</span>
        <div class="flex gap-2">
          <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
        </div>
      </div>
      <div ref="logContainer" class="flex-1 p-6 font-mono text-sm overflow-y-auto no-scrollbar space-y-3 text-gray-300 scroll-smooth">
        <div v-if="logs.length === 0" class="text-gray-600 italic animate-pulse">Waiting for engine events...</div>
        <div v-for="log in logs" :key="log.id" class="animate-fade-in flex gap-4 break-words">
          <span class="text-gray-600 whitespace-nowrap">[{{ formatDate(log.created_at) }}]</span>
          <span class="text-blue-400 whitespace-nowrap">[Task ID: {{ log.task_id }}]</span>
          <span :class="{
            'text-red-400': log.alert_type === 'price_drop' || log.alert_type === 'offline',
            'text-yellow-400': log.alert_type === 'rank_not_found',
            'text-purple-400': log.alert_type === 'error'
          }" class="font-bold flex-1">
            {{ log.message }}
          </span>
          <span v-if="log.is_pushed" class="whitespace-nowrap text-[10px] bg-green-900/50 border border-green-500/30 text-green-400 px-2 py-1 rounded self-start">已推送 Bark</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { alertsApi } from '../api/alerts'
import { useToast } from '../utils/toast'

const { success } = useToast()
const stats = ref({})
const logs = ref([])
const logContainer = ref(null)
let pollTimer = null
const refreshing = ref(false)

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

const fetchAll = async (isManual = false) => {
  if (isManual) refreshing.value = true
  try {
    const [sRes, lRes] = await Promise.all([
      alertsApi.getDashboardStats(),
      alertsApi.getAlertLogs(50) // 获取最近50条
    ])
    stats.value = sRes
    // 日志逆序排列，让最新的在最下面
    logs.value = lRes.reverse()
    if (isManual) success('大盘数据已同步')
  } catch (e) {
    // 错误已由 request.js 拦截
  } finally {
    if (isManual) refreshing.value = false
  }
}

const refreshAll = () => fetchAll(true)

// 监听 logs 变化，自动滚动到底部
watch(logs, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}, { deep: true })

onMounted(() => {
  fetchAll()
  pollTimer = setInterval(() => fetchAll(false), 5000) // 5秒轮询
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>