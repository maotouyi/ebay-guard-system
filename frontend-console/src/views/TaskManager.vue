<template>
  <div class="min-h-screen p-6 space-y-6 text-gray-100">
    <header class="flex items-center justify-between pb-4 border-b border-gray-800">
      <h2 class="text-2xl font-bold flex items-center gap-2">
        <Target class="w-6 h-6 text-blue-500" />
        监控矩阵 (Task Matrix)
      </h2>
      <button @click="$router.push('/')" class="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-md text-sm border border-gray-700 transition-colors">
        返回大盘
      </button>
    </header>

    <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg">
      <h3 class="text-lg font-medium mb-4 flex items-center gap-2"><Plus class="w-5 h-5"/> 部署新哨兵</h3>
      <form @submit.prevent="submitTask" class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label class="block text-sm text-gray-400 mb-1">金主 ID (Client ID)</label>
          <input v-model="newTask.client_id" type="number" required class="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:border-blue-500 focus:outline-none" placeholder="例如: 1" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">eBay Item ID</label>
          <input v-model="newTask.item_id" type="text" required class="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:border-blue-500 focus:outline-none" placeholder="输入 12 位纯数字" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">破价防守线 ($)</label>
          <input v-model="newTask.price_threshold" type="number" step="0.01" required class="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white focus:border-blue-500 focus:outline-none" placeholder="低于此价自动打爆电话" />
        </div>
        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors flex justify-center items-center gap-2">
          <ShieldAlert class="w-4 h-4"/>
          锁定目标
        </button>
      </form>
    </div>

    <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden shadow-lg">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-900 border-b border-gray-700 text-gray-400 text-sm">
            <th class="p-4 font-medium">任务 ID</th>
            <th class="p-4 font-medium">目标 Item</th>
            <th class="p-4 font-medium">防卫类型</th>
            <th class="p-4 font-medium">防守线</th>
            <th class="p-4 font-medium">状态</th>
            <th class="p-4 font-medium text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700 text-sm">
          <tr v-if="tasks.length === 0">
            <td colspan="6" class="p-8 text-center text-gray-500">当前没有部署任何哨兵，防线空虚</td>
          </tr>
          <tr v-for="task in tasks" :key="task.id" class="hover:bg-gray-750 transition-colors">
            <td class="p-4 text-gray-400">#{{ task.id }}</td>
            <td class="p-4 font-mono text-blue-400">
              <a :href="'https://www.ebay.com/itm/' + task.item_id" target="_blank" class="hover:underline">{{ task.item_id }}</a>
            </td>
            <td class="p-4"><span class="px-2 py-1 bg-gray-700 rounded text-xs">价格绞杀</span></td>
            <td class="p-4 font-mono text-red-400 font-bold">${{ task.price_threshold }}</td>
            <td class="p-4">
              <span class="flex items-center gap-1 text-green-500">
                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> 巡逻中
              </span>
            </td>
            <td class="p-4 text-right">
              <button @click="stopTarget(task.id)" class="text-red-400 hover:text-red-300 transition-colors text-sm border border-red-900 bg-red-900/20 px-3 py-1 rounded">
                撤防 (软删除)
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
  client_id: 1, // 默认填你打底的那个客户
  item_id: '',
  price_threshold: ''
})

// 加载任务列表
const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks/')
    tasks.value = res
  } catch (error) {
    alert("拿不到任务数据，检查后端有没有报错")
  }
}

// 提交新任务
const submitTask = async () => {
  try {
    await api.post('/tasks/', newTask.value)
    alert("哨兵部署成功！")
    newTask.value.item_id = '' // 清空输入框
    newTask.value.price_threshold = ''
    fetchTasks() // 刷新列表
  } catch (error) {
    alert("部署失败: " + (error.response?.data?.detail || error.message))
  }
}

// 停止任务
const stopTarget = async (id) => {
  if(!confirm("确定要撤掉这条防线吗？")) return;
  try {
    await api.put(`/tasks/${id}/stop`)
    fetchTasks() // 刷新列表
  } catch (error) {
    alert("撤防失败")
  }
}

onMounted(() => {
  fetchTasks()
})
</script>