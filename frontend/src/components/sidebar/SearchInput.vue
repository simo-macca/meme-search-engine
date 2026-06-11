<script setup>
import { Search, X, SlidersHorizontal } from 'lucide-vue-next'
import { computed } from 'vue'

const model = defineModel() // v-model for searchTerm
const props = defineProps({
  filterCount: Number,
})

const emit = defineEmits(['toggleFilters', 'search'])

const showClearButton = computed(() => model.value.length > 0)

const handleClear = () => (model.value = '')
</script>

<template>
  <div class="flex items-stretch space-x-2 rounded-xl border border-gray-200 bg-white p-1 shadow-xl">
    <div class="flex items-center p-2 text-gray-500">
      <Search class="cursor-pointer" :size="20" @click="emit('search')" />
    </div>

    <input
      type="text"
      v-model="model"
      placeholder="Search your favorite memes..."
      class="w-full bg-transparent px-1 py-2 text-base text-gray-800 placeholder-gray-400 focus:ring-0 focus:outline-none"
      @keyup.enter="emit('search')"
    />

    <button
      @click="emit('toggleFilters')"
      class="relative flex items-center space-x-2 rounded-lg bg-gray-200 p-2 font-semibold text-gray-600 hover:bg-gray-200 sm:px-4 sm:py-2"
    >
      <span class="flex items-center gap-2">
        <SlidersHorizontal :size="16" />
        <span class="hidden min-[425px]:inline">Filter</span>
      </span>

      <span
        v-if="props.filterCount > 0"
        class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] text-white"
      >
        {{ props.filterCount }}
      </span>
    </button>

    <button v-if="showClearButton" @click="handleClear" class="rounded-full p-1 text-gray-400 hover:text-gray-600">
      <X :size="20" />
    </button>
  </div>
</template>
