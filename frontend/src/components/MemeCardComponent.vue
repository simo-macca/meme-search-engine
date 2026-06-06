<script setup>
const props = defineProps({
  id: String,
  media_type: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  media_src: {
    type: String,
    required: true,
  },
  tags: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <div class="w-full overflow-hidden rounded-xl border border-gray-200 bg-white shadow-md">
    <!-- Header -->
    <div class="border-b border-gray-100 px-4 py-3">
      <h2 class="my-scrollbar h-6 overflow-auto text-sm font-semibold text-nowrap text-gray-800">
        {{ props.title }}
      </h2>
    </div>

    <!-- Main Content -->
    <div class="flex h-64 items-center justify-center p-4">
      <!-- Render image -->
      <img
        v-if="props.media_type === 'image'"
        :src="props.media_src"
        :alt="props.title"
        class="max-h-60 w-full rounded-lg object-contain"
        loading="lazy"
      />

      <!-- Render video -->
      <video
        v-else-if="props.media_type === 'video'"
        :src="props.media_src"
        controls
        class="max-h-60 w-full rounded-lg object-contain"
        loading="lazy"
      ></video>
    </div>

    <!-- Footer -->
    <div class="flex flex-wrap gap-2 border-t border-gray-100 px-4 py-3">
      <span
        v-for="tag in props.tags"
        :key="tag"
        class="h-6 rounded-full bg-gray-200 px-2 py-1 text-xs text-gray-700"
      >
        # {{ tag }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.my-scrollbar::-webkit-scrollbar {
  width: 0;
  height: 5px;
}

.my-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.my-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.my-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
