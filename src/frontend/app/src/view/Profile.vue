<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import { getUserStats, getUserPosts, uploadAvatar, uploadBanner } from '../api'

const userStore = useUserStore()
const themeStore = useThemeStore()
const router = useRouter()
const dark = computed(() => themeStore.dark)

const activeTab = ref('posts')
const bannerInput = ref(null)
const avatarInput = ref(null)

const userPosts = ref([])
const stats = ref({
  posts: 0,
  followers: 0,
  following: 0
})

const user = computed(() => userStore.user)

const bannerUrl = ref('')
const avatarUrl = ref('')

const API = 'https://localhost:8000'


onMounted(async () => {
  if (!user.value) return
  
  if (user.value.avatar_url && user.value.avatar_url !== '/def_user.png') {
    avatarUrl.value = user.value.avatar_url.startsWith('http')
    ? user.value.avatar_url
    : `${API}${user.value.avatar_url}`
  } else {
    avatarUrl.value = '/def_user.png'
  }
  
  if (user.value.banner_url && user.value.banner_url !== '' && user.value.banner_url !== 'null') {
    bannerUrl.value = user.value.banner_url.startsWith('http')
      ? user.value.banner_url
      : `${API}${user.value.banner_url}`
  } else {
    bannerUrl.value = ''
  }

  try {
    const data = await getUserStats(user.value.id)
    stats.value = {
      posts: data.post_count,
      followers: data.follower_count,
      following: data.following_count
    }
  } catch (e) {
    console.error('Erreur stats:', e)
  }

  try {
    userPosts.value = await getUserPosts(user.value.id)
  } catch (e) {
    console.error('Erreur posts:', e)
  }
})

async function onBannerChange(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const data = await uploadBanner(file)
    bannerUrl.value = `${API}${data.banner_url}`
    await userStore.fetchUser()
  } catch (err) {
    console.error('Erreur upload bannière:', err)
    bannerUrl.value = URL.createObjectURL(file)
  }
}

async function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const data = await uploadAvatar(file)
    avatarUrl.value = `${API}${data.avatar_url}`
    await userStore.fetchUser()
  } catch (err) {
    console.error('Erreur upload avatar:', err)
  }
}

function goToSettings() {
  router.push('/settings')
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50'" class="min-h-screen pb-16">

    <div
      class="relative w-full h-48 cursor-pointer overflow-hidden group"
      :class="bannerUrl ? '' : 'bg-gradient-to-br from-gray-800 via-gray-900 to-rose-950'"
      @click="bannerInput?.click()"
    >
      <img v-if="bannerUrl" :src="bannerUrl" alt="Banner" class="w-full h-full object-cover" />
      <div
        v-else
        class="flex flex-col items-center justify-center h-full text-white/30 group-hover:text-white/60 transition-colors gap-1 text-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        <span>Ajouter une bannière</span>
      </div>
      <input ref="bannerInput" type="file" accept="image/*" class="hidden" @change="onBannerChange" />
    </div>

    <div class="max-w-2xl mx-auto px-6">

      <div
        :class="dark ? 'border-gray-950' : 'border-rose-50'"
        class="relative w-28 h-28 -mt-14 rounded-full border-4 bg-gray-800 cursor-pointer overflow-hidden group/avatar"
        @click="avatarInput?.click()"
      >
        <img v-if="avatarUrl" :src="avatarUrl" alt="Avatar" class="w-full h-full object-cover" />
        <div v-else class="w-full h-full flex items-center justify-center text-white/40">
          <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/avatar:opacity-100 transition-opacity rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
      </div>

      <div class="flex items-center justify-between mt-4 gap-4 flex-wrap">
        <div>
          <h1 :class="dark ? 'text-white' : 'text-gray-900'" class="text-2xl font-bold">{{ user?.display_name || user?.username || 'Utilisateur' }}</h1>
          <p v-if="user?.display_name" class="text-sm text-gray-400">@{{ user?.username }}</p>
          <p :class="dark ? 'text-gray-400' : 'text-gray-400'" class="text-sm mt-0.5">{{ user?.bio || 'Aucune bio pour le moment.' }}</p>
        </div>
        <button
          @click="goToSettings"
          :class="dark ? 'border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white hover:border-gray-500' : 'border-rose-200 text-gray-800 hover:bg-gray-800 hover:text-rose-50 hover:border-gray-800'"
          class="flex items-center gap-1.5 px-4 py-2 rounded-full border text-sm font-medium transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          Paramètres
        </button>
      </div>

      <div :class="dark ? 'border-gray-700' : 'border-rose-200/60'" class="flex items-center gap-6 mt-5 py-4 border-b">
        <div class="text-center">
          <div :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-bold">{{ stats.posts }}</div>
          <div :class="dark ? 'text-gray-500' : 'text-rose-300'" class="text-xs uppercase tracking-wide">Posts</div>
        </div>
        <div class="text-center">
          <div :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-bold">{{ stats.followers }}</div>
          <div :class="dark ? 'text-gray-500' : 'text-rose-300'" class="text-xs uppercase tracking-wide">Followers</div>
        </div>
        <div class="text-center">
          <div :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-bold">{{ stats.following }}</div>
          <div :class="dark ? 'text-gray-500' : 'text-rose-300'" class="text-xs uppercase tracking-wide">Following</div>
        </div>
      </div>

      <div :class="dark ? 'border-gray-700' : 'border-rose-200/60'" class="flex border-b">
        <button
          v-for="tab in [
            { key: 'posts', label: 'Posts' },
            { key: 'likes', label: 'Likes' }
          ]"
          :key="tab.key"
          :class="[
            'flex-1 py-3 text-sm font-medium text-center transition-all border-b-2',
            activeTab === tab.key
              ? (dark ? 'text-white border-rose-400' : 'text-gray-900 border-rose-400')
              : (dark ? 'text-gray-500 border-transparent hover:text-gray-300' : 'text-rose-300 border-transparent hover:text-gray-600')
          ]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="py-4">
        <div v-if="activeTab === 'posts'" class="flex flex-col gap-3">
          <div v-if="userPosts.length === 0" :class="dark ? 'text-gray-500' : 'text-rose-300'" class="text-center py-12 text-sm">
            Aucun post pour le moment.
          </div>
          <div
            v-for="post in userPosts"
            :key="post.id"
            :class="dark ? 'bg-gray-900 border-gray-700 hover:shadow-gray-900/50' : 'bg-white border-rose-100 hover:shadow-rose-100/50'"
            class="rounded-xl border p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center gap-3 mb-3">
              <div class="w-9 h-9 rounded-full overflow-hidden bg-gray-800 flex-shrink-0">
                <img
                  :src="post.author?.avatar_url && post.author.avatar_url !== '/def_user.png' && post.author.avatar_url.startsWith('/') ? `${API}${post.author.avatar_url}` : (post.author?.avatar_url?.startsWith('http') ? post.author.avatar_url : '/def_user.png')"
                  alt=""
                  class="w-full h-full object-cover"
                />
              </div>
              <div>
                <span :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm">{{ post.author?.display_name || post.author?.username }}</span>
                <span :class="dark ? 'text-gray-500' : 'text-rose-300'" class="ml-2 text-xs">{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
            <p :class="dark ? 'text-gray-200' : 'text-gray-800'" class="text-sm leading-relaxed mb-3">{{ post.content }}</p>
            <div class="flex gap-5">
              <span :class="dark ? 'text-gray-500' : 'text-rose-300'" class="flex items-center gap-1.5 text-xs">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
                {{ post.like_count }}
              </span>
              <span :class="dark ? 'text-gray-500' : 'text-rose-300'" class="flex items-center gap-1.5 text-xs">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                {{ post.comment_count }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'likes'" :class="dark ? 'text-gray-500' : 'text-rose-300'" class="text-center py-12 text-sm">
          Posts likés à venir...
        </div>
      </div>
    </div>
  </div>
</template>