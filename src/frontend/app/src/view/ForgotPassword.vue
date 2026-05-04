<script setup>
import { ref, computed } from 'vue'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'

const themeStore = useThemeStore()
const router = useRouter()

const email = ref('')
const error = ref('')
const loading = ref(false)
const submitted = ref(false)
const focused = ref(false)

const themeClasses = computed(() => {
  if (themeStore.dark) {
    return {
      bg: 'bg-gray-950',
      sidebar: 'bg-gray-800 border-gray-700',
      header: 'bg-gray-900/80 border-gray-700',
      card: 'bg-gray-800 border-gray-700',
      label: 'text-gray-400',
    }
  } else {
    return {
      bg: 'bg-gray-50',
      sidebar: 'bg-rose-50 border-rose-200',
      header: 'bg-gray-50/80 border-gray-100',
      card: 'bg-rose-50 border-rose-100',
      label: 'text-gray-500',
    }
  }
})

function validate() {
  if (!email.value.trim()) {
    error.value = 'Veuillez saisir votre adresse e-mail.'
    return false
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    error.value = 'Adresse e-mail invalide.'
    return false
  }
  error.value = ''
  return true
}

async function handleSubmit() {
  if (!validate() || loading.value) return
  loading.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500))
  loading.value = false
  submitted.value = true
}

function reset() {
  submitted.value = false
  email.value = ''
  error.value = ''
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>

<template>
  <div :class="['min-h-screen flex items-center justify-center relative overflow-hidden transition-all duration-500', themeClasses.bg]">

    <!-- Background decorative blobs -->
    <div class="absolute inset-0 pointer-events-none">
      <div :class="['absolute -top-32 -left-32 w-96 h-96 rounded-full blur-3xl opacity-30 transition-all duration-500', themeStore.dark ? 'bg-rose-900' : 'bg-rose-200']" />
      <div :class="['absolute -bottom-32 -right-32 w-96 h-96 rounded-full blur-3xl opacity-20 transition-all duration-500', themeStore.dark ? 'bg-rose-800' : 'bg-rose-300']" />
      <div :class="['absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl opacity-10 transition-all duration-500', themeStore.dark ? 'bg-rose-700' : 'bg-rose-100']" />
    </div>

    <!-- Theme toggle -->
    <button
      @click="themeStore.toggle()"
      :class="['absolute top-6 right-6 w-10 h-10 rounded-full flex items-center justify-center border transition-all duration-300 hover:scale-110', themeClasses.card, 'border']"
    >
      <svg v-if="themeStore.dark" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    </button>

    <!-- Card -->
    <div
      :class="['relative w-full max-w-md mx-4 rounded-2xl border p-8 shadow-2xl backdrop-blur-sm transition-all duration-500', themeClasses.card, themeStore.dark ? 'shadow-rose-950/50' : 'shadow-rose-200/60']"
    >
      <!-- Logo / Icon -->
      <div class="flex justify-center mb-6">
        <div :class="['w-16 h-16 rounded-2xl flex items-center justify-center', themeStore.dark ? 'bg-rose-500/20 border border-rose-500/30' : 'bg-rose-100 border border-rose-200']">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
      </div>

      <!-- Heading -->
      <div class="text-center mb-8">
        <h1 :class="['text-2xl font-bold mb-2 tracking-tight', themeStore.dark ? 'text-white' : 'text-gray-900']">
          Mot de passe oublié ?
        </h1>
        <p :class="['text-sm leading-relaxed', themeClasses.label]">
          Saisissez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.
        </p>
      </div>

      <!-- Success state -->
      <Transition name="fade-slide">
        <div
          v-if="submitted"
          :class="['rounded-xl p-4 mb-6 flex items-start gap-3 border', themeStore.dark ? 'bg-rose-500/10 border-rose-500/30' : 'bg-rose-50 border-rose-200']"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p :class="['text-sm', themeStore.dark ? 'text-rose-300' : 'text-rose-700']">
            Un e-mail de réinitialisation a été envoyé à <strong>{{ email }}</strong>. Vérifiez votre boîte de réception.
          </p>
        </div>
      </Transition>

      <!-- Form -->
      <div v-if="!submitted" class="space-y-5">
        <div>
          <label :class="['block text-xs font-semibold uppercase tracking-widest mb-2', themeClasses.label]">
            Adresse e-mail
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" :class="['w-4 h-4 transition-colors duration-200', focused ? 'text-rose-500' : themeStore.dark ? 'text-gray-500' : 'text-gray-400']" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
              </svg>
            </span>
            <input
              v-model="email"
              type="email"
              placeholder="vous@exemple.com"
              @focus="focused = true"
              @blur="focused = false"
              @keyup.enter="handleSubmit"
              :class="[
                'w-full pl-10 pr-4 py-3 rounded-xl text-sm border outline-none transition-all duration-200',
                themeStore.dark
                  ? 'bg-gray-900 text-white placeholder-gray-600 border-gray-700 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
                  : 'bg-white text-gray-900 placeholder-gray-400 border-rose-200 focus:border-rose-400 focus:ring-2 focus:ring-rose-200/60',
                error ? (themeStore.dark ? 'border-red-500/70' : 'border-red-400') : ''
              ]"
            />
          </div>
          <Transition name="fade-slide">
            <p v-if="error" class="mt-1.5 text-xs text-red-400">{{ error }}</p>
          </Transition>
        </div>

        <!-- Submit button -->
        <button
          @click="handleSubmit"
          :disabled="loading"
          :class="[
            'w-full py-3 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 flex items-center justify-center gap-2',
            'bg-rose-500 hover:bg-rose-600 active:scale-[0.98] text-white shadow-lg shadow-rose-500/30',
            loading ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-rose-500/40'
          ]"
        >
          <svg v-if="loading" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span>{{ loading ? 'Envoi en cours…' : 'Envoyer le lien de réinitialisation' }}</span>
        </button>
      </div>

      <!-- Retry button after success -->
      <button
        v-if="submitted"
        @click="reset"
        :class="[
          'w-full py-3 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 border',
          themeStore.dark
            ? 'border-gray-700 text-gray-300 hover:bg-gray-700/50'
            : 'border-rose-200 text-rose-600 hover:bg-rose-50'
        ]"
      >
        Utiliser une autre adresse
      </button>

      <!-- Back to login -->
      <button @click="router.push('login')" div class="mt-6 text-center">
        <span
          :class="['text-sm inline-flex items-center gap-1.5 font-medium transition-colors duration-200', themeStore.dark ? 'text-gray-400 hover:text-rose-400' : 'text-gray-500 hover:text-rose-600']"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Retour à la connexion
        </span>
      </button>
    </div>
  </div>
</template>