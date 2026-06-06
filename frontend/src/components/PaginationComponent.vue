<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

const emit = defineEmits(['update:currentPage'])

const maxButtons = 5

const visiblePages = computed(() => {
  const pages = []
  let startPage = Math.max(1, props.currentPage - 2)
  let endPage = Math.min(props.totalPages, startPage + maxButtons - 1)

  if (endPage - startPage + 1 < maxButtons) {
    startPage = Math.max(1, endPage - maxButtons + 1)
  }

  for (let i = startPage; i <= endPage; i++) pages.push(i)
  return pages
})

function goTo(page) {
  if (page >= 1 && page <= props.totalPages) {
    emit('update:currentPage', page)
  }
}
</script>

<template>
  <div v-if="totalPages > 1" class="flex flex-wrap justify-center gap-2 px-4 py-3">
    <!-- Prev -->
    <button
      @click="goTo(currentPage - 1)"
      :disabled="currentPage === 1"
      class="rounded bg-white px-3 py-1 text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
    >
      &lt;
    </button>

    <!-- Page numbers -->
    <button
      v-for="n in visiblePages"
      :key="n"
      :class="[
        'rounded-full px-3 py-1 text-xs',
        n === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100',
      ]"
      @click="goTo(n)"
    >
      {{ n }}
    </button>

    <!-- Next -->
    <button
      @click="goTo(currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="rounded bg-white px-3 py-1 text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
    >
      &gt;
    </button>
  </div>
</template>
