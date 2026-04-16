<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import {
  getFollowingPosts, createPost, likePost, unlikePost,
  getSuggestions, followUser, getFollowing
} from '../api'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const user = computed(() => userStore.user)
const dark = computed(() => themeStore.dark)
const API = 'http://localhost:8000'
const RAWG_KEY = '04bb0cb2a9604bf39f6bddde196ff9ef'

const posts = ref([])
const newPostContent = ref('')
const newPostGame = ref(null)
const posting = ref(false)
const suggestions = ref([])
const following = ref([])
const feedLoading = ref(true)

// Game search
const gameQuery = ref('')
const gameResults = ref([])
const gameSearching = ref(false)
const showGameDropdown = ref(false)
let gameTimeout = null

watch(gameQuery, (val) => {
  clearTimeout(gameTimeout)
  if (!val.trim()) { gameResults.value = []; return }
  gameSearching.value = true
  gameTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`https://api.rawg.io/api/games?search=${encodeURIComponent(val)}&key=${RAWG_KEY}&page_size=15`)
      const data = await res.json()
      gameResults.value = (data.results || []).map(g => ({
        id: g.id,
        name: g.name,
        image: g.background_image,
        genres: g.genres?.map(x => x.name).join(', ') || ''
      }))
    } catch (e) { console.error(e); gameResults.value = [] }
    finally { gameSearching.value = false }
  }, 350)
})

function openGameDropdown() {
  showGameDropdown.value = true
  gameQuery.value = ''
  gameResults.value = []
}

function closeGameDropdown() {
  showGameDropdown.value = false
}

function selectGame(game) {
  newPostGame.value = { name: game.name, image: game.image }
  closeGameDropdown()
}

function removeGame() { newPostGame.value = null }

const onlineFriends = computed(() => following.value.filter(f => f.user?.is_online).map(f => f.user))

function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url === '/def_user.png') return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function formatDate(dateStr) {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return "à l'instant"
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `${Math.floor(diff / 86400)}j`
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function parsePost(post) {
  const match = post.content?.match(/^\[(.+?)\]\s*(.*)$/s)
  if (match) return { game: match[1], content: match[2] }
  return { game: null, content: post.content }
}

async function loadFeed() {
  feedLoading.value = true
  try { posts.value = await getFollowingPosts() }
  catch (e) { console.error(e) }
  finally { feedLoading.value = false }
}

async function handleCreatePost() {
  if (!newPostContent.value.trim() || posting.value) return
  posting.value = true
  try {
    const content = newPostGame.value
      ? `[${newPostGame.value.name}] ${newPostContent.value.trim()}`
      : newPostContent.value.trim()
    await createPost(content)
    newPostContent.value = ''
    newPostGame.value = null
    await loadFeed()
  } catch (e) { console.error(e) } finally { posting.value = false }
}

async function handleLike(e, post) {
  e.stopPropagation()
  try {
    if (post.is_liked) { await unlikePost(post.id); post.is_liked = false; post.like_count-- }
    else { await likePost(post.id); post.is_liked = true; post.like_count++ }
  } catch (err) { console.error(err) }
}

function goToPost(postId) { router.push(`/post/${postId}`) }

async function handleFollow(userId) {
  try {
    await followUser(userId)
    suggestions.value = suggestions.value.filter(s => s.id !== userId)
    if (user.value) following.value = await getFollowing(user.value.id)
    await loadFeed()
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  await loadFeed()
  if (user.value) {
    try { suggestions.value = await getSuggestions() } catch (e) { console.error(e) }
    try { following.value = await getFollowing(user.value.id) } catch (e) { console.error(e) }
  }
})
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50/50'" class="min-h-[calc(100vh-64px)]">

    <!-- Backdrop -->
    <div v-if="showGameDropdown" class="fixed inset-0 z-40" @click="closeGameDropdown" />

    <div class="max-w-6xl mx-auto flex gap-5 px-4 py-5">

      <div class="flex-1 min-w-0">

        <!-- Create post -->
        <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="rounded-2xl border mb-5 shadow-sm overflow-visible">
          <div class="p-5">
            <div class="flex gap-3">
              <img :src="avatarUrl(user)" class="h-11 w-11 rounded-full object-cover flex-shrink-0" />
              <div class="flex-1">
                <textarea v-model="newPostContent" placeholder="Quoi de neuf ?" rows="2" :class="dark ? 'text-white placeholder-gray-500' : 'text-gray-800 placeholder-gray-400'" class="w-full resize-none bg-transparent focus:outline-none text-[15px] leading-relaxed" @keydown.ctrl.enter="handleCreatePost" />

                <!-- Selected game tag -->
                <div v-if="newPostGame" class="mt-2 flex items-center gap-2">
                  <span :class="dark ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-700'" class="inline-flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full">
                    <img v-if="newPostGame.image" :src="newPostGame.image" class="w-4 h-4 rounded object-cover" />
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
                    {{ newPostGame.name }}
                    <button @click="removeGame" class="opacity-60 hover:opacity-100 transition-opacity">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div :class="dark ? 'border-gray-700 bg-gray-800/50' : 'border-rose-50 bg-rose-50/30'" class="relative flex items-center justify-between px-5 py-3 border-t">
            <div class="relative">
              <button @click.stop="openGameDropdown" :class="dark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600'" class="flex items-center gap-1.5 text-sm transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
                <span class="text-xs font-medium">Tag un jeu</span>
              </button>

              <!-- Game search dropdown -->
              <div
                v-if="showGameDropdown"
                @click.stop
                :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'"
                class="absolute left-0 top-full mt-2 w-80 rounded-xl shadow-2xl border overflow-hidden z-50"
              >
                <div class="p-3">
                  <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="absolute left-3 top-1/2 -translate-y-1/2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    <input
                      v-model="gameQuery"
                      placeholder="Rechercher un jeu..."
                      :class="dark ? 'bg-gray-900 text-white placeholder-gray-500 border-gray-700 focus:border-gray-500' : 'bg-gray-50 text-gray-800 placeholder-gray-400 border-gray-200 focus:border-gray-400'"
                      class="w-full pl-9 pr-3 py-2 rounded-lg border text-sm focus:outline-none transition-colors"
                      ref="gameSearchInput"
                    />
                  </div>
                </div>
                <div class="max-h-[420px] overflow-y-auto">
                  <div v-if="gameSearching" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-4 py-6 text-xs text-center">Recherche...</div>
                  <div v-else-if="gameQuery.trim() && gameResults.length === 0 && !gameSearching" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-4 py-6 text-xs text-center">Aucun jeu trouvé</div>
                  <button
                    v-for="game in gameResults" :key="game.id"
                    @click="selectGame(game)"
                    :class="dark ? 'hover:bg-gray-700' : 'hover:bg-gray-50'"
                    class="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors"
                  >
                    <img v-if="game.image" :src="game.image" class="w-12 h-12 rounded-lg object-cover flex-shrink-0" />
                    <div v-else :class="dark ? 'bg-gray-700' : 'bg-gray-200'" class="w-12 h-12 rounded-lg flex-shrink-0 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
                    </div>
                    <div class="min-w-0 flex-1">
                      <p :class="dark ? 'text-white' : 'text-gray-900'" class="text-sm font-medium truncate">{{ game.name }}</p>
                      <p class="text-gray-400 text-xs truncate">{{ game.genres || 'Jeu vidéo' }}</p>
                    </div>
                  </button>
                </div>
                <div v-if="!gameQuery.trim() && gameResults.length === 0" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-4 py-8 text-xs text-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mx-auto mb-2 opacity-40"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
                  Tapez le nom d'un jeu
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span :class="dark ? 'text-gray-600' : 'text-gray-300'" class="text-[11px] hidden sm:block">Ctrl+Enter</span>
              <button @click="handleCreatePost" :disabled="!newPostContent.trim() || posting" :class="newPostContent.trim() && !posting ? 'bg-gray-900 hover:bg-gray-800 text-white' : (dark ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-100 text-gray-300 cursor-not-allowed')" class="px-5 py-1.5 rounded-full text-sm font-medium transition-all">{{ posting ? 'Envoi...' : 'Publier' }}</button>
            </div>
          </div>
        </div>

        <div v-if="feedLoading" class="text-center py-16"><p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Chargement...</p></div>

        <div v-else-if="posts.length === 0" class="text-center py-16">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-600' : 'text-gray-300'" class="mx-auto mb-3"><circle cx="12" cy="12" r="10"/><path d="M8 15h8M9 9h.01M15 9h.01"/></svg>
          <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm font-medium">Rien ici pour le moment</p>
          <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-xs mt-1">Suivez des joueurs pour voir leurs posts</p>
        </div>

        <!-- Posts -->
        <div
          v-for="post in posts" :key="post.id"
          @click="goToPost(post.id)"
          :class="dark ? 'bg-gray-900 border-gray-700 hover:border-gray-600' : 'bg-white border-rose-100 hover:border-rose-200'"
          class="rounded-2xl border mb-3 overflow-hidden shadow-sm hover:shadow-md transition-all cursor-pointer"
        >
          <div class="p-5">
            <div class="flex items-start gap-3">
              <router-link :to="`/user/${post.author_id}`" @click.stop>
                <img :src="avatarUrl(post.author)" class="h-11 w-11 rounded-full object-cover flex-shrink-0" />
              </router-link>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <router-link :to="`/user/${post.author_id}`" @click.stop :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-[15px] hover:underline">{{ post.author?.display_name || post.author?.username }}</router-link>
                  <span class="text-gray-400 text-sm">@{{ post.author?.username }}</span>
                  <span :class="dark ? 'text-gray-600' : 'text-gray-300'" class="text-sm">·</span>
                  <span class="text-gray-400 text-sm">{{ formatDate(post.created_at) }}</span>
                </div>
                <span v-if="parsePost(post).game" :class="dark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'" class="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full mt-1.5">
                  <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
                  {{ parsePost(post).game }}
                </span>
                <p :class="dark ? 'text-gray-200' : 'text-gray-800'" class="text-[15px] leading-relaxed mt-2 whitespace-pre-wrap">{{ parsePost(post).content }}</p>
                <img v-if="post.image_url" :src="post.image_url.startsWith('http') ? post.image_url : `${API}${post.image_url}`" class="mt-3 rounded-xl max-h-96 w-full object-cover" />
                <div class="flex items-center gap-6 mt-4">
                  <button @click="handleLike($event, post)" class="group flex items-center gap-1.5">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" :fill="post.is_liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="post.is_liked ? 'text-rose-500' : (dark ? 'text-gray-500 group-hover:text-rose-500' : 'text-gray-400 group-hover:text-rose-500')" class="transition-colors"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    <span :class="post.is_liked ? 'text-rose-500' : (dark ? 'text-gray-500' : 'text-gray-400')" class="text-sm">{{ post.like_count }}</span>
                  </button>
                  <div class="flex items-center gap-1.5">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    <span :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">{{ post.comment_count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="w-80 flex-shrink-0 hidden lg:block">
        <div class="sticky top-[84px] flex flex-col gap-4">
          <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="rounded-2xl border overflow-hidden shadow-sm">
            <div class="px-5 pt-4 pb-2 flex items-center justify-between">
              <p :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-[15px]">Amis en ligne</p>
              <span v-if="onlineFriends.length > 0" class="flex items-center gap-1.5 text-xs text-green-500"><span class="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>{{ onlineFriends.length }}</span>
            </div>
            <div v-if="onlineFriends.length === 0" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-5 py-6 text-center text-sm">Personne en ligne</div>
            <router-link v-for="friend in onlineFriends" :key="friend.id" :to="`/user/${friend.id}`" :class="dark ? 'hover:bg-gray-800' : 'hover:bg-gray-50'" class="flex items-center gap-3 px-5 py-3 transition-colors">
              <div class="relative flex-shrink-0"><img :src="avatarUrl(friend)" class="h-10 w-10 rounded-full object-cover" /><div :class="dark ? 'border-gray-900' : 'border-white'" class="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-green-400 rounded-full border-2"></div></div>
              <div class="flex-1 min-w-0"><p :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm truncate">{{ friend.display_name || friend.username }}</p><p class="text-xs text-green-500">En ligne</p></div>
            </router-link>
            <div v-if="following.filter(f => !f.user?.is_online).length > 0" :class="dark ? 'border-gray-700' : 'border-gray-100'" class="border-t">
              <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-5 pt-3 pb-1 text-[11px] uppercase tracking-wide font-medium">Hors ligne</p>
              <router-link v-for="f in following.filter(f => !f.user?.is_online).slice(0, 5)" :key="f.id" :to="`/user/${f.user.id}`" :class="dark ? 'hover:bg-gray-800' : 'hover:bg-gray-50'" class="flex items-center gap-3 px-5 py-2.5 transition-colors">
                <img :src="avatarUrl(f.user)" class="h-8 w-8 rounded-full object-cover flex-shrink-0 opacity-60" />
                <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm truncate">{{ f.user.display_name || f.user.username }}</p>
              </router-link>
            </div>
          </div>
          <div v-if="suggestions.length > 0" :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="rounded-2xl border overflow-hidden shadow-sm">
            <p :class="dark ? 'text-white' : 'text-gray-900'" class="px-5 pt-4 pb-2 font-bold text-[15px]">Suggestions</p>
            <div v-for="s in suggestions.slice(0, 4)" :key="s.id" :class="dark ? 'hover:bg-gray-800' : 'hover:bg-gray-50'" class="flex items-center gap-3 px-5 py-3 transition-colors">
              <router-link :to="`/user/${s.id}`"><img :src="avatarUrl(s)" class="h-10 w-10 rounded-full object-cover flex-shrink-0" /></router-link>
              <div class="flex-1 min-w-0"><router-link :to="`/user/${s.id}`" :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm truncate block hover:underline">{{ s.display_name || s.username }}</router-link><p class="text-xs text-gray-400 truncate">@{{ s.username }}</p></div>
              <button @click="handleFollow(s.id)" class="bg-gray-900 text-white text-xs font-semibold px-4 py-1.5 rounded-full hover:bg-gray-800 transition-colors flex-shrink-0">Suivre</button>
            </div>
          </div>
          <p :class="dark ? 'text-gray-600' : 'text-gray-300'" class="text-[11px] text-center">ft_transcendence · 42 · 2026</p>
        </div>
      </div>
    </div>
  </div>
</template>