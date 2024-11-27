<template>
  <BaseWidget
    widget-id="todo"
    title="やることリスト"
    icon="mdi-clipboard-check-outline"
  >
    <template #header-append>
      <v-btn
        v-if="hasCompletedTasks"
        color="error"
        size="small"
        variant="outlined"
        @click="clearCompletedTasks"
      >
        完了済み削除
      </v-btn>
    </template>

    <div v-if="tasks.length > 0" class="pa-0">
      <v-checkbox
        v-for="task in tasks"
        :key="task.taskId"
        v-model="task.completed"
        color="info"
        class="todo-item pa-0"
        hide-details
        density="compact"
        @change="handleTaskCompletion(task)"
      >
        <template #label>
          <span :class="{ 'text-decoration-line-through': task.completed }">
            {{ task.title }}
          </span>
        </template>
      </v-checkbox>
    </div>
    <p v-else>タスクがありません</p>
    <v-text-field
      v-model="newTaskTitle"
      label="新しいタスク"
      hide-details
      single-line
      density="compact"
      class="mt-2"
      append-inner-icon="mdi-plus"
      @click:append-inner="addTask"
      @keydown.enter="handleNewTaskKeydown($event)"
    ></v-text-field>
  </BaseWidget>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { submitUserTasks, updateUserTasks, deleteUserTasks, listUserTasks } from '@/services/userTasksService'
import BaseWidget from './BaseWidget.vue'

const store = useStore()
const error = ref(null)
const tasks = ref([])
const newTaskTitle = ref('')
const hasCompletedTasks = computed(() => tasks.value.some(task => task.completed))
const userId = store.getters['auth/cognitoUserSub']

const fetchTasks = async () => {
  try {
    if (!userId) {
      console.error('User ID is not available')
      return
    }

    const response = await listUserTasks(userId)
    if (response && Array.isArray(response)) {
      tasks.value = response
    } else {
      tasks.value = []
    }
  } catch (err) {
    console.error('タスクの取得に失敗しました:', err)
    tasks.value = []
  }
}

const handleNewTaskKeydown = async (event) => {
  if (event.key === 'Enter' && !event.isComposing) {
    event.preventDefault()
    await addTask()
  }
}

const addTask = async () => {
  if (newTaskTitle.value.trim() && userId) {
    try {
      const newTask = {
        title: newTaskTitle.value.trim(),
        userId: userId,
        createdAt: new Date().toISOString(),
        completed: false
      }
      const response = await submitUserTasks(newTask)
      tasks.value.push(response)
      newTaskTitle.value = ''
    } catch (error) {
      console.error('タスクの追加に失敗しました:', error)
    }
  }
}

const handleTaskCompletion = async (task) => {
  try {
    await updateUserTasks({
      ...task,
      completed: task.completed
    })
  } catch (error) {
    console.error('タスクの更新に失敗しました:', error)
    task.completed = !task.completed // エラーの場合、UI上で元の状態に戻す
  }
}

const clearCompletedTasks = async () => {
  if (!userId) {
    console.error('User ID is not available')
    return
  }

  const completedTasks = tasks.value.filter(task => task.completed)
  
  error.value = null
  try {
    await Promise.all(completedTasks.map(task => deleteUserTasks(userId, task.taskId)))
    tasks.value = tasks.value.filter(task => !task.completed)
  } catch (err) {
    console.error('完了済みタスクの削除に失敗しました:', err)
  }
}

// Lifecycle hooks
onMounted(fetchTasks)
</script>

<style scoped>
.todo-item :deep() .v-selection-control {
  min-height: 1.2em !important;
}

.todo-item :deep() .v-label {
  padding-left: 8px;
}
</style>