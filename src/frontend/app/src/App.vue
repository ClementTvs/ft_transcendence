<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { useThemeStore } from './stores/theme'
import { getUsers } from './api'

const themeStore = useThemeStore()
const dark = computed(() => themeStore.dark)

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const showNotifDropdown = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const searchQuery = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const searching = ref(false)
let searchTimeout = null

const API = ''
const WS_NOTIF_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/notifications/ws`

const user = computed(() => userStore.user)

const avatarSrc = computed(() => {
  if (!user.value?.avatar_url) return '/def_user.png'
  if (user.value.avatar_url === '/def_user.png') return '/def_user.png'
  if (user.value.avatar_url.startsWith('http')) return user.value.avatar_url
  if (user.value.avatar_url.startsWith('/')) return `${API}${user.value.avatar_url}`
  return user.value.avatar_url
})

function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url === '/def_user.png') return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function getHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

watch(searchQuery, (val) => {
  clearTimeout(searchTimeout)
  if (!val.trim()) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  searching.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const results = await getUsers(val.trim())
      searchResults.value = results.filter(u => u.id !== user.value?.id).slice(0, 6)
      showSearchResults.value = true
    } catch (e) {
      console.error(e)
      searchResults.value = []
    } finally {
      searching.value = false
    }
  }, 300)
})

async function handleNavigation (to){
  if (route.path === to) {
    window.location.reload()
    return
  }
  await router.push(to)
}

function goToUser(userId) {
  searchQuery.value = ''
  showSearchResults.value = false
  if (userId === user.value?.id) {
    router.push('/profile')
  } else {
    router.push(`/user/${userId}`)
  }
}

function closeSearch() {
  showSearchResults.value = false
}

async function fetchUnreadCount() {
  try {
    const res = await fetch(`${API}/api/notifications/unread-count`, { headers: getHeaders() })
    if (res.ok) {
      const data = await res.json()
      unreadCount.value = data.unread_count
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchNotifications() {
  try {
    const res = await fetch(`${API}/api/notifications?limit=10`, { headers: getHeaders() })
    if (res.ok) {
      notifications.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

async function toggleNotifs() {
  showNotifDropdown.value = !showNotifDropdown.value
  if (showNotifDropdown.value) {
    await fetchNotifications()
    if (unreadCount.value > 0) {
      try {
        await fetch(`${API}/api/notifications/read-all`, {
          method: 'PUT',
          headers: getHeaders()
        })
        unreadCount.value = 0
      } catch (e) {
        console.error(e)
      }
    }
  }
}

function getNotifText(notif) {
  const actor = notif.actor?.display_name || notif.actor?.username || 'Quelqu\'un'
  switch (notif.type) {
    case 'like': return `${actor} a aimé votre post`
    case 'comment': return `${actor} a commenté votre post`
    case 'follow': return `${actor} vous suit`
    case 'message': return `${actor} vous a envoyé un message`
    default: return `${actor} — ${notif.type}`
  }
}

function formatTimeAgo(dateStr) {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return 'à l\'instant'
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return `${Math.floor(diff / 86400)}j`
}

function toggleDark() {
  themeStore.toggle()
}

function isActive(path) {
  return route.path === path
}

const hideNav = computed(() =>
  ['/login', '/register', '/forgot-password', '/settings'].includes(route.path)
)

let notifWs = null
//                                                                                   A verifier                 //
function connectNotifWS() {
  const token = localStorage.getItem('token')
  if (!token || notifWs) return
  notifWs = new WebSocket(`${WS_NOTIF_URL}?token=${token}`)
  notifWs.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      unreadCount.value++
      notifications.value.unshift({
        id: Date.now(),
        type: data.type,
        actor: { id: data.actor_id, username: data.actor_username },
        created_at: new Date().toISOString(),
        is_read: false,
        post_id: data.post_id ?? null,
      })
    } catch (e) { console.error(e) }
  }
  notifWs.onclose = () => {
    notifWs = null
    // Reconnect after 3s if token still present
    if (localStorage.getItem('token')) setTimeout(connectNotifWS, 3000)
  }
}

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await userStore.fetchUser()
      await fetchUnreadCount()
      connectNotifWS()
    } catch {
      localStorage.removeItem('token')
      router.push('/login')
    }
  }
})

// Connect WS when user logs in after the app was already mounted (e.g. arriving from /login)
watch(() => userStore.user, (newUser, oldUser) => {
  if (newUser && !oldUser) {
    fetchUnreadCount()
    connectNotifWS()
  }
  // Disconnect WS on logout
  if (!newUser && notifWs) {
    notifWs.close()
    notifWs = null
  }
})
</script>

<template>
  <nav
    v-if="!hideNav"
    :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-rose-50 border-rose-200'"
    class="flex justify-between items-center h-16 px-6 border-b sticky top-0 z-50"
  >
    <router-link to="/profile" class="flex items-center gap-3 group flex-shrink-0">
      <div class="relative">
        <img
          :src="avatarSrc"
          :class="dark ? 'ring-gray-700 group-hover:ring-rose-400' : 'ring-rose-100 group-hover:ring-rose-400'"
          class="h-9 w-9 rounded-full object-cover ring-2 transition-all"
        />
        <div
          v-if="user?.is_online"
          :class="dark ? 'border-gray-900' : 'border-rose-50'"
          class="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-green-400 rounded-full border-2"
        />
      </div>
      <span
        :class="dark ? 'text-white/70 group-hover:text-white' : 'text-gray-600 group-hover:text-gray-900'"
        class="text-sm font-medium transition-colors hidden xl:block"
      >
        {{ user?.display_name || user?.username || '' }}
      </span>
    </router-link>

    <div class="flex items-center gap-1">
      <router-link
        v-for="link in [
          { to: '/', label: 'Accueil' },
          { to: '/explore', label: 'Explore' },
          { to: '/chat', label: 'Chat' },
        ]"
        :key="link.to"
        :to="link.to"
        @click="handleNavigation(link.to)"
        :class="[
          isActive(link.to)
            ? (dark ? 'text-white bg-white/10' : 'text-rose-600 bg-rose-100')
            : (dark ? 'text-white/50 hover:text-white hover:bg-white/5' : 'text-gray-500 hover:text-gray-800 hover:bg-rose-100/50')
        ]"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
      >
        {{ link.label }}
      </router-link>
    </div>

    <div class="flex items-center gap-2 flex-shrink-0">

      <div class="relative hidden sm:block">
        <div class="relative">
          <svg
            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            :class="dark ? 'text-gray-500' : 'text-rose-300'"
            class="absolute left-3 top-1/2 -translate-y-1/2"
          >
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchQuery"
            @focus="searchQuery.trim() && (showSearchResults = true)"
            placeholder="Rechercher..."
            :class="dark
              ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-gray-600'
              : 'bg-white border-rose-100 text-gray-800 placeholder-rose-300 focus:border-rose-300'"
            class="w-44 focus:w-56 pl-9 pr-3 py-1.5 rounded-full border text-sm focus:outline-none transition-all"
          />
        </div>

        <div
          v-if="showSearchResults && searchQuery.trim()"
          :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100'"
          class="absolute top-full right-0 mt-2 w-72 rounded-xl shadow-xl border overflow-hidden z-50"
        >
          <div v-if="searching" class="px-4 py-4 text-center text-gray-400 text-sm">Recherche...</div>
          <div v-else-if="searchResults.length === 0" class="px-4 py-4 text-center text-gray-400 text-sm">
            Aucun résultat pour "{{ searchQuery }}"
          </div>
          <div v-else>
            <button
              v-for="result in searchResults"
              :key="result.id"
              @click="goToUser(result.id)"
              :class="dark ? 'hover:bg-gray-700' : 'hover:bg-gray-50'"
              class="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors"
            >
              <img :src="avatarUrl(result)" class="h-8 w-8 rounded-full object-cover flex-shrink-0" />
              <div class="min-w-0 flex-1">
                <p :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm truncate">
                  {{ result.display_name || result.username }}
                </p>
                <p class="text-gray-400 text-xs truncate">@{{ result.username }}</p>
              </div>
              <span
                v-if="result.is_online"
                class="text-[10px] text-green-500 font-medium flex items-center gap-1 flex-shrink-0"
              >
                <span class="h-1.5 w-1.5 rounded-full bg-green-400"></span>
                En ligne
              </span>
            </button>
          </div>
        </div>
      </div>

      <div class="relative">
        <button
          @click="toggleNotifs"
          :class="dark ? 'text-white/50 hover:text-white hover:bg-white/5' : 'text-gray-400 hover:text-gray-700 hover:bg-rose-100/50'"
          class="relative p-2 rounded-lg transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span
            v-if="unreadCount > 0"
            class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center bg-rose-500 text-white text-[10px] font-bold rounded-full px-1"
          >{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </button>

        <div
          v-if="showNotifDropdown"
          :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100'"
          class="absolute right-0 mt-2 w-80 rounded-xl shadow-xl border overflow-hidden z-50"
        >
          <div :class="dark ? 'border-gray-700' : 'border-gray-100'" class="px-4 py-3 border-b flex items-center justify-between">
            <span :class="dark ? 'text-white' : 'text-gray-800'" class="text-sm font-semibold">Notifications</span>
            <button @click="showNotifDropdown = false" :class="dark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600'" class="text-xs">Fermer</button>
          </div>
          <div class="max-h-80 overflow-y-auto">
            <div v-if="notifications.length === 0" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-4 py-8 text-center text-sm">Aucune notification</div>
            <div
              v-for="notif in notifications"
              :key="notif.id"
              :class="[
                notif.is_read ? (dark ? 'bg-gray-800' : 'bg-white') : (dark ? 'bg-rose-500/5' : 'bg-rose-50/50'),
                dark ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-50 hover:bg-gray-50'
              ]"
              class="px-4 py-3 border-b transition-colors flex items-start gap-3 cursor-pointer"
              @click="if (notif.actor) { notif.type === 'message' ? router.push(`/chat/${notif.actor.id}`) : goToUser(notif.actor.id) }; showNotifDropdown = false"
            >
              <img :src="avatarUrl(notif.actor)" class="h-8 w-8 rounded-full object-cover flex-shrink-0 mt-0.5" />
              <div class="flex-1 min-w-0">
                <p :class="dark ? 'text-gray-200' : 'text-gray-700'" class="text-sm leading-snug">{{ getNotifText(notif) }}</p>
                <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-xs mt-0.5">{{ formatTimeAgo(notif.created_at) }}</p>
              </div>
              <div v-if="!notif.is_read" class="h-2 w-2 rounded-full bg-rose-400 flex-shrink-0 mt-2" />
            </div>
          </div>
        </div>
      </div>

      <button
        @click="toggleDark"
        :class="dark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-rose-200 hover:bg-rose-300'"
        class="p-2 rounded-full transition-all"
      >
        <svg v-if="!dark" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-700">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      </button>
    </div>
  </nav>

  <div v-if="showNotifDropdown" class="fixed inset-0 z-40" @click="showNotifDropdown = false" />
  <div v-if="showSearchResults" class="fixed inset-0 z-40" @click="closeSearch" />
    <router-view class="pb-14"/>
    
  <footer v-if="!hideNav"
    :class="dark ? 'bg-gray-900 border-gray-800 text-gray-500' : 'bg-rose-50 border-rose-100 text-gray-400'"
    class="fixed bottom-0 left-0 right-0 border-t py-3 px-6 z-30"
  >
      <div class="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <p class="text-xs">© 2026 ft_transcendence · 42</p>
    
        <div class="flex items-center gap-4">
          <router-link
            to="/terms"
            :class="dark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'"
            class="text-xs transition-colors"
          >
            Conditions d'utilisation
          </router-link>
          <span :class="dark ? 'text-gray-700' : 'text-gray-300'">·</span>
          <router-link
            to="/privacy"
            :class="dark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'"
            class="text-xs transition-colors"
          >
            Politique de confidentialité
          </router-link>
        </div>
      </div>
    </footer>
</template>

<style scoped></style>