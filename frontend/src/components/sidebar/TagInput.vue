<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Array,
})
const emit = defineEmits(['update:modelValue'])

const tagInput = ref('')

watch(tagInput, (val) => {
  if (val.includes(',')) {
    const tags = val
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length)

    emit('update:modelValue', [...props.modelValue, ...tags])
    tagInput.value = ''
  }
})
</script>

<template>
  <div class="flex flex-col space-y-2">
    <label class="text-sm font-medium text-gray-700">Tags</label>

    <input
      type="text"
      v-model="tagInput"
      placeholder="Insert tags (comma separated)"
      class="rounded-md border border-gray-300 p-2 text-sm focus:border-blue-500"
    />
  </div>
</template>
