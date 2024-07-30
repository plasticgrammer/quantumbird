<template>
  <v-combobox
    :model-value="modelValue"
    :items="filteredProjectNames"
    class="project-combobox"
    label="プロジェクト"
    prepend-icon="mdi-folder-outline"
    required
    dense
    hide-details="auto"
    @update:model-value="updateValue"
    @keydown="handleKeyDown"
  >
    <template #item="{ props: itemProps, item }">
      <v-list-item v-bind="itemProps" class="project-list-item">
        <template #append>
          <v-btn
            v-if="projectNames.includes(item.title)"
            icon="mdi-close"
            size="small"
            flat
            tabindex="-1"
            @click.stop="removeProjectOption(item.title)"
          ></v-btn>
          <v-btn
            v-else
            icon="mdi-plus"
            size="small"
            color="primary"
            flat
            @click.stop="addProjectOption(item.title)"
          >
          </v-btn>
        </template>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script setup>
import { ref, computed } from 'vue'
import { updateMemberProjects } from '../services/memberService'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  projectNames: {
    type: Array,
    required: true
  },
  memberUuid: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'projectListChanged'])

const internalProjectNames = ref(props.projectNames)

const filteredProjectNames = computed(() => {
  const inputValue = props.modelValue ?? ''
  const lowerInput = inputValue.toLowerCase().trim()
  const existingProjects = new Set(internalProjectNames.value.map(name => name.toLowerCase()))
  
  const filtered = Array.from(existingProjects)
    .filter(name => name.includes(lowerInput))
  
  if (lowerInput && !existingProjects.has(lowerInput)) {
    filtered.push(inputValue)
  }
  
  return filtered
})

const updateValue = (newValue) => {
  emit('update:modelValue', newValue ?? '')
}

const addProjectOption = async (project) => {
  if (project && !internalProjectNames.value.includes(project)) {
    const newProjectList = [...internalProjectNames.value, project]
    try {
      await updateMemberProjects(props.memberUuid, newProjectList)
      internalProjectNames.value = newProjectList
      emit('projectListChanged', newProjectList)
    } catch (error) {
      console.error('Failed to add project:', error)
      // エラーハンドリング（例：エラーメッセージの表示）
    }
  }
}

const removeProjectOption = async (project) => {
  const newProjectList = internalProjectNames.value.filter(p => p !== project)
  try {
    await updateMemberProjects(props.memberUuid, newProjectList)
    internalProjectNames.value = newProjectList
    emit('projectListChanged', newProjectList)
    if (props.modelValue === project) {
      emit('update:modelValue', '')
    }
  } catch (error) {
    console.error('Failed to remove project:', error)
    // エラーハンドリング（例：エラーメッセージの表示）
  }
}

const handleKeyDown = async (event) => {
  if (event.key === 'Enter' && !event.isComposing) {
    event.preventDefault()
    const inputValue = (props.modelValue ?? '').trim()
    if (inputValue && !internalProjectNames.value.includes(inputValue)) {
      await addProjectOption(inputValue)
    }
  }
}
</script>

<style scoped>
.project-list-item:hover {
  background-color: rgba(179, 215, 255, 0.6) !important;
}
</style>