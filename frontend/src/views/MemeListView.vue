<script setup>
import MemeCardComponent from '@/components/MemeCardComponent.vue'
import { useMemeStore } from '@/stores/memeSearchStore'
import { computed, ref } from 'vue'
import SidebarTopics from '@/components/SidebarTopics.vue'
import LoadingComponent from '@/components/LoadingComponent.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchBar from '@/components/sidebar/SearchBar.vue'

const store = useMemeStore()

const current_docs = computed(() => store.results.length)
const needs_scrolling = computed(
  () => current_docs.value > 1 && store.found_docs > current_docs.value,
)
const how_many_pages = computed(() =>
  current_docs.value > 0 ? Math.ceil(store.found_docs / current_docs.value) : 0,
)

const sidebar = ref(null)

function openSidebar() {
  sidebar.value?.toggle()
}
</script>

<template>
  <main class="m-auto min-h-screen space-y-8">
    <SidebarTopics class="z-60 h-dvh" ref="sidebar" />
    <div class="sticky top-0 z-50 w-full bg-[#F8BF4F]/80 backdrop-blur-md">
      <SearchBar :open-sidebar="openSidebar" />
    </div>

    <section class="relative grid min-h-full grid-cols-1 gap-6 px-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-if="store.loading"
        class="col-span-full flex min-h-full items-center justify-center text-center"
      >
        <LoadingComponent />
      </div>
      <div
        v-else-if="!store.loading && store.results.length === 0 && (store.query || store.filters)"
        class="col-span-full flex min-h-full items-center justify-center"
      >
        <p class="text-lg text-gray-500">No results found for your search criteria.</p>
      </div>
      <MemeCardComponent
        v-else
        v-for="meme in store.results.filter((m) => m.media_src?.[0]?.trim())"
        :key="meme.id"
        :id="meme.id"
        :media_type="meme?.media_type?.[0] || ''"
        :title="meme?.title?.[0] || ``"
        :media_src="meme.media_src[0]"
        :tags="meme.tags"
      />
    </section>

    <PaginationComponent
      v-if="needs_scrolling && !store.loading"
      :current-page="store.start + 1"
      :total-pages="how_many_pages"
      @update:currentPage="(page) => store.updateSearch(page - 1)"
    />
  </main>
</template>
