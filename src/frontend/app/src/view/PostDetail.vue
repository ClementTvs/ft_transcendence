<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { likePost, unlikePost, getComments, createComment } from '../api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const user = computed(() => userStore.user)
const dark = computed(() => themeStore.dark)
const API = 'https://localhost:8000'

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const commentText = ref('')
const commentsLoading = ref(false)

function avatarUrl(u) {
  if (!u?.avatar_url) return '/def_user.png'
  if (u.avatar_url === '/def_user.png') return '/def_user.png'
  if (u.avatar_url.startsWith('http')) return u.avatar_url
  if (u.avatar_url.startsWith('/')) return `${API}${u.avatar_url}`
  return u.avatar_url
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDateShort(dateStr) {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return "à l'instant"
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `${Math.floor(diff / 86400)}j`
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function parsePost(p) {
  if (!p) return { game: null, content: '' }
  const match = p.content?.match(/^\[(.+?)\]\s*(.*)$/s)
  if (match) return { game: match[1], content: match[2] }
  return { game: null, content: p.content }
}

function getHeaders() {
  const token = localStorage.getItem('token')
  return { 'Content-Type': 'application/json', ...(token && { 'Authorization': `Bearer ${token}` }) }
}

async function loadPost() {
  const postId = route.params.id
  try {
    const res = await fetch(`${API}/api/posts/${postId}`, { headers: getHeaders() })
    if (!res.ok) throw new Error('Post not found')
    post.value = await res.json()
  } catch (e) {
    console.error(e)
    post.value = null
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  if (!post.value) return
  commentsLoading.value = true
  try { comments.value = await getComments(post.value.id) }
  catch (e) { comments.value = [] }
  finally { commentsLoading.value = false }
}

async function handleLike() {
  if (!post.value) return
  try {
    if (post.value.is_liked) { await unlikePost(post.value.id); post.value.is_liked = false; post.value.like_count-- }
    else { await likePost(post.value.id); post.value.is_liked = true; post.value.like_count++ }
  } catch (e) { console.error(e) }
}

async function handleComment() {
  const text = commentText.value.trim()
  if (!text || !post.value) return
  try {
    await createComment(post.value.id, text)
    commentText.value = ''
    await loadComments()
    post.value.comment_count++
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  await loadPost()
  await loadComments()
})
</script>

<template>
  <div :class="dark ? 'bg-gray-950' : 'bg-rose-50/50'" class="min-h-[calc(100vh-64px)]">
    <div class="max-w-2xl mx-auto px-4 py-5">

      <!-- Back -->
      <button @click="router.back()" :class="dark ? 'text-gray-400 hover:text-white' : 'text-gray-400 hover:text-gray-700'" class="flex items-center gap-2 mb-5 text-sm font-medium transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Retour
      </button>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm">Chargement...</p>
      </div>

      <!-- Not found -->
      <div v-else-if="!post" class="text-center py-20">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-600' : 'text-gray-300'" class="mx-auto mb-3"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        <p :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm font-medium">Post introuvable</p>
      </div>

      <template v-else>
        <!-- Post -->
        <div :class="dark ? 'bg-gray-900 border-gray-700' : 'bg-white border-rose-100'" class="rounded-2xl border shadow-sm overflow-hidden">
          <div class="p-6">
            <!-- Author -->
            <div class="flex items-center gap-3 mb-4">
              <router-link :to="`/user/${post.author_id}`">
                <img :src="avatarUrl(post.author)" class="h-12 w-12 rounded-full object-cover" />
              </router-link>
              <div>
                <router-link :to="`/user/${post.author_id}`" :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-base hover:underline">{{ post.author?.display_name || post.author?.username }}</router-link>
                <p class="text-gray-400 text-sm">@{{ post.author?.username }}</p>
              </div>
            </div>

            <!-- Game tag -->
            <span v-if="parsePost(post).game" :class="dark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'" class="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m6-1h.01m4 0h.01"/></svg>
              {{ parsePost(post).game }}
            </span>

            <!-- Content -->
            <p :class="dark ? 'text-gray-100' : 'text-gray-900'" class="text-lg leading-relaxed whitespace-pre-wrap">{{ parsePost(post).content }}</p>

            <!-- Image -->
            <img v-if="post.image_url" :src="post.image_url.startsWith('http') ? post.image_url : `${API}${post.image_url}`" class="mt-4 rounded-xl w-full object-cover max-h-[500px]" />

            <!-- Date -->
            <p :class="dark ? 'text-gray-500' : 'text-gray-400'" class="text-sm mt-4 pt-4" :style="{ borderTop: dark ? '1px solid #374151' : '1px solid #ffe4e6' }">
              {{ formatDate(post.created_at) }}
            </p>

            <!-- Stats -->
            <div :class="dark ? 'border-gray-700' : 'border-rose-100'" class="flex items-center gap-6 mt-4 pt-4 border-t">
              <div class="flex items-center gap-1.5">
                <span :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-sm">{{ post.like_count }}</span>
                <span :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm">{{ post.like_count === 1 ? 'like' : 'likes' }}</span>
              </div>
              <div class="flex items-center gap-1.5">
                <span :class="dark ? 'text-white' : 'text-gray-900'" class="font-bold text-sm">{{ post.comment_count }}</span>
                <span :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm">{{ post.comment_count === 1 ? 'commentaire' : 'commentaires' }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div :class="dark ? 'border-gray-700' : 'border-rose-100'" class="flex items-center gap-4 mt-4 pt-4 border-t">
              <button @click="handleLike" class="group flex items-center gap-2 flex-1 justify-center py-2 rounded-xl transition-colors" :class="dark ? 'hover:bg-gray-800' : 'hover:bg-rose-50'">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" :fill="post.is_liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="post.is_liked ? 'text-rose-500' : (dark ? 'text-gray-400' : 'text-gray-500')" class="transition-colors"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                <span :class="post.is_liked ? 'text-rose-500 font-semibold' : (dark ? 'text-gray-400' : 'text-gray-500')" class="text-sm">{{ post.is_liked ? 'Aimé' : 'Aimer' }}</span>
              </button>
              <div :class="dark ? 'bg-gray-700' : 'bg-rose-100'" class="w-px h-6"></div>
              <label for="comment-input" class="group flex items-center gap-2 flex-1 justify-center py-2 rounded-xl cursor-pointer transition-colors" :class="dark ? 'hover:bg-gray-800' : 'hover:bg-sky-50'">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="dark ? 'text-gray-400' : 'text-gray-500'"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                <span :class="dark ? 'text-gray-400' : 'text-gray-500'" class="text-sm">Commenter</span>
              </label>
            </div>
          </div>

          <!-- Comment input -->
          <div :class="dark ? 'border-gray-700 bg-gray-800/50' : 'border-rose-100 bg-gray-50/50'" class="px-6 py-4 border-t">
            <div class="flex gap-3 items-start">
              <img :src="avatarUrl(user)" class="h-9 w-9 rounded-full object-cover flex-shrink-0 mt-0.5" />
              <div class="flex-1">
                <textarea
                  id="comment-input"
                  v-model="commentText"
                  @keydown.ctrl.enter="handleComment"
                  placeholder="Écrire un commentaire..."
                  rows="2"
                  :class="dark ? 'bg-gray-900 text-white placeholder-gray-500 border-gray-700 focus:border-gray-500' : 'bg-white text-gray-800 placeholder-gray-400 border-rose-100 focus:border-rose-300'"
                  class="w-full rounded-xl border px-4 py-2.5 text-sm resize-none focus:outline-none transition-colors"
                />
                <div class="flex justify-end mt-2">
                  <button @click="handleComment" :disabled="!commentText.trim()" :class="commentText.trim() ? 'bg-gray-900 text-white hover:bg-gray-800' : (dark ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-100 text-gray-300 cursor-not-allowed')" class="px-5 py-1.5 rounded-full text-sm font-medium transition-all">Publier</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Comments -->
          <div :class="dark ? 'border-gray-700' : 'border-rose-100'" class="border-t">
            <div v-if="commentsLoading" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-6 py-8 text-center text-sm">Chargement...</div>
            <div v-else-if="comments.length === 0" :class="dark ? 'text-gray-500' : 'text-gray-400'" class="px-6 py-8 text-center text-sm">Pas encore de commentaire</div>
            <div v-else>
              <div v-for="comment in comments" :key="comment.id" :class="dark ? 'border-gray-700/50 hover:bg-gray-800/30' : 'border-gray-100/50 hover:bg-gray-50/50'" class="px-6 py-4 flex gap-3 border-b last:border-0 transition-colors">
                <router-link :to="`/user/${comment.author?.id}`">
                  <img :src="avatarUrl(comment.author)" class="h-9 w-9 rounded-full object-cover flex-shrink-0 mt-0.5" />
                </router-link>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <router-link :to="`/user/${comment.author?.id}`" :class="dark ? 'text-white' : 'text-gray-900'" class="font-semibold text-sm hover:underline">{{ comment.author?.display_name || comment.author?.username }}</router-link>
                    <span class="text-gray-400 text-xs">@{{ comment.author?.username }}</span>
                    <span :class="dark ? 'text-gray-600' : 'text-gray-300'" class="text-xs">·</span>
                    <span class="text-gray-400 text-xs">{{ formatDateShort(comment.created_at) }}</span>
                  </div>
                  <p :class="dark ? 'text-gray-200' : 'text-gray-700'" class="text-sm leading-relaxed mt-1">{{ comment.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>