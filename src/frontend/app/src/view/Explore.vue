<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { getPosts, likePost, unlikePost } from '../api'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const user = computed(() => userStore.user)
const dark = computed(() => themeStore.dark)
const API = ''
const RAWG_KEY = '04bb0cb2a9604bf39f6bddde196ff9ef'

const allPosts = ref([])
const loading = ref(true)
const activeGame = ref('all')
const sortBy = ref('recent')
const gameSearch = ref('')
const rawgResults = ref([])
const rawgLoading = ref(false)
const showGameSearch = ref(false)
let rawgTimeout = null

function parsePost(post) {
  const match = post.content?.match(/^\[(.+?)\]\s*(.*)$/s)
  if (match) return { game: match[1], content: match[2] }
  return { game: null, content: post.content }
}

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

watch(gameSearch, (val) => {
  clearTimeout(rawgTimeout)
  if (!val.trim()) { rawgResults.value = []; return }
  rawgLoading.value = true
  rawgTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`https://api.rawg.io/api/games?search=${encodeURIComponent(val)}&key=${RAWG_KEY}&page_size=8`)
      const data = await res.json()
      rawgResults.value = (data.results || []).map(g => ({
        id: g.id,
        name: g.name,
        image: g.background_image,
        genres: g.genres?.map(x => x.name).join(', ') || ''
      }))
    } catch (e) { console.error(e); rawgResults.value = [] }
    finally { rawgLoading.value = false }
  }, 400)
})

function selectRawgGame(game) {
  activeGame.value = game.name
  gameSearch.value = ''
  rawgResults.value = []
  showGameSearch.value = false
}

const gamePostCounts = computed(() => {
  const counts = {}
  allPosts.value.forEach(post => {
    const parsed = parsePost(post)
    if (parsed.game) counts[parsed.game] = (counts[parsed.game] || 0) + 1
  })
  return counts
})

const availableGames = computed(() => {
  return Object.entries(gamePostCounts.value)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({ name, count }))
})

const filteredPosts = computed(() => {
  let result = [...allPosts.value]
  if (activeGame.value !== 'all') {
    result = result.filter(post => parsePost(post).game === activeGame.value)
  }
  if (sortBy.value === 'popular') result.sort((a, b) => b.like_count - a.like_count)
  return result
})

async function handleLike(e, post) {
  e.stopPropagation()
  try {
    if (post.is_liked) { await unlikePost(post.id); post.is_liked = false; post.like_count-- }
    else { await likePost(post.id); post.is_liked = true; post.like_count++ }
  } catch (err) { console.error(err) }
}

function goToPost(postId) { router.push(`/post/${postId}`) }

onMounted(async () => {
  try { allPosts.value = await getPosts() }
  catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50/50'" class="min-h-[calc(100vh-64px)]">
    <div class="max-w-4xl mx-auto px-4 py-5">

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 :class="dark ? 'text-white' : 'text-gray-900'" class="text-2xl font-bold">Explorer</h1>
          <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm mt-0.5">Découvrez ce que la communauté partage</p>
        </div>
      </div>

      <!-- Filters -->
      <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="rounded-2xl border p-4 mb-5 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-xs font-semibold uppercase tracking-wide">Filtrer par jeu</p>
          </div>
          <div class="flex items-center gap-1">
            <button @click="sortBy = 'recent'" :class="sortBy === 'recent' ? (dark ? 'bg-white/10 text-white' : 'bg-gray-900 text-white') : (dark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600')" class="px-3 py-1 rounded-full text-xs font-medium transition-all flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Récents
            </button>
            <button @click="sortBy = 'popular'" :class="sortBy === 'popular' ? (dark ? 'bg-white/10 text-white' : 'bg-gray-900 text-white') : (dark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600')" class="px-3 py-1 rounded-full text-xs font-medium transition-all flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>Populaires
            </button>
          </div>
        </div>

        <!-- Game tags -->
        <div class="flex flex-wrap gap-2 mb-3">
          <button @click="activeGame = 'all'" :class="activeGame === 'all' ? (dark ? 'bg-white/10 text-white ring-1 ring-white/20' : 'bg-gray-900 text-white') : (dark ? 'bg-gray-800 text-gray-400 hover:bg-gray-750' : 'bg-gray-100 text-gray-500 hover:bg-gray-200')" class="px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
            Tous <span class="opacity-50">{{ allPosts.length }}</span>
          </button>
          <button v-for="game in availableGames" :key="game.name" @click="activeGame = game.name" :class="activeGame === game.name ? (dark ? 'bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/30' : 'bg-rose-100 text-rose-700 ring-1 ring-rose-200') : (dark ? 'bg-gray-800 text-gray-400 hover:bg-gray-750' : 'bg-gray-100 text-gray-500 hover:bg-gray-200')" class="px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5">
            {{ game.name }} <span class="opacity-50">{{ game.count }}</span>
          </button>
        </div>

        <!-- RAWG search -->
        <div class="relative">
          <div class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="gameSearch" @focus="showGameSearch = true" placeholder="Rechercher un jeu..." :class="dark ? 'bg-gray-800 text-white placeholder-gray-500' : 'bg-gray-50 text-gray-700 placeholder-gray-400'" class="flex-1 rounded-lg px-3 py-1.5 text-xs focus:outline-none transition-colors" />
          </div>
          <div v-if="showGameSearch && (rawgResults.length > 0 || rawgLoading)" :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'" class="absolute left-0 right-0 mt-2 rounded-xl shadow-xl border overflow-hidden z-50">
            <div v-if="rawgLoading" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-4 py-3 text-xs text-center">Recherche...</div>
            <button v-for="game in rawgResults" :key="game.id" @click="selectRawgGame(game)" :class="dark ? 'hover:bg-gray-700' : 'hover:bg-gray-50'" class="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors">
              <img v-if="game.image" :src="game.image" class="w-10 h-10 rounded-lg object-cover flex-shrink-0" />
              <div v-else :class="dark ? 'bg-gray-700' : 'bg-gray-200'" class="w-10 h-10 rounded-lg flex-shrink-0 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-500' : 'text-gray-400'"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
              </div>
              <div class="min-w-0 flex-1">
                <p :class="dark ? 'text-white' : 'text-gray-900'" class="text-sm font-medium truncate">{{ game.name }}</p>
                <p class="text-gray-400 text-xs truncate">{{ game.genres || 'Jeu vidéo' }}</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-20"><p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Chargement...</p></div>

      <div v-else-if="filteredPosts.length === 0" class="text-center py-20">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-600' : 'text-gray-300'" class="mx-auto mb-3"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm font-medium">{{ activeGame !== 'all' ? `Aucun post sur ${activeGame}` : 'Aucun post' }}</p>
        <button v-if="activeGame !== 'all'" @click="activeGame = 'all'" class="text-rose-500 text-xs mt-2 hover:underline">Voir tous les posts</button>
      </div>

      <!-- Posts -->
      <div v-for="post in filteredPosts" :key="post.id" @click="goToPost(post.id)" :class="dark ? 'bg-gray-900 border-gray-700 hover:border-gray-600' : 'bg-white border-rose-100 hover:border-rose-200'" class="rounded-2xl border mb-3 overflow-hidden shadow-sm hover:shadow-md transition-all cursor-pointer">
        <div class="p-5">
          <div class="flex items-start gap-3">
            <router-link :to="`/user/${post.author_id}`" @click.stop><img :src="avatarUrl(post.author)" class="h-11 w-11 rounded-full object-cover flex-shrink-0" /></router-link>
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
  </div>
  <div v-if="showGameSearch && rawgResults.length > 0" class="fixed inset-0 z-40" @click="showGameSearch = false" />
</template>