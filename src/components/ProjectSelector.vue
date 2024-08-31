<template>
  <v-combobox
    :model-value="modelValue"
    :items="filteredProjectNames"
    class="project-combobox"
    label="プロジェクト"
    required
    dense
    hide-details="auto"
    @update:model-value="updateValue"
    @keydown="handleKeyDown"
  >
    <template #prepend>
      <v-icon class="d-none d-md-flex">
        mdi-folder-outline
      </v-icon>
    </template>
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
import { ref, computed, inject } from 'vue'
import { updateMemberProjects } from '../services/publicService'

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

const showConfirmDialog = inject('showConfirmDialog')
const showNotification = inject('showNotification')
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
      showNotification('プロジェクトリストに登録しました。')
      internalProjectNames.value = newProjectList
      emit('projectListChanged', newProjectList)
    } catch (error) {
      console.error('Failed to add project:', error)
    }
  }
}

const removeProjectOption = async (project) => {
  const confirmed = await showConfirmDialog('確認', 'プロジェクトリストから削除します。よろしいですか？')
  if (!confirmed) {
    return
  }
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