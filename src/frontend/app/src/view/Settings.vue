<script setup>
import { ref, computed, reactive } from 'vue'
import { uploadAvatar, uploadBanner, changePassword, deleteAccount, updateProfile } from '../api'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'

const activeSection = ref('profile')
const saved = ref(false)
const twofa = ref(false)
const showConfirmDelete = ref(false)
const deleting = ref(false)
const selectedTheme = ref('rose')
const avatarInput = ref(null)
const bannerInput = ref(null)
const pass1 = ref(null)
const pass2 = ref(null)
const currentPass = ref(null)
const showPass = reactive({ current: false, pass1: false, pass2: false })
const passErrors = reactive({ current: '', pass1: '', pass2: '' })
const userStore = useUserStore()
const themeStore = useThemeStore()
const language = ref('fr')
const API = ''

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

const isDark = computed(() => themeStore.dark)

async function onBannerChange(e) {
  const file = e.target.files[0]
  if (!file) return
  form.banner_file = file
  form.banner_url = URL.createObjectURL(file)
}

async function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  form.avatar_file = file
  form.avatar_url = URL.createObjectURL(file)
}

function avatarUrl() {
  if (!form?.avatar_url) return '/def_user.png'
  if (form.avatar_url === '/def_user.png') return '/def_user.png'
  if (form.avatar_url.startsWith('http')) return form.avatar_url
  if (form.avatar_url.startsWith('/')) return `${API}${form.avatar_url}`
  return form.avatar_url
}

function bannerUrl() {
  if (!form.banner_url) return null
  if (form.banner_url.startsWith('http')) return form.banner_url
  if (form.banner_url.startsWith('/')) return `${API}${form.banner_url}`
  return form.banner_url
}

async function handleSave() {
  try {
    const changed = await save()
    if (changed) {
      saved.value = true
      setTimeout(() => { saved.value = false }, 2500)
    }
  } catch (err) {
    console.error(err)
  }
}

async function save() {
  let changed = false

  // Save profile fields (username, display_name, email, bio)
  const profilePayload = {}
  if (form.username !== userStore.user.username) profilePayload.username = form.username
  if (form.display_name !== userStore.user.display_name) profilePayload.display_name = form.display_name
  if (form.email !== userStore.user.email) profilePayload.email = form.email
  if ((form.bio ?? '') !== (userStore.user.bio ?? '')) profilePayload.bio = form.bio

  if (Object.keys(profilePayload).length > 0) {
    try {
      await updateProfile(profilePayload)
      await userStore.fetchUser()
      changed = true
    } catch (err) {
      console.error('Error updating profile:', err)
    }
  }

  if (form.avatar_file && form.avatar_url !== userStore.user.avatar_url) {
    try {
      const data = await uploadAvatar(form.avatar_file)
      form.avatar_url = `${API}${data.avatar_url}`
      form.avatar_file = null
      await userStore.fetchUser()
      changed = true
    } catch (err) {
      console.error('Error upload avatar:', err)
    }
  }

  if (form.banner_file && form.banner_url !== userStore.user.banner_url) {
    try {
      const data = await uploadBanner(form.banner_file)
      form.banner_url = `${API}${data.banner_url}`
      form.banner_file = null
      await userStore.fetchUser()
      changed = true
    } catch (err) {
      console.error('Error upload banner:', err)
    }
  }

  if (pass1.value || pass2.value || currentPass.value) {
    passErrors.current = ''
    passErrors.pass1 = ''
    passErrors.pass2 = ''

    if (!currentPass.value) {
      passErrors.current = 'Veuillez entrer votre mot de passe actuel'
      return false
    }
    if (pass1.value?.length < 6) {
      passErrors.pass1 = 'Le mot de passe doit contenir au moins 6 caractères'
      return false
    }
    if (pass1.value?.length > 72) {
      passErrors.pass1 = 'Le mot de passe doit contenir au maximum 72 caractères'
      return false
    }
    if (pass1.value !== pass2.value) {
      passErrors.pass2 = 'Les mots de passe ne correspondent pas'
      return false
    }

    try {
      await changePassword(currentPass.value, pass1.value)
      currentPass.value = ''
      pass1.value = ''
      pass2.value = ''
      changed = true
    } catch (err) {
      passErrors.current = 'Mot de passe actuel incorrect'
      console.error('Error changing password:', err)
      return false
    }
  }

  return changed
}

async function onDeleteAccount() {
  try {
    deleting.value = true
    await deleteAccount()
    userStore.logout()
  } catch (err) {
    console.error('Delete failed:', err)
  } finally {
    deleting.value = false
  }
}

const editing = reactive({
  username: false,
  display_name: false,
  email: false,
  bio: false,
})

const form = reactive({
  avatar_url: userStore.user.avatar_url,
  banner_url: userStore.user.banner_url,
  avatar_file: null,
  banner_file: null,
  username: userStore.user.username,
  display_name: userStore.user.display_name,
  email: userStore.user.email,
  bio: userStore.user.bio,
})

const navItems = {
  account: [
    {
      id: 'profile', label: 'Profil',
      icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/></svg>`
    },
    {
      id: 'security', label: 'Sécurité',
      icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/></svg>`
    },
  ],
  preferences: [
    {
      id: 'appearance', label: 'Apparence',
      icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42"/></svg>`
    },
    {
      id: 'danger', label: 'Suppression',
      icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/></svg>`
    },
  ]
}

const sections = {
  profile: { title: 'Mon profil', description: 'Gérez vos informations personnelles' },
  security: { title: 'Sécurité', description: 'Mot de passe et authentification' },
  appearance: { title: 'Apparence', description: 'Thème, langue et affichage' },
  danger: { title: 'Supprimer le compte', description: 'Actions irréversibles' },
}

const currentSection = computed(() => sections[activeSection.value])

const themes = [
  { id: 'rose',  label: 'Rose',  desc: 'Accent rosé', preview: 'bg-gradient-to-br from-rose-50 to-rose-100 border border-rose-200' },
  { id: 'dark',  label: 'Sombre', desc: 'Mode nuit', preview: 'bg-gradient-to-br from-gray-700 to-gray-900' },
]
</script>

<template>
  <div :class="['min-h-screen font-[\'Instrument_Sans\',sans-serif] transition-colors duration-300', themeClasses.bg]">

    <!-- Sidebar -->
    <aside :class="['fixed top-0 left-0 h-screen w-64 border-r flex flex-col z-10 transition-colors duration-300', themeClasses.sidebar]">

      <!-- Logo -->
      <div :class="['px-6 py-4 h-[90px] border-b', isDark ? 'border-gray-700' : 'border-rose-200']"> <!--bar haut param -->
        <div class="flex items-center gap-3">
          <div :class="['w-8 h-8 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-sm', isDark ? 'bg-gradient-to-br from-gray-600 to-gray-900 shadow-gray-500' : 'bg-gradient-to-br from-rose-400 to-rose-600 shadow-rose-200']">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
            </svg>
          </div>
          <span :class="['font-semibold tracking-tight', isDark ? 'text-gray-100' : 'text-gray-800']">Paramètres</span>
        </div>
          <!-- Bouton return profil -->
        <button
          @click="$router.push('/profile')"
          :class="['mt-3 flex items-center gap-2 text-xs font-medium transition-colors', isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-rose-500']">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"/>
          </svg>
          Retour au profil
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p :class="['px-3 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-widest', isDark ? 'text-gray-500' : 'text-gray-400']">Compte</p>
        <button
          v-for="item in navItems.account" :key="item.id"
          @click="activeSection = item.id"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150',
              activeSection === item.id
              ? (isDark 
                  ? 'bg-gray-700 text-gray-300 font-medium'
                  : 'bg-rose-100 text-rose-600 font-medium'
                )
              : (isDark 
                  ? 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                  : 'text-gray-500 hover:bg-rose-100 hover:text-gray-700'
                )
          ]">
          <span
            :class="activeSection === item.id
              ? (isDark ? 'text-gray-300' : 'text-rose-500')
              : (isDark ? 'text-gray-400' : 'text-gray-400')"
            v-html="item.icon">
          </span>          {{ item.label }}
        </button>

        <p :class="['px-3 pt-4 pb-1 text-[10px] font-semibold uppercase tracking-widest', isDark ? 'text-gray-500' : 'text-gray-400']">Préférences</p>
        <button
          v-for="item in navItems.preferences" :key="item.id"
          @click="activeSection = item.id"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150',
            activeSection === item.id
              ? (isDark
                  ? 'bg-gray-700 text-gray-300 font-medium'
                  : 'bg-rose-100 text-rose-600 font-medium'
                )
              : (isDark 
                  ? 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                  : 'text-gray-500 hover:bg-rose-100 hover:text-gray-700'
                )
          ]">
          <span
            :class="activeSection === item.id
              ? (isDark ? 'text-gray-300' : 'text-rose-500')
              : (isDark ? 'text-gray-400' : 'text-gray-400')"
            v-html="item.icon">
          </span>
          {{ item.label }}
        </button>
      </nav>

      <!-- User -->
      <div :class="['px-4 py-4 border-t', isDark ? 'border-gray-700' : 'border-rose-200']">
        <div class="flex items-center gap-3">
          <img v-if="form.avatar_url" :src="avatarUrl()" class="w-9 h-9 rounded-full"/>
          <div class="flex-1 min-w-0">
            <p :class="['text-sm font-medium truncate', isDark ? 'text-gray-100' : 'text-gray-800']">{{ form.username }}</p>
            <p class="text-xs text-gray-400 truncate">{{ form.email }}</p>
          </div>
          <button @click="userStore.logout()" :class="['text-gray-400', isDark ? 'hover:text-gray-300 transition-colors' : 'hover:text-rose-400 transition-colors']">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="ml-64 min-h-screen">

      <!-- Header -->
      <div :class="['sticky top-0 backdrop-blur-sm border-b px-8 py-2 h-[90px] z-10 transition-colors duration-300', isDark ? 'border-gray-700' : 'border-rose-200']"> <!-- bar haut droite-->
        <div class="flex items-center justify-between h-full">
          <div>
            <h1 :class="['text-lg font-semibold', isDark ? 'text-gray-100' : 'text-gray-900']">{{ currentSection.title }}</h1>
            <p class="text-sm text-gray-400 mt-0.5">{{ currentSection.description }}</p>
          </div>
          <button
            @click="handleSave"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200',
              saved
                ? (isDark
                    ? 'bg-green-900/30 text-green-400 border border-green-700'
                    : 'bg-green-50 text-green-600 border border-green-200'
                  )
                : (isDark
                    ? 'bg-gray-500 hover:bg-gray-600 text-white shadow-sm shadow-black/30'
                    : 'bg-rose-400 hover:bg-rose-500 text-white shadow-sm shadow-rose-200 hover:shadow-rose-300'
                  )
            ]">
            <svg v-if="saved" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"/>
            </svg>
            {{ saved ? 'Sauvegardé !' : 'Sauvegarder' }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="px-8 py-8 max-w-2xl">

        <!-- PROFILE SECTION -->
        <template v-if="activeSection === 'profile'">
          <div :class="['rounded-2xl border mb-5 shadow-sm overflow-hidden transition-colors duration-300', themeClasses.card]">

            <!-- Banner -->
            <div
              class="relative w-full h-36 cursor-pointer overflow-hidden group"
              :class="form.banner_url ? '' : 'bg-gradient-to-br from-gray-800 via-gray-900 to-rose-950'"
              @click="bannerInput?.click()">
              <img v-if="form.banner_url" :src="bannerUrl()" class="w-full h-full object-cover"/>
              <div v-else class="flex flex-col items-center justify-center h-full text-white/30 group-hover:text-white/60 transition-colors gap-1 text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                <span>Ajouter une bannière</span>
              </div>
              <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"/>
              <input ref="bannerInput" type="file" accept="image/*" class="hidden" @change="onBannerChange"/>
            </div>

            <!-- Avatar -->
            <div class="px-6">
              <div
                class="relative w-20 h-20 -mt-10 rounded-full border-4 bg-gray-800 cursor-pointer overflow-hidden group/avatar shadow-sm z-10"
                @click="avatarInput?.click()">
                <img v-if="form.avatar_url" :src="avatarUrl()" alt="Avatar" class="w-full h-full object-cover"/>
                <div v-else class="w-full h-full flex items-center justify-center text-white/40">
                  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/avatar:opacity-100 transition-opacity rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                </div>
                <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange"/>
              </div>
            </div>

            <!-- Form fields -->
            <div class="px-6 pt-3 pb-6 space-y-5">
              <h2 :class="['text-sm font-semibold', isDark ? 'text-gray-200' : 'text-gray-700']">Informations personnelles</h2>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Pseudo</label>
                  <div class="relative">
                    <input v-model="form.username" :disabled="!editing.username" type="text"
                      :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                        editing.username ?
                          (isDark
                              ? 'border-gray-400 bg-gray-600 text-gray-200'
                              : 'border-rose-300 bg-white text-gray-800'
                            )
                          : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                            )
                      ]"
                      placeholder="Claire"/>
                    <button @click="editing.username = !editing.username"
                      :class="['absolute right-3 top-1/2 -translate-y-1/2 transition-colors', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <div>
                  <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Nom d'utilisateur</label>
                  <div class="relative">
                    <input v-model="form.display_name" :disabled="!editing.display_name" type="text"
                      :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                        editing.display_name ?                           
                          (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"
                      placeholder="Martin"/>
                    <button @click="editing.display_name = !editing.display_name"
                      :class="['absolute right-3 top-1/2 -translate-y-1/2 ', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Email</label>
                <div class="relative">
                  <input v-model="form.email" :disabled="!editing.email" type="email"
                    :class="['w-full px-3.5 py-2.5 pl-10 pr-10 rounded-xl border text-sm focus:outline-none', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                      editing.email ?                           
                        (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"/>
                  <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300 pointer-events-none" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"/>
                  </svg>
                  <button @click="editing.email = !editing.email"
                      :class="['absolute right-3 top-1/2 -translate-y-1/2 ', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z"/>
                    </svg>
                  </button>
                </div>
              </div>

              <div>
                <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Bio</label>
                <div class="relative">
                  <textarea v-model="form.bio" :disabled="!editing.bio" rows="3"
                    :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                      editing.bio ?                         
                        (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"
                    placeholder="Décrivez-vous en quelques mots..."></textarea>
                  <button @click="editing.bio = !editing.bio"
                    :class="['absolute right-3 top-3', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z"/>
                    </svg>
                  </button>
                </div>
                <p class="text-right text-xs text-gray-300 mt-1">{{ form.bio?.length ?? 0 }}/160</p>
              </div>
            </div>
          </div>
        </template>

        <!-- SECURITY SECTION -->
        <template v-if="activeSection === 'security'">
          <div :class="['rounded-2xl border p-6 mb-5 shadow-sm space-y-5 transition-colors duration-300', themeClasses.card]">
            <h2 :class="['text-sm font-semibold', isDark ? 'text-gray-200' : 'text-gray-700']">Changer le mot de passe</h2>

            <!-- Mot de passe actuel -->
            <div>
              <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Mot de passe actuel</label>
              <div class="relative">
                <input v-model="currentPass" :type="showPass.current ? 'text' : 'password'"
                  :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                    passErrors.current ? 
                      (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"
                  placeholder="••••••••"/>
                <button type="button" @click="showPass.current = !showPass.current"
                  :class="['absolute right-3 top-1/2 -translate-y-1/2 ', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                  <svg v-if="showPass.current" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"/>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                  </svg>
                </button>
              </div>
              <p v-if="passErrors.current" class="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/></svg>
                {{ passErrors.current }}
              </p>
            </div>

            <!-- Nouveau mot de passe -->
            <div>
              <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Nouveau mot de passe</label>
              <div class="relative">
                <input v-model="pass1" :type="showPass.pass1 ? 'text' : 'password'"
                  :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                    passErrors.pass1 ?                       
                      (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"
                  placeholder="••••••••"/>
                <button type="button" @click="showPass.pass1 = !showPass.pass1"
                  :class="['absolute right-3 top-1/2 -translate-y-1/2 ', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                  <svg v-if="showPass.pass1" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"/>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                  </svg>
                </button>
              </div>
              <p v-if="passErrors.pass1" class="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/></svg>
                {{ passErrors.pass1 }}
              </p>
            </div>

            <!-- Confirmer -->
            <div>
              <label :class="['block text-xs font-medium mb-1.5', themeClasses.label]">Confirmer</label>
              <div class="relative">
                <input v-model="pass2" :type="showPass.pass2 ? 'text' : 'password'"
                  :class="['w-full px-3.5 py-2.5 pr-10 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all', isDark ? 'focus:border-gray-500 focus:ring-2 focus:ring-gray-400 transition-all placeholder-gray-500' : 'focus:border-rose-500 focus:ring-2 focus:ring-rose-300 transition-all placeholder-gray-300',
                    passErrors.pass2 ?                       
                      (isDark
                                ? 'border-gray-400 bg-gray-600 text-gray-200'
                                : 'border-rose-300 bg-white text-gray-800'
                              )
                            : (isDark
                              ? 'border-gray-600 bg-gray-700 text-gray-200'
                              : 'border-gray-200 bg-gray-50 text-gray-800'
                              )
                      ]"
                  placeholder="••••••••"/>
                <button type="button" @click="showPass.pass2 = !showPass.pass2"
                  :class="['absolute right-3 top-1/2 -translate-y-1/2 ', isDark ? 'text-gray-400 hover:text-gray-500' : 'text-gray-300 hover:text-rose-400 ']">
                  <svg v-if="showPass.pass2" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"/>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                  </svg>
                </button>
              </div>
              <p v-if="passErrors.pass2" class="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/></svg>
                {{ passErrors.pass2 }}
              </p>
            </div>
          </div>
        </template> 

        <!-- APPEARANCE SECTION -->
        <template v-if="activeSection === 'appearance'">
          <div :class="['rounded-2xl border p-6 mb-5 shadow-sm transition-colors duration-300', themeClasses.card]">
            <h2 :class="['text-sm font-semibold mb-5', isDark ? 'text-gray-200' : 'text-gray-700']">Thème</h2>
            <div class="grid grid-cols-3 gap-3">
            <button
              v-for="theme in themes"
              :key="theme.id"
              @click="theme.id === 'dark' ? themeStore.dark = true : themeStore.dark = false"
              :class="[
                'p-3 rounded-xl border-2 transition-all text-left',
                (theme.id === 'dark' && themeStore.dark) || (theme.id === 'light' && !themeStore.dark)
                  ? (isDark
                      ? 'border-gray-500 bg-gray-500'
                      : 'border-rose-400 bg-gray-50')
                  : (isDark
                      ? 'border-gray-600 hover:border-gray-500'
                      : 'border-gray-100 hover:border-gray-50 bg-gray-50')
              ]"
            >
              <div :class="['w-full h-12 rounded-lg mb-2', theme.preview]"></div>

              <p :class="['text-xs font-medium', isDark ? 'text-gray-200' : 'text-gray-700']">
                {{ theme.label }}
              </p>

              <p class="text-[10px] text-gray-400">
                {{ theme.desc }}
              </p>
            </button>
            </div>
          </div>
        </template> 

        <!-- DANGER ZONE -->
        <template v-if="activeSection === 'danger'">
          <div :class="['rounded-2xl border p-6 shadow-sm transition-colors duration-300', isDark ? 'border-gray-500': 'border-red-100','', themeClasses.card]">
            <div class="flex items-start gap-3 mb-4">
              <div class="w-9 h-9 rounded-xl bg-gray-50 flex items-center justify-center flex-shrink-0">
                <svg :class="['w-4 h-4', isDark ? 'text-red-600' : 'text-red-400']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/>
                </svg>
              </div>
              <div>
                <h2 class="text-sm font-semibold text-red-600">Supprimer le compte</h2>
                <p class="text-xs text-gray-400 mt-0.5">Cette action est permanente et irréversible.</p>
              </div>
            </div>
            <button  @click="showConfirmDelete = true" class="text-sm px-4 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl font-medium transition-colors shadow-sm">
              Supprimer mon compte
            </button>
            <div v-if="showConfirmDelete" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div :class="['rounded-2xl p-6 w-[400px] shadow-xl', isDark ? 'bg-gray-800' : 'bg-white']">
                <h2 :class="['text-lg font-semibold', isDark ? 'text-gray-300' : 'text-gray-800']">
                  Êtes-vous sûr ?
                </h2>
                <p :class="['text-sm mt-2', isDark ? 'text-gray-200' : 'text-gray-500' ]">
                  Cette action est irréversible. Votre compte sera désactivé.
                </p>
                <div class="flex justify-end gap-3 mt-6">
                  <button
                    @click="showConfirmDelete = false"
                    class="px-4 py-2 text-sm rounded-xl bg-gray-100 hover:bg-gray-200">
                    Annuler
                  </button>
                  <button
                    @click="onDeleteAccount"
                    :disabled="deleting"
                    class="px-4 py-2 text-sm rounded-xl bg-red-500 hover:bg-red-600 text-white">
                    {{ deleting ? 'Suppression...' : 'Oui, supprimer' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>

      </div>
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');
</style>