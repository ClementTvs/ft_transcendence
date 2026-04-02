<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import {
  getPosts, createPost, likePost, unlikePost,
  getComments, createComment,
  getSuggestions, followUser
} from '../api'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const API = 'http://localhost:8000'

// ── State ──
const posts = ref([])
const newPostContent = ref('')
const newPostGame = ref('')
const posting = ref(false)
const suggestions = ref([])
const expandedComments = ref({})
const commentTexts = ref({})
const commentsData = ref({})
const loadingComments = ref({})
const showGamePicker = ref(false)

// Game tags disponibles
const gamesList = [
  { name: 'League of Legends', icon: '⚔️', color: 'bg-amber-100 text-amber-700' },
  { name: 'Valorant', icon: '🔫', color: 'bg-red-100 text-red-600' },
  { name: 'CS2', icon: '💣', color: 'bg-orange-100 text-orange-700' },
  { name: 'Minecraft', icon: '⛏️', color: 'bg-green-100 text-green-700' },
  { name: 'Fortnite', icon: '🏗️', color: 'bg-blue-100 text-blue-600' },
  { name: 'Rocket League', icon: '🚀', color: 'bg-sky-100 text-sky-600' },
  { name: 'GTA V', icon: '🚗', color: 'bg-purple-100 text-purple-600' },
  { name: 'Apex Legends', icon: '🎯', color: 'bg-rose-100 text-rose-600' },
  { name: 'Overwatch 2', icon: '🛡️', color: 'bg-orange-100 text-orange-600' },
  { name: 'Genshin Impact', icon: '✨', color: 'bg-teal-100 text-teal-600' },
  { name: 'Phasmophobia', icon: '👻', color: 'bg-gray-200 text-gray-700' },
  { name: 'Autre', icon: '🎮', color: 'bg-gray-100 text-gray-600' },
]

// Placeholder: amis en ligne avec jeu actuel
// TODO: remplacer par un vrai appel API quand le back sera prêt
const onlineFriends = ref([
  { id: 1, username: 'qq', display_name: 'qq', avatar_url: '/def_user.png', is_online: true, playing: 'League of Legends' },
])

function getGameInfo(name) {
  return gamesList.find(g => g.name === name) || { name, icon: '🎮', color: 'bg-gray-100 text-gray-600' }
}

// ── Helpers ──
function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/uploads')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function formatDate(dateStr) {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return 'à l\'instant'
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `${Math.floor(diff / 86400)}j`
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

// ── Actions ──
async function loadFeed() {
  try {
    posts.value = await getPosts()
  } catch (e) {
    console.error('Erreur chargement feed:', e)
  }
}

function selectGame(game) {
  newPostGame.value = game.name
  showGamePicker.value = false
}

function removeGame() {
  newPostGame.value = ''
}

async function handleCreatePost() {
  if (!newPostContent.value.trim() || posting.value) return
  posting.value = true
  try {
    // On envoie le contenu avec le tag jeu en préfixe pour le moment
    // TODO: quand le back supportera un champ "game", l'envoyer séparément
    const content = newPostGame.value
      ? `[${newPostGame.value}] ${newPostContent.value.trim()}`
      : newPostContent.value.trim()
    await createPost(content)
    newPostContent.value = ''
    newPostGame.value = ''
    await loadFeed()
  } catch (e) {
    console.error('Erreur création post:', e)
  } finally {
    posting.value = false
  }
}

// Parse un tag jeu depuis le contenu du post (format: [NomDuJeu] contenu)
function parsePost(post) {
  const match = post.content?.match(/^\[(.+?)\]\s*(.*)$/s)
  if (match) {
    return { game: match[1], content: match[2] }
  }
  return { game: null, content: post.content }
}

async function handleLike(post) {
  try {
    if (post.is_liked) {
      await unlikePost(post.id)
      post.is_liked = false
      post.like_count--
    } else {
      await likePost(post.id)
      post.is_liked = true
      post.like_count++
    }
  } catch (e) {
    console.error('Erreur like:', e)
  }
}

async function toggleComments(postId) {
  expandedComments.value[postId] = !expandedComments.value[postId]
  if (expandedComments.value[postId] && !commentsData.value[postId]) {
    loadingComments.value[postId] = true
    try {
      commentsData.value[postId] = await getComments(postId)
    } catch (e) {
      commentsData.value[postId] = []
    } finally {
      loadingComments.value[postId] = false
    }
  }
}

async function handleComment(postId) {
  const text = commentTexts.value[postId]?.trim()
  if (!text) return
  try {
    await createComment(postId, text)
    commentTexts.value[postId] = ''
    commentsData.value[postId] = await getComments(postId)
    const post = posts.value.find(p => p.id === postId)
    if (post) post.comment_count++
  } catch (e) {
    console.error('Erreur envoi commentaire:', e)
  }
}

async function handleFollow(userId) {
  try {
    await followUser(userId)
    suggestions.value = suggestions.value.filter(s => s.id !== userId)
  } catch (e) {
    console.error('Erreur follow:', e)
  }
}

onMounted(async () => {
  await loadFeed()
  if (user.value) {
    try { suggestions.value = await getSuggestions() } catch (e) { console.error(e) }
  }
})
</script>

<template>
  <div class="min-h-[calc(100vh-64px)] bg-rose-50/50">
    <div class="max-w-6xl mx-auto flex gap-5 px-4 py-5">

      <div class="flex-1 min-w-0">

        <div class="bg-white rounded-2xl border border-rose-100 mb-5 shadow-sm overflow-hidden">
          <div class="p-5">
            <div class="flex gap-3">
              <img :src="avatarUrl(user)" class="h-11 w-11 rounded-full object-cover flex-shrink-0" />
              <div class="flex-1">
                <textarea
                  v-model="newPostContent"
                  placeholder="Partage quelque chose avec la commu..."
                  rows="2"
                  class="w-full resize-none bg-transparent text-gray-800 placeholder-gray-400 focus:outline-none text-[15px] leading-relaxed"
                  @keydown.ctrl.enter="handleCreatePost"
                />
                <!-- Game tag sélectionné -->
                <div v-if="newPostGame" class="mt-2 flex items-center gap-2">
                  <span
                    :class="getGameInfo(newPostGame).color"
                    class="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
                  >
                    {{ getGameInfo(newPostGame).icon }} {{ newPostGame }}
                    <button @click="removeGame" class="ml-1 opacity-60 hover:opacity-100">✕</button>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between px-5 py-3 border-t border-rose-50 bg-rose-50/30">
            <div class="relative">
              <button
                @click="showGamePicker = !showGamePicker"
                class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors"
              >
                <span class="text-base">🎮</span>
                <span class="text-xs font-medium">Tag un jeu</span>
              </button>
              <div
                v-if="showGamePicker"
                class="absolute bottom-full left-0 mb-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
              >
                <div class="max-h-64 overflow-y-auto py-1">
                  <button
                    v-for="game in gamesList"
                    :key="game.name"
                    @click="selectGame(game)"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 transition-colors"
                  >
                    <span>{{ game.icon }}</span>
                    <span>{{ game.name }}</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-[11px] text-gray-300 hidden sm:block">Ctrl+Enter</span>
              <button
                @click="handleCreatePost"
                :disabled="!newPostContent.trim() || posting"
                :class="newPostContent.trim() && !posting
                  ? 'bg-gray-900 hover:bg-gray-800 text-white'
                  : 'bg-gray-100 text-gray-300 cursor-not-allowed'"
                class="px-5 py-1.5 rounded-full text-sm font-medium transition-all"
              >
                {{ posting ? 'Envoi...' : 'Publier' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="posts.length === 0" class="text-center py-20">
          <p class="text-2xl mb-2">🎮</p>
          <p class="text-gray-400 text-sm">Aucun post pour le moment</p>
          <p class="text-gray-300 text-xs mt-1">Soyez le premier à publier !</p>
        </div>

        <div
          v-for="post in posts"
          :key="post.id"
          class="bg-white rounded-2xl border border-rose-100 mb-3 overflow-hidden shadow-sm hover:shadow-md hover:shadow-rose-100/40 transition-all"
        >
          <div class="p-5">
            <div class="flex items-start gap-3">
              <img :src="avatarUrl(post.author)" class="h-11 w-11 rounded-full object-cover flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-bold text-gray-900 text-[15px]">{{ post.author?.display_name || post.author?.username }}</span>
                  <span class="text-gray-400 text-sm">@{{ post.author?.username }}</span>
                  <span class="text-gray-300 text-sm">·</span>
                  <span class="text-gray-400 text-sm">{{ formatDate(post.created_at) }}</span>
                </div>

                <span
                  v-if="parsePost(post).game"
                  :class="getGameInfo(parsePost(post).game).color"
                  class="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full mt-1.5"
                >
                  {{ getGameInfo(parsePost(post).game).icon }} {{ parsePost(post).game }}
                </span>

                <p class="text-gray-800 text-[15px] leading-relaxed mt-2 whitespace-pre-wrap">{{ parsePost(post).content }}</p>

                <div class="flex items-center gap-8 mt-4">
                  <button @click="handleLike(post)" class="group flex items-center gap-2">
                    <div
                      :class="post.is_liked ? 'bg-rose-50 text-rose-500' : 'text-gray-400 group-hover:bg-rose-50 group-hover:text-rose-500'"
                      class="p-1.5 rounded-full transition-all"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24"
                        :fill="post.is_liked ? 'currentColor' : 'none'"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                      </svg>
                    </div>
                    <span :class="post.is_liked ? 'text-rose-500' : 'text-gray-400 group-hover:text-rose-500'" class="text-sm transition-colors">{{ post.like_count }}</span>
                  </button>

                  <button @click="toggleComments(post.id)" class="group flex items-center gap-2">
                    <div
                      :class="expandedComments[post.id] ? 'bg-sky-50 text-sky-500' : 'text-gray-400 group-hover:bg-sky-50 group-hover:text-sky-500'"
                      class="p-1.5 rounded-full transition-all"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                      </svg>
                    </div>
                    <span :class="expandedComments[post.id] ? 'text-sky-500' : 'text-gray-400 group-hover:text-sky-500'" class="text-sm transition-colors">{{ post.comment_count }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="expandedComments[post.id]" class="border-t border-gray-100 bg-gray-50/50">
            <div v-if="loadingComments[post.id]" class="px-5 py-6 text-center text-gray-400 text-sm">Chargement...</div>
            <div v-else>
              <div v-if="commentsData[post.id]?.length === 0" class="px-5 py-6 text-center text-gray-400 text-sm">Pas encore de commentaire</div>
              <div
                v-for="comment in commentsData[post.id]"
                :key="comment.id"
                class="px-5 py-3 flex gap-3 border-b border-gray-100/50 last:border-0"
              >
                <img :src="avatarUrl(comment.author)" class="h-8 w-8 rounded-full object-cover flex-shrink-0 mt-0.5" />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-semibold text-gray-800 text-sm">{{ comment.author?.display_name || comment.author?.username }}</span>
                    <span class="text-gray-400 text-xs">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <p class="text-gray-700 text-sm leading-relaxed mt-0.5">{{ comment.content }}</p>
                </div>
              </div>
            </div>
            <div class="px-5 py-3 flex gap-3 items-center bg-white border-t border-gray-100">
              <img :src="avatarUrl(user)" class="h-8 w-8 rounded-full object-cover flex-shrink-0" />
              <input
                v-model="commentTexts[post.id]"
                @keydown.enter="handleComment(post.id)"
                placeholder="Écrire un commentaire..."
                class="flex-1 bg-gray-50 rounded-full px-4 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:bg-gray-100 transition-colors"
              />
              <button
                @click="handleComment(post.id)"
                :disabled="!commentTexts[post.id]?.trim()"
                :class="commentTexts[post.id]?.trim() ? 'bg-gray-900 text-white hover:bg-gray-800' : 'bg-gray-100 text-gray-300 cursor-not-allowed'"
                class="px-4 py-2 rounded-full text-sm font-medium transition-all"
              >→</button>
            </div>
          </div>
        </div>
      </div>

      <div class="w-80 flex-shrink-0 hidden lg:block">
        <div class="sticky top-[84px] flex flex-col gap-4">

          <div class="bg-white rounded-2xl border border-rose-100 overflow-hidden shadow-sm">
            <div class="px-5 pt-4 pb-2 flex items-center justify-between">
              <p class="font-bold text-gray-900 text-[15px]">En ligne</p>
              <span class="flex items-center gap-1.5 text-xs text-green-500">
                <span class="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
                {{ onlineFriends.length }}
              </span>
            </div>
            <div v-if="onlineFriends.length === 0" class="px-5 py-6 text-center text-gray-400 text-sm">
              Personne en ligne
            </div>
            <div
              v-for="friend in onlineFriends"
              :key="friend.id"
              class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors"
            >
              <div class="relative flex-shrink-0">
                <img :src="avatarUrl(friend)" class="h-10 w-10 rounded-full object-cover" />
                <div class="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-green-400 rounded-full border-2 border-white"></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 text-sm truncate">{{ friend.display_name || friend.username }}</p>
                <p v-if="friend.playing" class="text-xs text-gray-400 truncate flex items-center gap-1">
                  <span>🎮</span>
                  <span class="text-green-600 font-medium">{{ friend.playing }}</span>
                </p>
              </div>
            </div>
          </div>

          <div v-if="suggestions.length > 0" class="bg-white rounded-2xl border border-rose-100 overflow-hidden shadow-sm">
            <p class="px-5 pt-4 pb-2 font-bold text-gray-900 text-[15px]">À suivre</p>
            <div
              v-for="s in suggestions.slice(0, 4)"
              :key="s.id"
              class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors"
            >
              <img :src="avatarUrl(s)" class="h-10 w-10 rounded-full object-cover flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 text-sm truncate">{{ s.display_name || s.username }}</p>
                <p class="text-xs text-gray-400 truncate">@{{ s.username }}</p>
              </div>
              <button
                @click="handleFollow(s.id)"
                class="bg-gray-900 text-white text-xs font-semibold px-4 py-1.5 rounded-full hover:bg-gray-800 transition-colors flex-shrink-0"
              >
                Suivre
              </button>
            </div>
          </div>

          <div v-if="user" class="bg-white rounded-2xl border border-rose-100 p-5 shadow-sm">
            <div class="flex items-center gap-3">
              <router-link to="/profile">
                <img :src="avatarUrl(user)" class="h-11 w-11 rounded-full object-cover" />
              </router-link>
              <div class="min-w-0">
                <p class="font-bold text-gray-900 text-sm truncate">{{ user.display_name || user.username }}</p>
                <p class="text-xs text-gray-400 truncate">@{{ user.username }}</p>
              </div>
            </div>
            <router-link
              to="/profile"
              class="block text-center mt-4 py-2 rounded-full border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Mon profil
            </router-link>
          </div>

          <p class="text-[11px] text-gray-300 text-center">ft_transcendence · 42 · 2026</p>
        </div>
      </div>

    </div>
  </div>

  <div v-if="showGamePicker" class="fixed inset-0 z-40" @click="showGamePicker = false" />
</template>