import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/meme-list',
      name: 'List of memes',
      component: () => import('../views/MemeListView.vue'),
    },
  ],
})

export default router
