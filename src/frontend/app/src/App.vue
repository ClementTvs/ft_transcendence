<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user';
import { getProfile } from './api';

const dark = ref(false);
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

function toggleDark() {
  dark.value = !dark.value;
}

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await userStore.fetchUser()
    } catch {
      localStorage.removeItem('token')
      router.push('/login')
    }
  }
})
</script>

<template>
  <nav v-if="!['/login', '/register', '/forgot-password'].includes(route.path)" :class="dark ? 'bg-gray-800 text-white border-blue-300' : 'bg-rose-50 border-gray-800'" class="flex justify-between items-center h-24 px-4 border-b-4">
    <router-link to="/profile">
      <div class="rounded-full p-2 bg-black">
        <img src="/def_user.png" class="h-8 w-8"/>
      </div>
    </router-link>
    <div class="flex gap-12">
      <router-link to="/">
        <p>Accueil</p>
      </router-link>
      <router-link to="/post">
        <p>Post</p>
      </router-link>
      <router-link to="/game">
        <p>Game</p>
      </router-link>
    </div>
    <button @click="toggleDark">
      <div :class="dark ? 'bg-gray-600' : 'bg-rose-200'" class="rounded-full p-2">
        <img
          :src="dark ? '/sun.svg' : '/moon.svg'"
          class="h-8 w-8"
        />
      </div>
    </button>
  </nav>
  <router-view />
</template>

<style scoped></style>
