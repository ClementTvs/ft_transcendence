<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import { getUserStats, getUserPosts, uploadAvatar, uploadBanner, deletePost } from '../api'

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

const API = ''

// Menu options + confirmation
const openMenuPostId = ref(null)
const postToDelete = ref(null)
const deleting = ref(false)


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

  document.addEventListener('keydown', onEsc)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onEsc)
})

function onEsc(e) {
  if (e.key === 'Escape') {
    openMenuPostId.value = null
    postToDelete.value = null
  }
}

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

function goToPost(postId) {
  router.push(`/post/${postId}`)
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

function parsePost(post) {
  const match = post.content?.match(/^\[(.+?)\]\s*(.*)$/s)
  if (match) return { game: match[1], content: match[2] }
  return { game: null, content: post.content }
}

function postAuthorAvatar(post) {
  const a = post.author?.avatar_url
  if (!a || a === '/def_user.png') return '/def_user.png'
  if (a.startsWith('http')) return a
  if (a.startsWith('/')) return `${API}${a}`
  return a
}

function toggleMenu(e, postId) {
  e.stopPropagation()
  openMenuPostId.value = openMenuPostId.value === postId ? null : postId
}

function closeMenu() {
  openMenuPostId.value = null
}

function askDelete(e, post) {
  e.stopPropagation()
  postToDelete.value = post
  openMenuPostId.value = null
}

function cancelDelete() {
  if (deleting.value) return
  postToDelete.value = null
}

async function confirmDelete() {
  if (!postToDelete.value || deleting.value) return
  const post = postToDelete.value
  deleting.value = true

  // Optimistic update
  const prevPosts = userPosts.value
  const prevStats = { ...stats.value }
  userPosts.value = userPosts.value.filter(p => p.id !== post.id)
  stats.value.posts = Math.max(0, stats.value.posts - 1)

  try {
    await deletePost(post.id)
    postToDelete.value = null
  } catch (err) {
    console.error('Erreur suppression post:', err)
    // Revert
    userPosts.value = prevPosts
    stats.value = prevStats
    alert('Erreur lors de la suppression du post')
  } finally {
    deleting.value = false
  }
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
            @click="goToPost(post.id)"
            :class="dark ? 'bg-gray-900 border-gray-700 hover:shadow-gray-900/50' : 'bg-white border-rose-100 hover:shadow-rose-100/50'"
            class="relative rounded-xl border p-4 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div
              v-if="post.author_id === user?.id"
              class="absolute top-3 right-3 z-10"
              @click.stop
            >
              <button
                @click="toggleMenu($event, post.id)"
                :class="dark ? 'text-gray-500 hover:text-gray-300 hover:bg-gray-800' : 'text-gray-400 hover:text-gray-700 hover:bg-rose-50'"
                class="p-1.5 rounded-full transition-colors"
                aria-label="Options du post"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="5" cy="12" r="2"/>
                  <circle cx="12" cy="12" r="2"/>
                  <circle cx="19" cy="12" r="2"/>
                </svg>
              </button>

              <div
                v-if="openMenuPostId === post.id"
                :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-rose-100'"
                class="absolute right-0 top-full mt-1 w-44 rounded-xl border shadow-lg overflow-hidden z-20"
              >
                <button
                  @click="askDelete($event, post)"
                  :class="dark ? 'hover:bg-red-500/10' : 'hover:bg-red-50'"
                  class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500 transition-colors text-left"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/>
                    <path d="M10 11v6"/>
                    <path d="M14 11v6"/>
                    <path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>
                  </svg>
                  Supprimer
                </button>
              </div>
            </div>

            <div class="flex items-center gap-3 mb-3 pr-8">
              <div class="w-9 h-9 rounded-full overflow-hidden bg-gray-800 flex-shrink-0">
                <img :src="postAuthorAvatar(post)" alt="" class="w-full h-full object-cover" />
              </div>
              <div>
                <span :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm">{{ post.author?.display_name || post.author?.username }}</span>
                <span :class="dark ? 'text-gray-500' : 'text-rose-300'" class="ml-2 text-xs">{{ formatDate(post.created_at) }}</span>
              </div>
            </div>

            <span v-if="parsePost(post).game" :class="dark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'" class="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
              {{ parsePost(post).game }}
            </span>

            <p :class="dark ? 'text-gray-200' : 'text-gray-800'" class="text-sm leading-relaxed mb-3 whitespace-pre-wrap">{{ parsePost(post).content }}</p>

            <img
              v-if="post.image_url"
              :src="post.image_url.startsWith('http') ? post.image_url : `${API}${post.image_url}`"
              :class="dark ? 'border-gray-700' : 'border-rose-100'"
              class="mb-3 rounded-xl max-h-96 w-full object-cover border"
              loading="lazy"
            />

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
      </div>
    </div>

    <div
      v-if="openMenuPostId !== null"
      class="fixed inset-0 z-[5]"
      @click="closeMenu"
    />

    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="postToDelete"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          @click.self="cancelDelete"
        >
          <div
            :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'"
            class="w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden"
          >
            <div class="p-6">
              <div class="flex items-start gap-4">
                <div :class="dark ? 'bg-red-500/10' : 'bg-red-50'" class="flex-shrink-0 w-11 h-11 rounded-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-500">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 :class="dark ? 'text-white' : 'text-gray-900'" class="text-lg font-bold">Supprimer ce post ?</h3>
                  <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm mt-1.5 leading-relaxed">
                    Cette action est irréversible. Le post, son image et tous les commentaires associés seront définitivement supprimés.
                  </p>
                </div>
              </div>

              <!-- Aperçu du post -->
              <div
                :class="dark ? 'bg-gray-800 border-gray-700' : 'bg-rose-50/60 border-rose-100'"
                class="mt-4 p-3 rounded-xl border max-h-32 overflow-hidden"
              >
                <p :class="dark ? 'text-gray-300' : 'text-gray-700'" class="text-sm line-clamp-3">
                  {{ parsePost(postToDelete).content || '(aucun texte)' }}
                </p>
              </div>
            </div>

            <div :class="dark ? 'bg-gray-800/50 border-gray-700' : 'bg-rose-50/30 border-rose-100'" class="flex justify-end gap-2 px-6 py-4 border-t">
              <button
                @click="cancelDelete"
                :disabled="deleting"
                :class="dark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'"
                class="px-4 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                @click="confirmDelete"
                :disabled="deleting"
                class="px-5 py-2 rounded-full text-sm font-semibold text-white bg-red-500 hover:bg-red-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg v-if="deleting" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="animate-spin">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                {{ deleting ? 'Suppression...' : 'Supprimer' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>