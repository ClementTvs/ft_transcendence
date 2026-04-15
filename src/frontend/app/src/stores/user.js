import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProfile } from '../api'
import router  from '../router/index'

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
    router.push('/login')
  }

  return { user, fetchUser, logout }
})