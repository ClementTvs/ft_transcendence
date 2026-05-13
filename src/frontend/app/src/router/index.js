import { createRouter, createWebHistory } from 'vue-router'
import Home from "../view/Home.vue"
import Profile from "../view/Profile.vue"
import UserProfile from "../view/UserProfile.vue"
import Chat from "../view/Chat.vue"
import Explore from "../view/Explore.vue"
import PostDetail from "../view/PostDetail.vue"
import Login from "../view/Login.vue"
import ForgotPassword from '../view/ForgotPassword.vue'
import ResetPassword from '../view/ResetPassword.vue'
import Register from '../view/Register.vue'
import { useUserStore } from '../stores/user'
import Settings from '../view/Settings.vue'
import Terms from '../view/TermOfService.vue'
import Privacy from '../view/PrivacyPolicy.vue'
import NotFound from '../view/404.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home, meta: { requiresAuth: true } },
    { path: '/profile', component: Profile, meta: { requiresAuth: true } },
    { path: '/user/:id(\\d+)', component: UserProfile, meta: { requiresAuth: true } },
    { path: '/chat/:userId?', component: Chat, meta: { requiresAuth: true } },
    { path: '/explore', component: Explore, meta: { requiresAuth: true } },
    { path: '/post/:id(\\d+)', component: PostDetail, meta: { requiresAuth: true } },
    { path: '/terms', component: Terms },
    { path: '/privacy', component: Privacy },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/settings', component: Settings, meta: { requiresAuth:true }},
    { path: '/forgot-password', component: ForgotPassword },
    { path: '/reset-password', component: ResetPassword },
    { path: '/:pathMatch(.*)*', component: NotFound},
  ],
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (token) {
    const userStore = useUserStore()
    if (!userStore.user) {
      await userStore.fetchUser()
    }
    next()
  } else {
    next()
  }
})

export default router