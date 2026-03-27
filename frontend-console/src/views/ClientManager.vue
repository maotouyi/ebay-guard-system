<template>
  <div class="p-8 space-y-8 bg-gray-950 min-h-full relative">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tighter flex items-center gap-3">
          <Users class="w-10 h-10 text-purple-500" /> 客户与通知管理
        </h1>
        <p class="text-gray-400 mt-2">统管所有客户资料与 Bark / 企微路由</p>
      </div>
      <button @click="openModal()" class="bg-purple-600 hover:bg-purple-500 text-white px-8 py-4 rounded-2xl flex items-center gap-3 text-lg font-medium transition-all shadow-lg shadow-purple-500/20">
        <Plus class="w-6 h-6" /> 新增金主
      </button>
    </header>

    <div class="bg-black/40 backdrop-blur-2xl border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
      <table class="w-full text-sm">
        <thead class="bg-[#111]">
          <tr class="text-left text-gray-400 border-b border-white/5">
            <th class="p-6 font-medium">ID</th>
            <th class="p-6 font-medium">客户名称</th>
            <th class="p-6 font-medium">通知通道 (Bark/Wechat)</th>
            <th class="p-6 font-medium">到期时间</th>
            <th class="p-6 font-medium">状态</th>
            <th class="p-6 text-right font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-if="clients.length === 0" class="text-center text-gray-500">
            <td colspan="6" class="p-12">暂无客户数据。</td>
          </tr>
          <tr v-for="client in clients" :key="client.id" class="hover:bg-white/5 transition-colors">
            <td class="p-6 font-mono text-gray-500">#{{ client.id }}</td>
            <td class="p-6 font-bold text-gray-200">{{ client.name }}</td>
            <td class="p-6">
              <div class="space-y-1">
                <div v-if="client.bark_url" class="flex items-center gap-2 text-xs">
                  <span class="bg-red-500/20 text-red-400 px-2 py-0.5 rounded">Bark</span>
                  <span class="font-mono text-gray-400 truncate max-w-[200px]" :title="client.bark_url">{{ client.bark_url }}</span>
                </div>
                <div v-if="client.wechat_webhook" class="flex items-center gap-2 text-xs">
                  <span class="bg-green-500/20 text-green-400 px-2 py-0.5 rounded">Wechat</span>
                  <span class="font-mono text-gray-400 truncate max-w-[200px]">{{ client.wechat_webhook }}</span>
                </div>
                <div v-if="!client.bark_url && !client.wechat_webhook" class="text-gray-600 italic">未配置通知</div>
              </div>
            </td>
            <td class="p-6 font-mono text-gray-400">{{ formatDate(client.expire_date) }}</td>
            <td class="p-6">
              <span class="bg-green-500/10 border border-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-medium">
                合作中
              </span>
            </td>
            <td class="p-6 text-right space-x-3">
              <button @click="testNotification(client)" class="text-blue-400 hover:text-blue-300 transition-colors">Test 路由</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <transition name="fade">
      <div v-if="showModal" class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
        <div class="bg-[#111] border border-white/10 rounded-3xl w-full max-w-lg p-8 shadow-2xl relative" @click.stop>
          <h3 class="text-2xl font-bold mb-6 text-white">新增客户档案</h3>

          <form @submit.prevent="saveClient" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">客户名称 <span class="text-red-500">*</span></label>
              <input v-model="form.name" required class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl p-3.5 text-white focus:border-purple-500 focus:outline-none transition-colors" placeholder="如: 张总-汽配类目" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">Bark 推送 URL (推荐)</label>
              <input v-model="form.bark_url" class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl p-3.5 text-white focus:border-purple-500 focus:outline-none transition-colors" placeholder="https://api.day.app/your_key" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">企业微信 Webhook</label>
              <input v-model="form.wechat_webhook" class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl p-3.5 text-white focus:border-purple-500 focus:outline-none transition-colors" placeholder="https://qyapi.weixin.qq.com/cgi-bin/..." />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">订阅到期日 <span class="text-red-500">*</span></label>
              <input v-model="form.expire_date" type="datetime-local" required class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl p-3.5 text-gray-300 focus:border-purple-500 focus:outline-none transition-colors [color-scheme:dark]" />
            </div>

            <div class="flex gap-4 pt-6">
              <button type="button" @click="showModal = false" class="flex-1 bg-white/5 hover:bg-white/10 text-white py-3.5 rounded-xl font-medium transition-colors">取消</button>
              <button type="submit" :disabled="isSubmitting" class="flex-1 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white py-3.5 rounded-xl font-medium transition-colors flex justify-center items-center gap-2">
                <RefreshCw v-if="isSubmitting" class="w-5 h-5 animate-spin" />
                {{ isSubmitting ? '保存中...' : '确认录入' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Users, Plus, RefreshCw } from 'lucide-vue-next'
import { clientsApi } from '../api/clients'
import { useToast } from '../utils/toast'

const { success, warning } = useToast()
const clients = ref([])
const showModal = ref(false)
const isSubmitting = ref(false)

const form = ref({
  name: '',
  bark_url: '',
  wechat_webhook: '',
  expire_date: ''
})

const formatDate = (isoStr) => {
  if (!isoStr) return '-'
  return isoStr.replace('T', ' ').substring(0, 16)
}

const fetchClients = async () => {
  try {
    const res = await clientsApi.getList()
    clients.value = res || []
  } catch (e) {}
}

const openModal = () => {
  // 设置默认到期时间为一个月后
  const nextMonth = new Date()
  nextMonth.setMonth(nextMonth.getMonth() + 1)

  form.value = {
    name: '',
    bark_url: '',
    wechat_webhook: '',
    // 格式化为 datetime-local 需要的格式 yyyy-MM-ddThh:mm
    expire_date: nextMonth.toISOString().slice(0, 16)
  }
  showModal.value = true
}

const saveClient = async () => {
  isSubmitting.value = true
  try {
    // 处理空字符串为 null，防止后端校验报错
    const payload = { ...form.value }
    if (!payload.bark_url) payload.bark_url = null
    if (!payload.wechat_webhook) payload.wechat_webhook = null

    // 转换为 UTC 格式供后端解析
    payload.expire_date = new Date(payload.expire_date).toISOString()

    await clientsApi.create(payload)
    success('客户档案录入成功！')
    showModal.value = false
    fetchClients()
  } catch (e) {
  } finally {
    isSubmitting.value = false
  }
}

const testNotification = () => {
  warning('后端暂未暴露测试 API 路由，此功能待开放。')
}

onMounted(fetchClients)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>