import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/upload' },
  { path: '/upload', name: 'upload', component: () => import('../views/UploadView.vue') },
  { path: '/chat', name: 'chat', component: () => import('../views/ChatView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router