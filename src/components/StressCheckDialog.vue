<template>
  <v-dialog v-model="dialog" max-width="600px">
    <v-card color="blue-lighten-5" min-height="430px" rounded="lg">
      <v-card-text class="pt-0">
        <v-img
          src="@/assets/images/advisor_mental.png"
          max-width="200"
          class="mx-auto my-0"
          :aspect-ratio="1"
        ></v-img>

        <div v-if="currentStep == 0">
          <!-- 初期説明画面 -->
          <v-card flat class="bg-plain">
            <v-card-title class="text-h5 text-center">ストレスチェックへようこそ</v-card-title>
            <v-card-text>
              <p>このチェックは、あなたの現在のストレスレベルを評価するためのものです。</p>
              <p>システムに回答を保持することはありません。</p>
              <p>１０の質問に対して [いいえ] から [はい] の５段階で評価してください。</p>
              <p>準備ができたら「開始」ボタンをクリックしてください。</p>
            </v-card-text>
          </v-card>
          <v-btn color="secondary" block class="mt-6" @click="startCheck">
            開始
          </v-btn>
        </div>

        <div v-if="currentStep > 0 && !showResult">
          <div class="d-flex align-center mb-5">
            <v-progress-linear
              :model-value="progressPercentage"
              color="deep-purple-accent-2"
              striped
              rounded
              height="26"
              class="flex-grow-1 mr-2 progress-bar"
            >
              <template #default>
                <strong>{{ currentStep }} / {{ questions.length }}</strong>
              </template>
            </v-progress-linear>
          </div>
          <v-window 
            v-model="currentStep" 
            show-arrows
          >
            <template #next>
            </template>
            <v-window-item
              v-for="(question, index) in questions"
              :key="index"
              :value="index + 1"
            >
              <v-card
                max-width="500px"
                class="mx-auto my-1 px-6 bg-plain"
              >
                <v-card-title class="text-body-1 text-center">Q{{ index + 1 }}. {{ question }}</v-card-title>
                <v-card-text class="text-center pb-0">
                  <v-rating 
                    v-model="answers[index]" 
                    :item-labels="['いいえ','','','','はい']"
                    size="x-large"
                    active-color="deep-purple-accent-2"
                    color="grey-lighten-2"
                    empty-icon="mdi-emoticon-neutral-outline"
                    full-icon="mdi-emoticon-dead"
                    length="5" 
                    hover
                    @update:model-value="handleRatingUpdate(index)"
                  ></v-rating>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </div>

        <div v-if="showResult">
          <v-card flat>
            <v-card-title class="text-h5">チェック結果</v-card-title>
            <v-card-text>
              <p class="text-deep-purple-accent-4">あなたのストレスレベル:<span class="text-h4 ml-2"> {{ stressLevel }}</span> / 5.0</p>
              <p>{{ getStressLevelDescription() }}</p>
            </v-card-text>
          </v-card>
          <v-btn color="secondary" block class="mt-6" @click="closeDialog">
            閉じる
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const emit = defineEmits(['stress-level-updated'])

const dialog = ref(false)
const currentStep = ref(0)
const showResult = ref(false)
const stressLevel = ref(0)
const progressPercentage = ref(0)

const questions = [
  '最近、仕事や生活でイライラすることが多いですか？',
  '睡眠の質が低下していると感じますか？',
  '食欲に変化がありますか？',
  '集中力が低下していると感じますか？',
  '身体的な疲労を感じますか？',
  '仕事や責任に対して圧倒されていると感じますか？',
  '家族や友人との関係に悪影響が出ていますか？',
  '頭痛や筋肉の張りなど、身体的な症状がありますか？',
  '将来に対して不安を感じることが増えましたか？',
  '趣味や楽しみのための時間が減っていますか？'
]

const answers = reactive(Array(questions.length).fill(0))

const closeDialog = () => {
  dialog.value = false
}

const startCheck = () => {
  currentStep.value = 1
}

const submitStressCheck = () => {
  const totalScore = answers.reduce((sum, current) => sum + current, 0)
  const averageScore = totalScore / questions.length
  stressLevel.value = averageScore.toFixed(1)
  emit('stress-level-updated', stressLevel.value)
  showResult.value = true
}

const updateProgress = () => {
  const currentProgressStep = currentStep.value
  progressPercentage.value = (currentProgressStep / questions.length) * 100
}

const handleRatingUpdate = (index) => {
  if (index === questions.length - 1) {
    // 最後の質問の場合、100%にして完了
    progressPercentage.value = 100
    submitStressCheck()
  } else {
    // 次の質問に進む
    currentStep.value++
  }
}

const openDialog = () => {
  currentStep.value = 0
  answers.fill(0)
  showResult.value = false
  dialog.value = true
  updateProgress()
}

const getStressLevelDescription = () => {
  if (stressLevel.value <= 1) return 'ストレスレベルは低めです。現在の状態を維持しましょう。'
  if (stressLevel.value <= 2) return 'ストレスレベルは平均的です。定期的にリラックスする時間を設けましょう。'
  if (stressLevel.value <= 3) return 'ストレスレベルがやや高めです。ストレス解消法を見直してみましょう。'
  if (stressLevel.value <= 4) return 'ストレスレベルが高めです。休息を取り、必要であれば専門家に相談することを検討しましょう。'
  return 'ストレスレベルがかなり高いです。早急に休息を取り、専門家に相談することをおすすめします。'
}

// currentStepが変更されるたびにプログレスを更新
watch(currentStep, updateProgress)

defineExpose({ openDialog })
</script>

<style scoped>
.progress-bar {
  transition: all 0.5s ease-out;
}
</style>