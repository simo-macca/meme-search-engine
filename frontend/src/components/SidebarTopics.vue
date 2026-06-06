<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMemeStore } from '@/stores/memeSearchStore'
import { X } from 'lucide-vue-next'

const isOpen = ref(false)
const store = useMemeStore()

const clusters = computed(() => store.all_clusters)
const selectedTopic = computed(() => store.selected_cluster?.labels?.[0])

onMounted(() => {
  store.loadClusters()
})

function toggle() {
  isOpen.value = !isOpen.value
}

function toggleTopic(cluster) {
  store.filterByCluster(cluster)
}

function clearFilters() {
  store.filterByCluster(null)
}

function isSelected(label) {
  return selectedTopic.value === label
}

defineExpose({ toggle })
</script>

<template>
  <aside :class="['sidebar', { open: isOpen }]">
    <header class="sidebar-header">
      <h3 class="text-xl font-bold text-gray-800">Topics</h3>
      <button
        @click="toggle"
        class="flex h-8 w-8 items-center justify-center rounded-lg text-gray-600 transition-colors hover:bg-gray-200 hover:text-gray-800"
      >
        <X />
      </button>
    </header>

    <div class="mt-6 space-y-2">
      <button
        v-for="cluster in clusters"
        :key="cluster.labels[0]"
        @click="toggleTopic(cluster)"
        :class="[
          'w-full rounded-lg px-4 py-3 text-left transition-all duration-200',
          'group flex items-center justify-between',
          isSelected(cluster.labels[0])
            ? 'scale-[1.02] transform bg-blue-500 text-white shadow-md'
            : 'border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:shadow-sm',
        ]"
      >
        <span class="text-sm font-medium">{{ cluster.labels[0] }}</span>
        <span
          :class="[
            'rounded-full px-2 py-1 text-xs font-semibold',
            isSelected(cluster.labels[0])
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 group-hover:bg-gray-200',
          ]"
        >
          {{ cluster.docs.length }}
        </span>
      </button>
    </div>

    <button
      v-if="selectedTopic"
      @click="clearFilters"
      class="mt-6 w-full transform rounded-lg bg-linear-to-r from-red-500 to-red-600 px-4 py-3 text-sm font-medium text-white shadow-md transition-all duration-200 hover:scale-[1.02] hover:from-red-600 hover:to-red-700 hover:shadow-lg"
    >
      Clear Cluster Filter: {{ selectedTopic }}
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  background: linear-gradient(to bottom, #f9fafb, #f3f4f6);
  border-right: 1px solid #e5e7eb;
  padding: 1.5rem;
  position: fixed;
  top: 0;
  bottom: 0;
  left: -280px;
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar.open {
  left: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
