<template>
  <div class="flex h-screen bg-gray-950 text-gray-100 font-sans">
    <div class="w-64 bg-black/70 backdrop-blur-xl border-r border-white/10 flex flex-col z-10">
      <div class="p-6 border-b border-white/10">
        <h1 class="text-2xl font-bold tracking-tighter flex items-center gap-2">
          <span class="text-green-500">🦅</span> eBay Guard
        </h1>
        <p class="text-xs text-gray-500 mt-1">v1.5 商业主控台</p>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all text-sm font-medium" active-class="bg-white/10 text-white shadow-inner">
          <Activity class="w-5 h-5" /> 数据大盘
        </router-link>
        <router-link to="/tasks" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all text-sm font-medium" active-class="bg-white/10 text-white shadow-inner">
          <Target class="w-5 h-5" /> 监控矩阵
        </router-link>
        <router-link to="/clients" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all text-sm font-medium" active-class="bg-white/10 text-white shadow-inner">
          <Users class="w-5 h-5" /> 客户管理
        </router-link>
      </nav>

      <div class="p-4 border-t border-white/10 text-xs text-gray-500 flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        引擎状态：在线
      </div>
    </div>

    <div class="flex-1 overflow-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-gray-950 to-black">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <div class="fixed top-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
      <transition-group name="toast">
        <div v-for="toast in toasts" :key="toast.id"
             class="px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border backdrop-blur-xl pointer-events-auto min-w-[300px]"
             :class="{
               'bg-green-500/10 border-green-500/20 text-green-400': toast.type === 'success',
               'bg-red-500/10 border-red-500/20 text-red-400': toast.type === 'error',
               'bg-yellow-500/10 border-yellow-500/20 text-yellow-400': toast.type === 'warning',
               'bg-blue-500/10 border-blue-500/20 text-blue-400': toast.type === 'info'
             }">
          <span v-if="toast.type === 'success'">✅</span>
          <span v-else-if="toast.type === 'error'">🚨</span>
          <span v-else-if="toast.type === 'warning'">⚠️</span>
          <span v-else>ℹ️</span>
          <span class="font-medium text-sm">{{ toast.message }}</span>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { Activity, Target, Users } from 'lucide-vue-next'
import { toasts } from './utils/toast'
</script>

<style>
/* 路由切换动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Toast 动画 */
.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from { opacity: 0; transform: translateX(50px) scale(0.9); }
.toast-leave-to { opacity: 0; transform: translateY(-20px) scale(0.9); }
</style>