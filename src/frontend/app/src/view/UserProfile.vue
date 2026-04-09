<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  getUserStats, getUserPosts, isFollowing, followUser, unfollowUser,
  getOrCreateConversation
} from '../api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const me = computed(() => userStore.user)

const API = 'http://localhost:8000'

const profile = ref(null)
const stats = ref({ post_count: 0, follower_count: 0, following_count: 0 })
const posts = ref([])
const following = ref(false)
const loading = ref(true)
const followLoading = ref(false)

const isOwnProfile = computed(() => me.value?.id === profile.value?.id)

function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url === '/def_user.png') return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function bannerUrl(u) {
  if (!u?.banner_url) return ''
  if (u.banner_url.startsWith('http')) return u.banner_url
  if (u.banner_url.startsWith('/')) return `${API}${u.banner_url}`
  return u.banner_url
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function loadProfile(userId) {
  loading.value = true
  try {
    const data = await getUserStats(userId)
    profile.value = data
    console.log('profile data:', data)
    console.log('banner_url:', data.banner_url)
    stats.value = {
      post_count: data.post_count,
      follower_count: data.follower_count,
      following_count: data.following_count
    }
    posts.value = await getUserPosts(userId)
    if (me.value && me.value.id !== userId) {
      const res = await isFollowing(userId)
      following.value = res.is_following
    }
  } catch (e) {
    console.error('Erreur chargement profil:', e)
  } finally {
    loading.value = false
  }
}

async function handleFollow() {
  if (!profile.value || followLoading.value) return
  followLoading.value = true
  try {
    if (following.value) {
      await unfollowUser(profile.value.id)
      following.value = false
      stats.value.follower_count--
    } else {
      await followUser(profile.value.id)
      following.value = true
      stats.value.follower_count++
    }
  } catch (e) {
    console.error('Erreur follow:', e)
  } finally {
    followLoading.value = false
  }
}

async function handleDM() {
  if (!profile.value) return
  try {
    await getOrCreateConversation(profile.value.id)
    router.push(`/chat/${profile.value.id}`)
  } catch (e) {
    console.error('Erreur DM:', e)
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) loadProfile(Number(newId))
})

onMounted(() => {
  const userId = Number(route.params.id)
  if (userId) loadProfile(userId)
})
</script>

<template>
  <div class="min-h-screen bg-rose-50">

    <div v-if="loading" class="flex items-center justify-center py-32">
      <p class="text-gray-400 text-sm">Chargement...</p>
    </div>

    <div v-else-if="!profile" class="flex flex-col items-center justify-center py-32">
      <p class="text-gray-400 text-lg mb-2">Utilisateur introuvable</p>
      <button @click="router.push('/')" class="text-rose-500 text-sm hover:text-rose-600">Retour à l'accueil</button>
    </div>

    <template v-else>
      <div
        class="w-full h-48"
        :class="bannerUrl(profile) ? '' : 'bg-gradient-to-br from-gray-800 via-gray-900 to-rose-950'"
      >
        <img v-if="bannerUrl(profile)" :src="bannerUrl(profile)" alt="Banner" class="w-full h-full object-cover" />
      </div>

      <div class="max-w-2xl mx-auto px-6">

        <div class="flex items-end justify-between">
          <div class="w-28 h-28 -mt-14 rounded-full border-4 border-rose-50 bg-gray-800 overflow-hidden">
            <img :src="avatarUrl(profile)" alt="Avatar" class="w-full h-full object-cover" />
          </div>

          <div class="pb-2 flex items-center gap-2">
            <router-link
              v-if="isOwnProfile"
              to="/profile"
              class="px-5 py-2 rounded-full border border-rose-200 text-sm font-medium text-gray-800 hover:bg-gray-800 hover:text-rose-50 hover:border-gray-800 transition-all"
            >
              Modifier le profil
            </router-link>

            <template v-else>
              <button
                @click="handleDM"
                class="p-2 rounded-full border border-gray-300 text-gray-500 hover:text-rose-500 hover:border-rose-300 hover:bg-rose-50 transition-all"
                title="Envoyer un message"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect width="20" height="16" x="2" y="4" rx="2"/>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
              </button>
              <button
                @click="handleFollow"
                :disabled="followLoading"
                :class="following
                  ? 'border-gray-300 text-gray-700 hover:border-red-300 hover:text-red-500 hover:bg-red-50'
                  : 'bg-gray-900 text-white hover:bg-gray-800 border-gray-900'"
                class="px-5 py-2 rounded-full border text-sm font-semibold transition-all"
              >
                {{ followLoading ? '...' : (following ? 'Suivi ✓' : 'Suivre') }}
              </button>
            </template>
          </div>
        </div>

        <!-- Info -->
        <div class="mt-3">
          <h1 class="text-2xl font-bold text-gray-900">{{ profile.display_name || profile.username }}</h1>
          <p class="text-sm text-gray-400">@{{ profile.username }}</p>
          <div class="flex items-center gap-2 mt-1">
            <span v-if="profile.is_online" class="inline-flex items-center gap-1 text-xs text-green-500 font-medium">
              <span class="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span> En ligne
            </span>
            <span v-else class="text-xs text-gray-400">Hors ligne</span>
          </div>
          <p v-if="profile.bio" class="text-sm text-gray-600 mt-2 leading-relaxed">{{ profile.bio }}</p>
        </div>

        <!-- Stats -->
        <div class="flex items-center gap-6 mt-4 py-4 border-b border-rose-200/60">
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900">{{ stats.post_count }}</div>
            <div class="text-xs text-rose-300 uppercase tracking-wide">Posts</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900">{{ stats.follower_count }}</div>
            <div class="text-xs text-rose-300 uppercase tracking-wide">Followers</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900">{{ stats.following_count }}</div>
            <div class="text-xs text-rose-300 uppercase tracking-wide">Following</div>
          </div>
        </div>

        <!-- Posts -->
        <div class="py-4">
          <div v-if="posts.length === 0" class="text-center py-12 text-gray-400 text-sm">Aucun post</div>
          <div
            v-for="post in posts" :key="post.id"
            class="bg-white rounded-xl border border-rose-100 p-4 mb-3 hover:shadow-md hover:shadow-rose-100/50 transition-shadow"
          >
            <div class="flex items-center gap-3 mb-3">
              <img :src="avatarUrl(post.author)" class="h-10 w-10 rounded-full object-cover flex-shrink-0" />
              <div>
                <span class="font-semibold text-gray-900 text-sm">{{ post.author?.display_name || post.author?.username }}</span>
                <span class="ml-2 text-gray-400 text-xs">{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
            <p class="text-gray-800 text-[15px] leading-relaxed whitespace-pre-wrap">{{ post.content }}</p>
            <div class="flex gap-6 mt-3">
              <span class="flex items-center gap-1.5 text-gray-400 text-xs">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                  :fill="post.is_liked ? 'currentColor' : 'none'" :class="post.is_liked ? 'text-rose-500' : ''"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
                {{ post.like_count }}
              </span>
              <span class="flex items-center gap-1.5 text-gray-400 text-xs">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                {{ post.comment_count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>