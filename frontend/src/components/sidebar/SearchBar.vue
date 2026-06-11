<script setup>
import { ref, computed } from 'vue'
import router from '@/router/index.js'
import { useRoute } from 'vue-router'
import { Menu } from 'lucide-vue-next'
import { useMemeStore } from '@/stores/memeSearchStore.js'

import SearchInput from './SearchInput.vue'
import FilterPanel from './FilterPanel.vue'
import ActiveFiltersBar from './ActiveFiltersBar.vue'

const props = defineProps({
  onHomePage: { type: Boolean, default: false },
  openSidebar: Function,
})

const searchTerm = ref('')
const activeFilters = ref({})
const isFilterOpen = ref(false)

const route = useRoute()
const store = useMemeStore()

const showMenu = computed(() => route.name !== 'Home')

const activeFilterCount = computed(() => {
  let count = 0
  if (activeFilters.value['1']) count++
  if (activeFilters.value['2']) count++
  if (activeFilters.value['3']?.length) count++
  return count
})

const performSearch = () => {
  isFilterOpen.value = false
  store.query = searchTerm.value
  store.filters = activeFilters.value
  store.start = 0
  store.performSearch()

  if (props.onHomePage) router.push('/meme-list')
}

const clearAllFilters = () => {
  activeFilters.value = {}
  store.filterByCluster(null)
  performSearch()
}
</script>

<template>
  <div class="flex w-full items-center gap-4 p-8">
    <Menu v-if="showMenu" @click="openSidebar" :size="35" class="m-[13px] self-start text-left" />

    <div class="mx-auto w-full max-w-xl">
      <SearchInput
        v-model="searchTerm"
        :filterCount="activeFilterCount"
        @toggleFilters="isFilterOpen = !isFilterOpen"
        @search="performSearch"
      />

      <ActiveFiltersBar :cluster="store.selected_cluster" :count="activeFilterCount" @clear="clearAllFilters" />

      <FilterPanel v-if="isFilterOpen" v-model:filters="activeFilters" @search="performSearch" />
    </div>
  </div>
</template>
