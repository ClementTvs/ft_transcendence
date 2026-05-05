<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import {
  getConversations, getOrCreateConversation, getMessages, markConversationRead
} from '../api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const me = computed(() => userStore.user)
const dark = computed(() => themeStore.dark)

const API = 'https://localhost:8000'
const WS_URL = 'wss://localhost:8000/api/messages/ws/chat'

const conversations = ref([])
const activeConvId = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)
const messagesLoading = ref(false)
const messagesContainer = ref(null)
const searchQuery = ref('')

let ws = null

function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url === '/def_user.png') return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function formatTime(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 86400) return formatTime(dateStr)
  if (diff < 604800) return d.toLocaleDateString('fr-FR', { weekday: 'short' })
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const activeConversation = computed(() =>
  conversations.value.find(c => c.id === activeConvId.value)
)

const otherUser = computed(() => activeConversation.value?.other_user)

const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) return conversations.value
  const s = searchQuery.value.toLowerCase()
  return conversations.value.filter(c => {
    const name = c.other_user?.display_name || c.other_user?.username || ''
    return name.toLowerCase().includes(s)
  })
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function connectWS() {
  const token = localStorage.getItem('token')
  if (!token) return

  ws = new WebSocket(`${WS_URL}?token=${token}`)

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    // Read receipt
    if (data.type === 'read_receipt') {
      if (data.conversation_id === activeConvId.value) {
        messages.value.forEach(msg => {
          if (msg.sender_id === me.value?.id) {
            msg.is_read = true
          }
        })
      }
      return
    }

    if (data.conversation_id === activeConvId.value) {
      if (!messages.value.find(m => m.id === data.id)) {
        messages.value.push(data)
        scrollToBottom()
      }
      if (data.sender_id !== me.value?.id && ws) {
        ws.send(JSON.stringify({
          type: 'mark_read',
          conversation_id: activeConvId.value
        }))
      }
    }

    refreshConversations()
  }

  ws.onclose = () => {
    setTimeout(() => {
      if (me.value) connectWS()
    }, 3000)
  }
}

async function refreshConversations() {
  try {
    conversations.value = await getConversations()
  } catch (e) {
    console.error(e)
  }
}

async function selectConversation(conv) {
  activeConvId.value = conv.id
  messagesLoading.value = true

  try {
    messages.value = await getMessages(conv.id)
    messagesLoading.value = false
    await nextTick()
    scrollToBottom()

    if (conv.unread_count > 0 && ws) {
      ws.send(JSON.stringify({
        type: 'mark_read',
        conversation_id: conv.id
      }))
      conv.unread_count = 0
    }
  } catch (e) {
    console.error(e)
    messagesLoading.value = false
  }
}

async function sendMessage() {
  const content = newMessage.value.trim()
  if (!content || !activeConvId.value || !otherUser.value || !ws) return

  ws.send(JSON.stringify({
    to_user_id: otherUser.value.id,
    conversation_id: activeConvId.value,
    content: content
  }))

  newMessage.value = ''
}

async function openConversationWithUser(userId) {
  try {
    const conv = await getOrCreateConversation(userId)
    await refreshConversations()
    await selectConversation(conv)
  } catch (e) {
    console.error('Erreur ouverture conversation:', e)
  }
}

onMounted(async () => {
  try {
    conversations.value = await getConversations()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }

  connectWS()

  const targetUserId = route.params.userId
  if (targetUserId) {
    await openConversationWithUser(Number(targetUserId))
  } else if (conversations.value.length > 0) {
    await selectConversation(conversations.value[0])
  }
})

watch(() => route.params.userId, async (newId) => {
  if (newId) {
    await openConversationWithUser(Number(newId))
  }
})

onUnmounted(() => {
  if (ws) {
    ws.onclose = null
    ws.close()
  }
})
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50'" class="flex h-[calc(100vh-64px)]">

    <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="w-80 border-r flex flex-col flex-shrink-0">
      <div :class="dark ? 'border-gray-700' : 'border-rose-100'" class="px-5 py-4 border-b">
        <h2 :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-lg">Messages</h2>
        <div class="relative mt-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            :class="dark ? 'text-gray-500' : 'text-rose-300'"
            class="absolute left-3 top-1/2 -translate-y-1/2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchQuery"
            placeholder="Rechercher une conversation..."
            :class="dark
              ? 'bg-gray-800 text-white placeholder-gray-500 focus:bg-gray-750'
              : 'bg-rose-50 text-gray-700 placeholder-rose-300 focus:bg-rose-100/50'"
            class="w-full pl-9 pr-3 py-2 rounded-full text-sm focus:outline-none transition-colors"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-5 py-10 text-center text-sm">Chargement...</div>
        <div v-else-if="filteredConversations.length === 0" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-5 py-10 text-center text-sm">
          {{ searchQuery ? 'Aucun résultat' : 'Aucune conversation' }}
        </div>
        <button
          v-for="conv in filteredConversations"
          :key="conv.id"
          @click="selectConversation(conv)"
          :class="activeConvId === conv.id
            ? (dark ? 'bg-gray-800' : 'bg-rose-50')
            : (dark ? 'hover:bg-gray-800' : 'hover:bg-gray-50')"
          class="w-full flex items-center gap-3 px-5 py-3.5 text-left transition-colors border-b"
          :style="{ borderColor: dark ? '#374151' : '#f9fafb' }"
        >
          <div class="relative flex-shrink-0">
            <img :src="avatarUrl(conv.other_user)" class="h-12 w-12 rounded-full object-cover" />
            <div
              v-if="conv.other_user?.is_online"
              :class="dark ? 'border-gray-900' : 'border-white'"
              class="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-green-400 rounded-full border-2"
            />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <p :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm truncate">
                {{ conv.other_user?.display_name || conv.other_user?.username }}
              </p>
              <span v-if="conv.last_message" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-[11px] flex-shrink-0 ml-2">
                {{ formatDate(conv.last_message.created_at) }}
              </span>
            </div>
            <div class="flex items-center justify-between mt-0.5">
              <p :class="dark ? 'text-gray-400' : 'text-gray-400'" class="text-xs truncate">
                <span v-if="conv.last_message">
                  <span v-if="conv.last_message.sender_id === me?.id" :class="dark ? 'text-gray-500' : 'text-gray-500'">Vous : </span>
                  {{ conv.last_message.content }}
                </span>
                <span v-else class="italic">Nouvelle conversation</span>
              </p>
              <span
                v-if="conv.unread_count > 0"
                class="ml-2 min-w-[20px] h-5 flex items-center justify-center bg-rose-500 text-white text-[10px] font-bold rounded-full px-1.5 flex-shrink-0"
              >
                {{ conv.unread_count }}
              </span>
            </div>
          </div>
        </button>
      </div>
    </div>

    <div class="flex-1 flex flex-col">

      <div v-if="!activeConvId" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"
            :class="dark ? 'text-gray-600' : 'text-gray-300'"
            class="mx-auto mb-3">
            <rect width="20" height="16" x="2" y="4" rx="2"/>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
          </svg>
          <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Sélectionnez une conversation</p>
          <p :class="dark ? 'text-gray-600' : 'text-gray-300'" class="text-xs mt-1">ou envoyez un message depuis le profil d'un joueur</p>
        </div>
      </div>

      <template v-else>
        <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="flex items-center gap-3 px-5 py-3 border-b">
          <router-link :to="`/user/${otherUser?.id}`">
            <img :src="avatarUrl(otherUser)" class="h-10 w-10 rounded-full object-cover" />
          </router-link>
          <div class="flex-1 min-w-0">
            <router-link :to="`/user/${otherUser?.id}`" :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm hover:underline">
              {{ otherUser?.display_name || otherUser?.username }}
            </router-link>
            <p class="text-xs" :class="otherUser?.is_online ? 'text-green-500' : (dark ? 'text-gray-500' : 'text-gray-400')">
              {{ otherUser?.is_online ? 'En ligne' : 'Hors ligne' }}
            </p>
          </div>
        </div>

        <div ref="messagesContainer" class="flex-1 overflow-y-auto px-5 py-4">
          <div v-if="messagesLoading" class="flex items-center justify-center py-10">
            <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Chargement des messages...</p>
          </div>

          <div v-else-if="messages.length === 0" class="flex items-center justify-center py-10">
            <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Aucun message. Dites bonjour !</p>
          </div>

          <div v-else class="flex flex-col gap-1.5 w-full">
            <div
              v-for="msg in messages"
              :key="msg.id"
              :class="msg.sender_id === me?.id ? 'items-end' : 'items-start'"
              class="flex flex-col w-full"
            >
              <div
                :class="msg.sender_id === me?.id
                  ? 'bg-gray-900 text-white rounded-2xl rounded-br-md'
                  : dark
                    ? 'bg-gray-700 border border-gray-600 text-gray-100 rounded-2xl rounded-bl-md'
                    : 'bg-white border border-rose-100 text-gray-800 rounded-2xl rounded-bl-md'"
                class="max-w-[70%] px-4 py-2.5 shadow-sm overflow-hidden"
                style="word-break: break-all;"
              >
                <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
              </div>
              <span
                :class="msg.sender_id === me?.id ? 'text-right' : 'text-left'"
                class="text-[10px] mt-0.5 px-1 flex items-center gap-1"
                :style="msg.sender_id === me?.id ? 'justify-content: flex-end' : ''"
              >
                <span :class="dark ? 'text-gray-500' : 'text-gray-400'">{{ formatTime(msg.created_at) }}</span>
                <template v-if="msg.sender_id === me?.id">
                  <svg v-if="msg.is_read" xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round" class="text-blue-500">
                    <path d="M18 6L7 17l-5-5"/><path d="M22 10L11 21"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'">
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                </template>
              </span>
            </div>
          </div>
        </div>

        <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="px-5 py-3 border-t">
          <div class="flex items-center gap-3">
            <input
              v-model="newMessage"
              @keydown.enter.exact.prevent="sendMessage"
              placeholder="Écrire un message..."
              :class="dark
                ? 'bg-gray-800 text-white placeholder-gray-500 focus:bg-gray-750'
                : 'bg-rose-50 text-gray-700 placeholder-gray-400 focus:bg-rose-100/50'"
              class="flex-1 rounded-full px-5 py-2.5 text-sm focus:outline-none transition-colors"
            />
            <button
              @click="sendMessage"
              :disabled="!newMessage.trim()"
              :class="newMessage.trim()
                ? 'bg-gray-900 text-white hover:bg-gray-800'
                : (dark ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-100 text-gray-300 cursor-not-allowed')"
              class="p-2.5 rounded-full transition-all"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>