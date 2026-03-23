<template>
  <div class="min-h-screen p-6 space-y-6">
    <header class="flex items-center justify-between pb-4 border-b border-gray-800">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Activity class="w-6 h-6 text-green-500" />
          eBay Sleep Guard <span class="text-sm font-normal text-gray-500 ml-2">v1.5 商业主控台</span>
        </h1>
        <p class="text-sm text-gray-400 mt-1">系统运行状态：🟢 监控引擎活跃中</p>
      </div>
      <div class="flex gap-4">
        <button @click="$router.push('/tasks')" class="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors flex items-center gap-2">
          进入监控矩阵
        </button>
        <button @click="refreshData" class="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-md transition-colors flex items-center gap-2">
          <RefreshCw class="w-4 h-4" :class="{'animate-spin': isRefreshing}" />
          手动同步
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-lg">
        <h3 class="text-gray-400 text-sm font-medium mb-2">活跃监控任务 (Active Tasks)</h3>
        <p class="text-3xl font-bold text-white">{{ stats.active_tasks }}</p>
      </div>
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-lg">
        <h3 class="text-gray-400 text-sm font-medium mb-2">今日拦截异常 (Today's Alerts)</h3>
        <p class="text-3xl font-bold text-red-400">{{ stats.today_alerts }}</p>
      </div>
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-lg">
        <h3 class="text-gray-400 text-sm font-medium mb-2">累计战果 (Total Hunts)</h3>
        <p class="text-3xl font-bold text-green-400">{{ stats.total_alerts }}</p>
      </div>
    </div>

    <div class="bg-black border border-gray-700 rounded-lg shadow-2xl overflow-hidden flex flex-col h-[500px]">
      <div class="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
        <span class="text-xs font-mono text-gray-400">root@ebay-guard-engine:~# tail -f /var/log/hunter.log</span>
        <div class="flex gap-2">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
      </div>

      <div class="p-4 font-mono text-sm overflow-y-auto no-scrollbar flex-1 space-y-2">
        <div v-if="logs.length === 0" class="text-gray-500 italic">Waiting for incoming alerts...</div>

        <div v-for="log in logs" :key="log.id" class="animate-fade-in-up">
          <span class="text-gray-500">[{{ log.created_at }}]</span>
          <span class="text-blue-400 ml-2">[Item: {{ log.item_id }}]</span>

          <span v-if="log.alert_type === 'price_drop'" class="text-red-400 ml-2 font-bold">
            [破价警报] {{ log.message }}
          </span>
          <span v-else-if="log.alert_type === 'offline'" class="text-yellow-400 ml-2 font-bold">
            [下架警报] {{ log.message }}
          </span>
          <span v-else class="text-gray-300 ml-2">
            [{{ log.alert_type }}] {{ log.message }}
          </span>

          <span v-if="log.is_pushed" class="text-green-500 text-xs ml-2">(已推送企微/Bark)</span>
          <span v-else class="text-gray-600 text-xs ml-2">(冷却静默拦截)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Activity, RefreshCw } from 'lucide-vue-next'
import api from '../api/request' // 引入咱们之前封装的 Axios

const stats = ref({ active_tasks: 0, total_alerts: 0, today_alerts: 0 })
const logs = ref([])
const isRefreshing = ref(false)
let pollInterval = null

const fetchStats = async () => {
  try {
    const res = await api.get('/stats/')
    stats.value = res
  } catch (error) {
    console.error("拿不到大盘数据", error)
  }
}

const fetchLogs = async () => {
  try {
    const res = await api.get('/logs/?limit=20')
    logs.value = res
  } catch (error) {
    console.error("拿不到日志", error)
  }
}

const refreshData = async () => {
  isRefreshing.value = true
  await Promise.all([fetchStats(), fetchLogs()])
  setTimeout(() => { isRefreshing.value = false }, 500)
}

// 页面加载时执行，并且设置定时器每 5 秒自动刷一次（录视频的时候看着数据自己跳最帅）
onMounted(() => {
  refreshData()
  pollInterval = setInterval(refreshData, 5000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
})
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>