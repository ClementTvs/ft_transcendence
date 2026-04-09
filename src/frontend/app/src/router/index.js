import { createRouter, createWebHistory } from 'vue-router'
import Home from "../view/Home.vue"
import Profile from "../view/Profile.vue"
import UserProfile from "../view/UserProfile.vue"
import Chat from "../view/Chat.vue"
import Post from "../view/Post.vue"
import Login from "../view/Login.vue"
import ForgotPassword from '../view/ForgotPassword.vue'
import Register from '../view/Register.vue'
import Game from '../view/Game.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', component: Home, meta: { requiresAuth:true } },
    {path: '/profile', component: Profile, meta: { requiresAuth:true } },
    {path: '/user/:id', component: UserProfile, meta: { requiresAuth:true } },
    {path: '/chat/:userId?', component: Chat, meta: { requiresAuth:true } },
    {path: '/post', component: Post, meta: { requiresAuth:true } },
    {path: '/game', component: Game, meta: { requiresAuth:true } },
    {path: '/login', component: Login},
    {path: '/register', component: Register},
    {path: '/forgot-password', component: ForgotPassword}
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