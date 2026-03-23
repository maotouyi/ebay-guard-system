<template>
  <div class="flex h-screen bg-gray-950 text-gray-100">
    <!-- 侧边栏 -->
    <div class="w-64 bg-black/70 backdrop-blur-xl border-r border-white/10 flex flex-col">
      <div class="p-6 border-b border-white/10">
        <h1 class="text-2xl font-bold tracking-tighter flex items-center gap-2">
          <span class="text-green-500">🛡️</span> eBay Guard
        </h1>
        <p class="text-xs text-gray-500 mt-1">v1.5 商业主控台</p>
      </div>

      <nav class="flex-1 p-4 space-y-1">
        <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all" :class="{ 'bg-white/10': $route.path === '/' }">
          <Activity class="w-5 h-5" /> 数据大盘
        </router-link>
        <router-link to="/tasks" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all" :class="{ 'bg-white/10': $route.path === '/tasks' }">
          <Target class="w-5 h-5" /> 监控矩阵
        </router-link>
        <router-link to="/clients" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all" :class="{ 'bg-white/10': $route.path === '/clients' }">
          <Users class="w-5 h-5" /> 客户管理
        </router-link>
      </nav>

      <div class="p-4 border-t border-white/10 text-xs text-gray-500">
        引擎状态：<span class="text-green-500">🟢 在线</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-auto">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { Activity, Target, Users } from 'lucide-vue-next'
</script>