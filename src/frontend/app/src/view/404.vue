<script setup>
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { computed } from 'vue'

const router = useRouter()
const themeStore = useThemeStore()
const dark = computed(() => themeStore.isDark)
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50/50'" class="min-h-[calc(100vh-64px)] flex items-center justify-center px-4">
    <div class="text-center max-w-md">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-600' : 'text-gray-300'" class="mx-auto mb-6">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>

      <h1 :class="dark ? 'text-white' : 'text-gray-900'" class="text-7xl font-bold mb-3">404</h1>

      <h2 :class="dark ? 'text-gray-200' : 'text-gray-800'" class="text-xl font-semibold mb-2">
        Page introuvable
      </h2>
      <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm mb-8">
        La page que tu cherches n'existe pas ou a été déplacée.
      </p>

      <div class="flex items-center justify-center gap-3">
        <button
          @click="router.back()"
          :class="dark ? 'bg-gray-800 hover:bg-gray-700 text-gray-200' : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'"
          class="px-5 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          Retour
        </button>
        <button
          @click="router.push('/')"
          class="px-5 py-2.5 rounded-lg text-sm font-medium bg-rose-500 hover:bg-rose-600 text-white transition-colors flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Accueil
        </button>
      </div>
    </div>
  </div>
</template>