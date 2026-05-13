<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { resetPassword } from '../api'

const router = useRouter()
const route = useRoute()

const token = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)
const success = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    error.value = 'Lien de réinitialisation invalide ou expiré.'
  }
})

function validate() {
  error.value = ''
  if (!password.value) return (error.value = 'Veuillez saisir un nouveau mot de passe.'), false
  if (password.value.length < 6) return (error.value = 'Le mot de passe doit contenir au moins 6 caractères.'), false
  if (password.value.length > 72) return (error.value = 'Le mot de passe doit contenir au maximum 72 caractères.'), false
  if (password.value !== confirm.value) return (error.value = 'Les mots de passe ne correspondent pas.'), false
  return true
}

async function handleSubmit() {
  if (!validate() || loading.value) return
  loading.value = true
  try {
    await resetPassword(token.value, password.value)
    success.value = true
  } catch (err) {
    error.value = err.message || 'Lien invalide ou expiré. Veuillez recommencer.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active { transition: all 0.25s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(-6px); }
.fade-slide-leave-to  { opacity: 0; transform: translateY(-6px); }
</style>

<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-gray-50">

    <!-- Background blobs -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full blur-3xl opacity-30 bg-rose-200" />
      <div class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full blur-3xl opacity-20 bg-rose-300" />
    </div>

    <!-- Card -->
    <div class="relative w-full max-w-md mx-4 rounded-2xl border p-8 shadow-2xl backdrop-blur-sm bg-rose-50 border-rose-100 shadow-rose-200/60">

      <!-- Icon -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center bg-rose-100 border border-rose-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
      </div>

      <!-- Heading -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold mb-2 tracking-tight text-gray-900">
          Nouveau mot de passe
        </h1>
        <p class="text-sm leading-relaxed text-gray-500">
          Choisissez un nouveau mot de passe sécurisé pour votre compte.
        </p>
      </div>

      <!-- Success state -->
      <Transition name="fade-slide">
        <div v-if="success" class="rounded-xl p-4 mb-6 flex flex-col items-center gap-3 border bg-rose-50 border-rose-200 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-rose-700 font-medium">Mot de passe mis à jour avec succès !</p>
          <button
            @click="router.push('/login')"
            class="mt-2 px-5 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-sm font-semibold shadow shadow-rose-300 transition-all">
            Se connecter
          </button>
        </div>
      </Transition>

      <!-- Form -->
      <div v-if="!success" class="space-y-5">

        <!-- No token warning -->
        <Transition name="fade-slide">
          <p v-if="!token && error" class="text-sm text-center text-red-500 bg-red-50 border border-red-200 rounded-xl p-3">
            {{ error }}
          </p>
        </Transition>

        <template v-if="token">
          <!-- New password -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-widest mb-2 text-gray-500">
              Nouveau mot de passe
            </label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                @keyup.enter="handleSubmit"
                :class="[
                  'w-full px-4 pr-10 py-3 rounded-xl text-sm border outline-none transition-all duration-200',
                  'bg-white text-gray-900 placeholder-gray-400 focus:ring-2',
                  error
                    ? 'border-red-400 focus:border-red-400 focus:ring-red-200/60'
                    : 'border-rose-200 focus:border-rose-400 focus:ring-rose-200/60'
                ]"
              />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-rose-500 transition-colors">
                <svg v-if="showPassword" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 01-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Confirm password -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-widest mb-2 text-gray-500">
              Confirmer le mot de passe
            </label>
            <div class="relative">
              <input
                v-model="confirm"
                :type="showConfirm ? 'text' : 'password'"
                placeholder="••••••••"
                @keyup.enter="handleSubmit"
                :class="[
                  'w-full px-4 pr-10 py-3 rounded-xl text-sm border outline-none transition-all duration-200',
                  'bg-white text-gray-900 placeholder-gray-400 focus:ring-2',
                  error
                    ? 'border-red-400 focus:border-red-400 focus:ring-red-200/60'
                    : 'border-rose-200 focus:border-rose-400 focus:ring-rose-200/60'
                ]"
              />
              <button type="button" @click="showConfirm = !showConfirm"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-rose-500 transition-colors">
                <svg v-if="showConfirm" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 01-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error -->
          <Transition name="fade-slide">
            <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
          </Transition>

          <!-- Submit -->
          <button
            @click="handleSubmit"
            :disabled="loading"
            :class="[
              'w-full py-3 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 flex items-center justify-center gap-2',
              'bg-rose-500 hover:bg-rose-600 active:scale-[0.98] text-white shadow-lg shadow-rose-500/30',
              loading ? 'opacity-70 cursor-not-allowed' : ''
            ]"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>{{ loading ? 'Enregistrement…' : 'Réinitialiser le mot de passe' }}</span>
          </button>
        </template>
      </div>

      <!-- Back to login -->
      <button @click="router.push('/login')" class="mt-6 w-full text-center">
        <span class="text-sm inline-flex items-center gap-1.5 font-medium transition-colors duration-200 text-gray-500 hover:text-rose-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Retour à la connexion
        </span>
      </button>

    </div>
  </div>
</template>
