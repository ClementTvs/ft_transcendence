<script setup>
import { ref } from 'vue'

const dark = ref(false);

function toggleDark() {
  dark.value = !dark.value;
}
</script>

<template>
  <nav :class="dark ? 'bg-rose-50' : 'bg-gray-800 text-white border-blue-300'" class="flex justify-between items-center h-24 px-4 border-b-4">
    <span>Logo</span>
    <div class="flex gap-12">
      <a>Accueil</a>
      <a>Post</a>
      <a>Profil</a>
    </div>
    <button @click="toggleDark">
      <div :class="dark ? 'bg-rose-200' : 'bg-gray-600'" class="rounded-full p-2">
        <img
          :src="dark ? '/sun.svg' : '/moon.svg'"
          class="h-6 w-6"
        />
      </div>
    </button>
  </nav>
  <h1>You did it!</h1>
  <p>
    Visit <a href="https://vuejs.org/" target="_blank" rel="noopener">vuejs.org</a> to read the
    documentation
  </p>
</template>

<style scoped></style>
