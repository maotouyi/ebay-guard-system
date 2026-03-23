<template>
  <div class="p-8 space-y-8">
    <!-- Header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter">数据大盘</h1>
        <p class="text-gray-400">实时监控引擎 · 今天已拦截 {{ stats.today_alerts }} 次异常</p>
      </div>
      <button @click="refreshAll" class="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-xl px-6 py-3 rounded-2xl border border-white/10 transition-all">
        <RefreshCw :class="{ 'animate-spin': refreshing }" class="w-5 h-5" />
        立即刷新
      </button>
    </header>

    <!-- 状态卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <div class="text-6xl font-bold text-white">{{ stats.active_tasks }}</div>
        <div class="text-gray-400 mt-2">活跃监控任务</div>
      </div>
      <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <div class="text-6xl font-bold text-white">{{ stats.today_alerts }}</div>
        <div class="text-gray-400 mt-2">今日拦截报警</div>
      </div>
      <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <div class="text-6xl font-bold text-white">{{ stats.total_alerts }}</div>
        <div class="text-gray-400 mt-2">累计战果</div>
      </div>
    </div>

    <!-- ECharts 7天趋势 -->
    <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
      <h3 class="text-lg font-medium mb-6 flex items-center gap-2">7天异常波动趋势 <span class="text-xs bg-green-500/20 text-green-400 px-3 py-1 rounded-full">ECharts</span></h3>
      <div ref="chartRef" class="h-80 w-full"></div>
    </div>

    <!-- 极致终端日志流 -->
    <div class="bg-black border border-white/10 rounded-3xl overflow-hidden shadow-2xl h-[420px] flex flex-col">
      <div class="bg-gray-950 px-6 py-4 border-b border-white/10 flex items-center justify-between font-mono text-xs">
        <span>root@ebay-guard-engine:~# tail -f hunter.log</span>
        <div class="flex gap-2">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
      </div>
      <div ref="logContainer" class="flex-1 p-6 font-mono text-sm overflow-y-auto no-scrollbar space-y-3 text-gray-300">
        <div v-if="logs.length === 0" class="text-gray-500 italic">等待报警日志...</div>
        <div v-for="log in logs" :key="log.id" class="animate-fade-in">
          <span class="text-gray-500">[{{ log.created_at }}]</span>
          <span class="text-blue-400 ml-3">[{{ log.item_id }}]</span>
          <span :class="log.alert_type === 'price_drop' ? 'text-red-400' : 'text-yellow-400'" class="ml-3 font-bold">
            {{ log.message }}
          </span>
          <span v-if="log.is_pushed" class="ml-4 text-xs bg-green-900 text-green-400 px-2 py-0.5 rounded">已推送</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Activity, RefreshCw } from 'lucide-vue-next'
import api from '../api/request'

const stats = ref({ active_tasks: 12, today_alerts: 7, total_alerts: 184 })
const logs = ref([])
const chartRef = ref(null)
let chartInstance = null
let pollTimer = null
const refreshing = ref(false)

const fetchAll = async () => {
  try {
    const [sRes, lRes] = await Promise.all([
      api.get('/stats/'),
      api.get('/logs/?limit=30')
    ])
    stats.value = sRes
    logs.value = lRes
  } catch (e) { console.error(e) }
}

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value, 'dark')
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '5%', right: '5%', bottom: '10%' },
    xAxis: { type: 'category', data: ['03-17','03-18','03-19','03-20','03-21','03-22','03-23'] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#333' } } },
    series: [{
      name: '异常次数',
      type: 'line',
      smooth: true,
      data: [3, 8, 5, 12, 7, 15, 9],
      lineStyle: { color: '#22c55e' },
      areaStyle: { color: 'rgba(34,197,94,0.2)' }
    }]
  }
  chartInstance.setOption(option)
}

// 每5秒刷新（录视频超帅）
const refreshAll = async () => {
  refreshing.value = true
  await fetchAll()
  // 模拟趋势轻微波动
  if (chartInstance) {
    const newData = chartInstance.getOption().series[0].data.map(v => v + Math.floor(Math.random()*3)-1)
    chartInstance.setOption({ series: [{ data: newData }] })
  }
  refreshing.value = false
}

onMounted(() => {
  fetchAll()
  initChart()
  pollTimer = setInterval(refreshAll, 5000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
  if (chartInstance) chartInstance.dispose()
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>