<script setup>
import { ref } from 'vue'
import TagInput from './TagInput.vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  filters: Object,
})
const emit = defineEmits(['update:filters', 'search'])

const internal = ref({ ...props.filters })

const filterOptions = [
  { id: '1', label: 'Image' },
  { id: '2', label: 'Video' },
  { id: '3', label: 'Tags' },
]

const updateFilters = () => emit('update:filters', { ...internal.value })

const toggleFilter = (id) => {
  if (id === '3') {
    internal.value['3'] = internal.value['3'] ? null : []
  } else {
    internal.value[id] = !internal.value[id]
  }
  updateFilters()
}

const removeTag = (tag) => {
  internal.value['3'] = internal.value['3'].filter((t) => t !== tag)
  updateFilters()
}
</script>

<template>
  <div class="mt-3 rounded-xl border border-gray-300 bg-white p-4 shadow-md transition-all duration-500">
    <h3 class="mb-3 border-b border-gray-200 pb-2 text-sm font-semibold text-gray-700">Apply filters</h3>

    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="option in filterOptions"
        :key="option.id"
        class="flex cursor-pointer items-center text-sm text-gray-600"
      >
        <input
          type="checkbox"
          :checked="!!internal[option.id]"
          class="h-4 w-4 rounded border-gray-300 text-blue-600"
          @change="toggleFilter(option.id)"
        />
        <span class="ml-2">{{ option.label }}</span>
      </div>
    </div>

    <TagInput
      v-if="internal['3']"
      :model-value="internal['3']"
      @update:modelValue="
        (val) => {
          internal['3'] = val
          updateFilters()
        }
      "
      class="mt-3"
    />

    <div v-if="internal['3']?.length" class="mt-2 flex flex-wrap gap-2">
      <span
        v-for="tag in internal['3']"
        :key="tag"
        class="flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-700"
      >
        {{ tag }}
        <button @click="removeTag(tag)">
          <X size="12" class="text-blue-500 hover:text-blue-700" />
        </button>
      </span>
    </div>

    <button
      class="mt-4 w-full rounded-md bg-blue-500 px-4 py-1 text-sm text-white hover:bg-blue-600"
      @click="emit('search')"
    >
      Apply
    </button>
  </div>
</template>
