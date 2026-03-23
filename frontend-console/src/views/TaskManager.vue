<template>
  <div class="p-8 space-y-8 bg-gray-950">
    <!-- Header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter flex items-center gap-3">
          <Target class="w-10 h-10 text-blue-500" /> 监控矩阵
        </h1>
        <p class="text-gray-400">三条防卫线 · 实时部署哨兵</p>
      </div>
      <button @click="$router.push('/')" class="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-xl px-6 py-3 rounded-2xl border border-white/10">
        ← 返回大盘
      </button>
    </header>

    <!-- 部署新哨兵（玻璃卡片） -->
    <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
      <h3 class="text-xl font-medium mb-6 flex items-center gap-2"><Plus class="w-6 h-6" /> 部署新哨兵</h3>
      <form @submit.prevent="submitTask" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label class="block text-sm text-gray-400 mb-2">客户 ID (Client ID)</label>
          <input v-model="newTask.client_id" type="number" required class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none" placeholder="1" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">eBay Item ID</label>
          <input v-model="newTask.item_id" type="text" required class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none" placeholder="12位纯数字" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">监控类型</label>
          <select v-model="newTask.monitor_type" required class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none">
            <option value="price_drop">价格破线（默认）</option>
            <option value="sentiment">舆情监控（差评/敏感词）</option>
            <option value="traffic">流量排名监控</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">破价防守线 ($)</label>
          <input v-model="newTask.price_threshold" type="number" step="0.01" class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none" placeholder="低于此价报警" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">目标 Zip Code</label>
          <input v-model="newTask.target_zipcode" type="text" class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none" placeholder="90210" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">巡逻频率</label>
          <select v-model="newTask.check_interval" required class="w-full bg-gray-900 border border-white/10 rounded-2xl p-4 text-white focus:border-blue-500 focus:outline-none">
            <option value="5">激进 5分钟</option>
            <option value="15">标准 15分钟</option>
            <option value="30" selected>常规 30分钟</option>
          </select>
        </div>
        <button type="submit" class="md:col-span-3 bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white font-medium py-4 rounded-2xl flex items-center justify-center gap-3 text-lg transition-all">
          <ShieldAlert class="w-6 h-6" /> 立即锁定目标
        </button>
      </form>
    </div>

    <!-- 任务列表 -->
    <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
      <table class="w-full">
        <thead class="bg-gray-900/80">
          <tr class="text-left text-gray-400 text-sm border-b border-white/10">
            <th class="p-6">任务ID</th>
            <th class="p-6">Item</th>
            <th class="p-6">类型</th>
            <th class="p-6">防守线</th>
            <th class="p-6">Zip</th>
            <th class="p-6">频率</th>
            <th class="p-6">状态</th>
            <th class="p-6 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/10 text-sm">
          <tr v-if="tasks.length === 0" class="text-center text-gray-500">
            <td colspan="8" class="p-12">防线空虚，快部署第一条哨兵吧！</td>
          </tr>
          <tr v-for="task in tasks" :key="task.id" class="hover:bg-white/5 transition-all">
            <td class="p-6 font-mono text-gray-400">#{{ task.id }}</td>
            <td class="p-6">
              <a :href="'https://www.ebay.com/itm/' + task.item_id" target="_blank" class="text-blue-400 hover:underline font-mono">{{ task.item_id }}</a>
            </td>
            <td class="p-6">
              <span class="px-4 py-1 bg-white/10 rounded-full text-xs" :class="task.monitor_type === 'price_drop' ? 'text-red-400' : 'text-yellow-400'">
                {{ task.monitor_type === 'price_drop' ? '价格' : task.monitor_type === 'sentiment' ? '舆情' : '流量' }}
              </span>
            </td>
            <td class="p-6 font-bold text-red-400">${{ task.price_threshold || '-' }}</td>
            <td class="p-6 font-mono">{{ task.target_zipcode || '-' }}</td>
            <td class="p-6">{{ task.check_interval }}分钟</td>
            <td class="p-6">
              <span class="flex items-center gap-2 text-green-500">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                巡逻中
              </span>
            </td>
            <td class="p-6 text-right">
              <button @click="stopTarget(task.id)" class="bg-red-900/30 hover:bg-red-900/50 text-red-400 px-5 py-2 rounded-2xl text-sm transition-all">
                撤防
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
import { Target, Plus, ShieldAlert } from 'lucide-vue-next'
import api from '../api/request'

const tasks = ref([])
const newTask = ref({
  client_id: 1,
  item_id: '',
  monitor_type: 'price_drop',
  price_threshold: '',
  target_zipcode: '',
  check_interval: 30
})

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks/')
    tasks.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const submitTask = async () => {
  try {
    await api.post('/tasks/', newTask.value)
    alert('✅ 哨兵部署成功！引擎已开始巡逻')
    Object.assign(newTask.value, { item_id: '', price_threshold: '', target_zipcode: '' })
    fetchTasks()
  } catch (e) {
    alert('部署失败：' + (e.response?.data?.detail || e.message))
  }
}

const stopTarget = async (id) => {
  if (!confirm('确定撤掉这条防线吗？')) return
  try {
    await api.put(`/tasks/${id}/stop`)
    fetchTasks()
  } catch (e) {
    alert('撤防失败')
  }
}

onMounted(fetchTasks)
</script>