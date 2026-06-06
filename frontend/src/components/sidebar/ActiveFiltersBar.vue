<script setup>
const props = defineProps({
  cluster: Object,
  count: Number,
})

const emit = defineEmits(['clear'])
</script>

<template>
  <div v-if="props.cluster || count > 0" class="mt-2 flex items-center gap-2 px-1">
    <span
      v-if="props.cluster"
      class="flex items-center gap-1 rounded-md border border-amber-200 bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700"
    >
      Topic: {{ props.cluster.labels[0] }}
    </span>

    <button
      @click="emit('clear')"
      class="ml-auto cursor-pointer text-xs text-blue-500 hover:underline"
    >
      Clear all
    </button>
  </div>
</template>
