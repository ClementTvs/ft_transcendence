<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPosts, likePost } from '../api'

const posts = ref([])
const selectedGame = ref(null)
const searchGame = ref('')
const searchFriend = ref('')

const games = ['League of Legends', 'Valorant', 'CS2', 'Minecraft', 'Fortnite', 'GTA V', 'Rocket League', 'Apex Legends']

const filteredGames = computed(() => {
  if (!searchGame.value) return games
  return games.filter(g =>
    g.toLowerCase().includes(searchGame.value.toLowerCase())
  )
})

const filteredPosts = computed(() => {
  if (!selectedGame.value) return posts.value
  return posts.value.filter(p => p.game === selectedGame.value)
})

async function handleLike(postId) {
  await likePost(postId)
  posts.value = await getPosts()
}

onMounted(async () => {
  posts.value = await getPosts()
})
</script>

<template>
  <div class="flex h-[calc(100vh-96px)]">

    <div class="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <input v-model="searchFriend" placeholder="Rechercher un ami..."
          class="w-full border border-gray-200 rounded-lg p-2 text-sm
                 focus:outline-none focus:border-rose-400" />
      </div>
      <div class="flex-1 overflow-y-auto">
        <div class="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer">
          <div class="relative">
            <img src="/def_user.png" class="h-10 w-10 rounded-full" />
            <div class="absolute bottom-0 right-0 h-3 w-3 bg-green-400 rounded-full border-2 border-white"></div>
          </div>
          <div>
            <p class="font-medium text-gray-800 text-sm">Ami 1</p>
            <p class="text-xs text-gray-400">En ligne</p>
          </div>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-100">
      <div>

        <div v-if="filteredPosts.length === 0" class="text-center text-gray-400 mt-12">
          Aucun post pour le moment.
        </div>

        <div v-for="post in filteredPosts" :key="post.id"
          class="bg-white border-b border-gray-700 p-4 flex gap-3 hover:bg-gray-50 cursor-pointer">
          <img :src="post.author?.avatar_url || '/def_user.png'"
            class="h-10 w-10 rounded-full" />
          <div class="flex-1 flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <p class="font-bold text-gray-900 text-sm">
                {{ post.author?.display_name || post.author?.username }}
              </p>
              <p class="text-sm text-gray-400">
                · {{ new Date(post.created_at).toLocaleDateString('fr-FR') }}
              </p>
              <span v-if="post.game"
                class="text-xs bg-rose-100 text-rose-500 rounded-full px-2 py-0.5">
                🎮 {{ post.game }}
              </span>
            </div>
            <p class="text-gray-800">{{ post.content }}</p>
            <div class="flex gap-6 text-sm text-gray-400 mt-1">
              <button @click="handleLike(post.id)"
                class="hover:text-rose-500 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
                </svg> {{ post.like_count }}
              </button>
              <button class="hover:text-blue-500 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.068.157 2.148.279 3.238.364.466.037.893.281 1.153.671L12 21l2.652-3.978c.26-.39.687-.634 1.153-.67 1.09-.086 2.17-.208 3.238-.365 1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                </svg>{{ post.comment_count }}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div class="w-72 bg-white border-l border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <input v-model="searchGame" placeholder="Rechercher un jeu..."
          class="w-full border border-gray-200 rounded-lg p-2 text-sm
                 focus:outline-none focus:border-rose-400" />
      </div>

      <div class="p-3">
        <button @click="selectedGame = null"
          :class="!selectedGame ? 'bg-rose-400 text-white' : 'text-gray-600 hover:bg-gray-100'"
          class="w-full text-left rounded-lg px-3 py-2 text-sm mb-1">
          Tous les posts
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-3">
        <button v-for="game in filteredGames" :key="game"
          @click="selectedGame = game"
          :class="selectedGame === game ? 'bg-rose-400 text-white' : 'text-gray-600 hover:bg-gray-100'"
          class="w-full text-left rounded-lg px-3 py-2 text-sm mb-1 flex items-center gap-2">
          🎮 {{ game }}
        </button>
      </div>
    </div>

  </div>
</template>