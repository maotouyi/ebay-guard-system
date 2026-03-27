<template>
  <div class="p-8 space-y-8 bg-gray-950">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter flex items-center gap-3">
          <Target class="w-10 h-10 text-blue-500" /> 监控矩阵
        </h1>
        <p class="text-gray-400 mt-2">价格防卫 · 排名监控 · 实时部署哨兵</p>
      </div>
    </header>

    <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl">
      <h3 class="text-xl font-bold mb-6 flex items-center gap-2 text-white">
        <Plus class="w-6 h-6 text-blue-500" /> 部署新哨兵
      </h3>
      <form @submit.prevent="submitTask" class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">归属客户 ID</label>
          <input v-model="newTask.client_id" type="number" required class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all" placeholder="输入客户ID" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">eBay Item ID</label>
          <input v-model="newTask.item_id" type="text" required class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all" placeholder="12位商品编号" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">监控引擎类型</label>
          <select v-model="newTask.monitor_type" class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all appearance-none">
            <option value="price">🚨 价格跌破防卫</option>
            <option value="rank">📊 自然排名监控</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">巡逻频率</label>
          <select v-model="newTask.check_interval" class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all appearance-none">
            <option :value="5">⚡ 激进 (5分钟)</option>
            <option :value="15">🏃 标准 (15分钟)</option>
            <option :value="30">🚶 常规 (30分钟)</option>
          </select>
        </div>

        <div v-if="newTask.monitor_type === 'price'" class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-400 mb-2">破价防守线 (USD $)</label>
          <input v-model="newTask.price_threshold" type="number" step="0.01" class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all" placeholder="例如: 19.99 (低于此价立即报警)" />
        </div>

        <div v-if="newTask.monitor_type === 'rank'" class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-400 mb-2">搜索目标关键词</label>
          <input v-model="newTask.target_keyword" type="text" :required="newTask.monitor_type === 'rank'" class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all" placeholder="例如: wireless earbuds" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-400 mb-2">反风控注入 Zip Code</label>
          <input v-model="newTask.target_zipcode" type="text" class="w-full bg-[#111] border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all" placeholder="默认: 90001 (洛杉矶)" />
        </div>

        <div class="md:col-span-4 mt-2">
          <button type="submit" :disabled="isSubmitting" class="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 text-lg transition-all shadow-lg shadow-blue-500/20">
            <ShieldAlert v-if="!isSubmitting" class="w-6 h-6" />
            <RefreshCw v-else class="w-6 h-6 animate-spin" />
            {{ isSubmitting ? '引擎连接中...' : '立即锁定目标并部署' }}
          </button>
        </div>
      </form>
    </div>

    <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
      <table class="w-full text-sm">
        <thead class="bg-[#111]">
          <tr class="text-left text-gray-400 border-b border-white/5">
            <th class="p-5 font-medium">任务 / 客户</th>
            <th class="p-5 font-medium">Item ID</th>
            <th class="p-5 font-medium">监控模式</th>
            <th class="p-5 font-medium">阈值 / 关键词</th>
            <th class="p-5 font-medium">邮编</th>
            <th class="p-5 font-medium">状态</th>
            <th class="p-5 text-right font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-if="tasks.length === 0" class="text-center text-gray-500">
            <td colspan="7" class="p-12">防线空虚，快部署第一条哨兵吧！</td>
          </tr>
          <tr v-for="task in tasks" :key="task.id" class="hover:bg-white/5 transition-colors group">
            <td class="p-5">
              <div class="font-mono text-gray-300">#{{ task.id }}</div>
              <div class="text-xs text-gray-500 mt-1">Client: {{ task.clientId }}</div>
            </td>
            <td class="p-5">
              <a :href="'https://www.ebay.com/itm/' + task.itemId" target="_blank" class="text-blue-400 hover:text-blue-300 font-mono flex items-center gap-1">
                {{ task.itemId }}
              </a>
            </td>
            <td class="p-5">
              <span class="px-3 py-1 rounded-full text-xs font-medium border"
                    :class="task.monitorType === 'price' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-purple-500/10 border-purple-500/20 text-purple-400'">
                {{ task.monitorType === 'price' ? '价格防卫' : '排名监控' }}
              </span>
            </td>
            <td class="p-5 font-mono">
              <span v-if="task.monitorType === 'price'" class="text-red-300">${{ task.priceThreshold || '无' }}</span>
              <span v-else class="text-purple-300">"{{ task.targetKeyword || '-' }}"</span>
            </td>
            <td class="p-5 font-mono text-gray-400">{{ task.targetZipcode || '90001' }}</td>
            <td class="p-5">
              <span v-if="task.is_active" class="flex items-center gap-2 text-green-400 font-medium">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>巡逻中
              </span>
              <span v-else class="flex items-center gap-2 text-gray-500 font-medium">
                <div class="w-2 h-2 rounded-full bg-gray-600"></div>已休眠
              </span>
            </td>
            <td class="p-5 text-right">
              <button @click="toggleTaskStatus(task)" class="text-sm px-4 py-2 rounded-xl transition-all font-medium"
                      :class="task.is_active ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20' : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'">
                {{ task.is_active ? '强制撤防' : '重新激活' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Target, Plus, ShieldAlert, RefreshCw } from 'lucide-vue-next'
import { tasksApi } from '../api/tasks'
import { useToast } from '../utils/toast'

const { success, error } = useToast()
const tasks = ref([])
const isSubmitting = ref(false)

const newTask = ref({
  client_id: null,
  item_id: '',
  monitor_type: 'price',
  price_threshold: null,
  target_keyword: '',
  target_zipcode: '90001',
  check_interval: 30
})

const fetchTasks = async () => {
  try {
    const res = await tasksApi.getList()
    tasks.value = res || []
  } catch (e) {
    // 错误处理已在拦截器中
  }
}

const submitTask = async () => {
  isSubmitting.value = true
  try {
    // 数据清理，移除不需要的字段
    const payload = { ...newTask.value }
    if (payload.monitor_type === 'price') delete payload.target_keyword
    if (payload.monitor_type === 'rank') delete payload.price_threshold

    await tasksApi.create(payload)
    success('哨兵部署成功！引擎已锁定目标。')
    // 重置表单，保留客户ID和邮编方便连续添加
    Object.assign(newTask.value, { item_id: '', price_threshold: null, target_keyword: '' })
    fetchTasks()
  } catch (e) {
    // error notification is handled by axios interceptor
  } finally {
    isSubmitting.value = false
  }
}

const toggleTaskStatus = async (task) => {
  try {
    await tasksApi.toggleActive(task.id)
    success(`任务 #${task.id} 状态已更新`)
    fetchTasks()
  } catch (e) {
  }
}

onMounted(fetchTasks)
</script>