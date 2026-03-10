import { createRouter, createWebHistory } from 'vue-router'
import Home from "../view/Home.vue"
import Profile from "../view/Profile.vue"
import Post from "../view/Post.vue"
import Login from "../view/Login.vue"
import ForgotPassword from '../view/ForgotPassword.vue'
import Register from '../view/Register.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', component: Home},
    {path: '/profile', component: Profile},
    {path: '/post', component: Post},
    {path: '/login', component: Login},
    {path: '/register', component: Register},
    {path: '/forgot-password', component: ForgotPassword}

  ],
})

export default router
