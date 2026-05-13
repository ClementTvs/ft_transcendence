<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { forgotPassword } from '../api'

const router = useRouter()

const email = ref('')
const error = ref('')
const loading = ref(false)
const submitted = ref(false)
const focused = ref(false)

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

async function handleSubmit()
{ 
  if (!validate() || loading.value) return
  loading.value = true 
  try { 
  const data = await forgotPassword(email.value) 
  } 
  catch (err) { 
  console.error(err) 
  }
  finally {
  await new Promise(r => setTimeout(r, 1500))
  loading.value = false
  submitted.value = true
  }
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
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-gray-50">

    <!-- Background decorative blobs -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full blur-3xl opacity-30 bg-rose-200" />
      <div class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full blur-3xl opacity-20 bg-rose-300" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl opacity-10 bg-rose-100" />
    </div>

    <!-- Card -->
    <div class="relative w-full max-w-md mx-4 rounded-2xl border p-8 shadow-2xl backdrop-blur-sm bg-rose-50 border-rose-100 shadow-rose-200/60">

      <!-- Logo / Icon -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center bg-rose-100 border border-rose-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
      </div>

      <!-- Heading -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold mb-2 tracking-tight text-gray-900">
          Mot de passe oublié ?
        </h1>
        <p class="text-sm leading-relaxed text-gray-500">
          Saisissez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.
        </p>
      </div>

      <!-- Success state -->
      <Transition name="fade-slide">
        <div
          v-if="submitted"
          class="rounded-xl p-4 mb-6 flex items-start gap-3 border bg-rose-50 border-rose-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-rose-700">
            Si votre adresse e-mail est lié a un compte Transcendence, un e-mail de réinitialisation a été envoyé à <strong>{{ email }}</strong>. Vérifiez votre boîte de réception.
          </p>
        </div>
      </Transition>

      <!-- Form -->
      <div v-if="!submitted" class="space-y-5">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-widest mb-2 text-gray-500">
            Adresse e-mail
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" :class="['w-4 h-4 transition-colors duration-200', focused ? 'text-rose-500' : 'text-gray-400']" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                'bg-white text-gray-900 placeholder-gray-400 focus:ring-2',
                error
                  ? 'border-red-400 focus:border-red-400 focus:ring-red-200/60'
                  : 'border-rose-200 focus:border-rose-400 focus:ring-rose-200/60'
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
        class="w-full py-3 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 border border-rose-200 text-rose-600 hover:bg-rose-100"
      >
        Utiliser une autre adresse
      </button>

      <!-- Back to login -->
      <button @click="router.push('login')" class="mt-6 w-full text-center">
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