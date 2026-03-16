import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProfile } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)

    async function fetchUser() {
    try {
        user.value = await getProfile()
    } catch (e) {
        user.value = null
        throw e
    }
    }

  function logout() {
    localStorage.removeItem('token')
    user.value = null
  }

  return { user, fetchUser, logout }
})