import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const dark = ref(localStorage.getItem('dark') === 'true')

  watch(dark, (val) => {
    localStorage.setItem('dark', val)
  })

  function toggle() {
    dark.value = !dark.value
  }

  return { dark, toggle }
})