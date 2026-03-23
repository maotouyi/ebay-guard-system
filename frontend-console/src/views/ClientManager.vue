<template>
  <div class="p-8 space-y-8 bg-gray-950">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter flex items-center gap-3">
          <Users class="w-10 h-10 text-purple-500" /> 客户与通知管理
        </h1>
        <p class="text-gray-400">绑定 Bark / 企微 / 阿里云 · 永久客户</p>
      </div>
      <button @click="openModal()" class="bg-green-600 hover:bg-green-700 px-8 py-4 rounded-2xl flex items-center gap-3 text-lg">
        <Plus class="w-6 h-6" /> 新增客户
      </button>
    </header>

    <!-- 客户表格 -->
    <div class="bg-black/50 backdrop-blur-2xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
      <table class="w-full">
        <thead class="bg-gray-900/80">
          <tr class="text-gray-400 text-sm border-b border-white/10">
            <th class="p-6">客户</th>
            <th class="p-6">Bark / 企微</th>
            <th class="p-6">手机号</th>
            <th class="p-6">到期日</th>
            <th class="p-6">状态</th>
            <th class="p-6 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/10">
          <tr v-if="clients.length === 0" class="text-center text-gray-500">
            <td colspan="6" class="p-12">暂无客户，快添加第一个金主吧！</td>
          </tr>
          <tr v-for="client in clients" :key="client.id" class="hover:bg-white/5">
            <td class="p-6 font-medium">{{ client.name }}</td>
            <td class="p-6 font-mono text-xs break-all">{{ client.wechat_webhook || client.bark_id || '-' }}</td>
            <td class="p-6">{{ client.phone || '-' }}</td>
            <td class="p-6 text-gray-400">{{ client.expire_date || '永久' }}</td>
            <td class="p-6">
              <span class="text-green-500">🟢 活跃</span>
            </td>
            <td class="p-6 text-right flex gap-3 justify-end">
              <button @click="testClient(client.id)" class="text-green-400 hover:text-green-300">测试推送</button>
              <button @click="editClient(client)" class="text-blue-400 hover:text-blue-300">编辑</button>
              <button @click="deleteClient(client.id)" class="text-red-400 hover:text-red-300">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑模态框 -->
    <div v-if="showModal" class="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center z-50">
      <div class="bg-gray-900 border border-white/10 rounded-3xl w-full max-w-md p-8">
        <h3 class="text-2xl font-bold mb-6">{{ editingId ? '编辑客户' : '新增客户' }}</h3>

        <div class="space-y-6">
          <div>
            <label class="block text-sm text-gray-400 mb-2">客户名称</label>
            <input v-model="modalClient.name" class="w-full bg-black border border-white/10 rounded-2xl p-4" placeholder="张老板" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">企微 Webhook</label>
            <input v-model="modalClient.wechat_webhook" class="w-full bg-black border border-white/10 rounded-2xl p-4" placeholder="https://qyapi.weixin.qq.com/..." />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">Bark ID</label>
            <input v-model="modalClient.bark_id" class="w-full bg-black border border-white/10 rounded-2xl p-4" placeholder="xxxxxxx" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">阿里云手机号（可选）</label>
            <input v-model="modalClient.phone" class="w-full bg-black border border-white/10 rounded-2xl p-4" placeholder="13800138000" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">到期日期（留空=永久）</label>
            <input v-model="modalClient.expire_date" type="date" class="w-full bg-black border border-white/10 rounded-2xl p-4" />
          </div>
        </div>

        <div class="flex gap-4 mt-8">
          <button @click="saveClient" class="flex-1 bg-green-600 hover:bg-green-700 py-4 rounded-2xl">保存客户</button>
          <button @click="showModal = false" class="flex-1 bg-gray-800 hover:bg-gray-700 py-4 rounded-2xl">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Users, Plus } from 'lucide-vue-next'
import api from '../api/request'

const clients = ref([])
const showModal = ref(false)
const editingId = ref(null)
const modalClient = ref({
  name: '',
  wechat_webhook: '',
  bark_id: '',
  phone: '',
  expire_date: ''
})

const fetchClients = async () => {
  try {
    const res = await api.get('/clients/')
    clients.value = res || []
  } catch (e) {}
}

const openModal = (client = null) => {
  if (client) {
    modalClient.value = { ...client }
    editingId.value = client.id
  } else {
    modalClient.value = { name: '', wechat_webhook: '', bark_id: '', phone: '', expire_date: '' }
    editingId.value = null
  }
  showModal.value = true
}

const saveClient = async () => {
  try {
    if (editingId.value) {
      await api.put(`/clients/${editingId.value}`, modalClient.value)
    } else {
      await api.post('/clients/', modalClient.value)
    }
    showModal.value = false
    fetchClients()
  } catch (e) {
    alert('保存失败')
  }
}

const deleteClient = async (id) => {
  if (!confirm('删除客户？')) return
  try {
    await api.delete(`/clients/${id}`)
    fetchClients()
  } catch (e) {}
}

const testClient = async (id) => {
  try {
    await api.post(`/clients/${id}/test`)
    alert('✅ 测试推送已发送！请检查手机/Bark')
  } catch (e) {
    alert('测试失败（后端暂未实现测试接口也没关系，先看看日志）')
  }
}

onMounted(fetchClients)
</script>