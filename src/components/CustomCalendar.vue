<template>
    <v-sheet class="custom-calendar ma-1" rounded>
      <div class="text-center py-1">{{ monthName }} {{ year }}</div>
      <v-row no-gutters class="calendar-header">
        <v-col v-for="day in weekdays" :key="day" cols="1" class="text-center">
          {{ day }}
        </v-col>
      </v-row>
      <v-row no-gutters v-for="week in calendarDays" :key="week[0].date">
        <v-col v-for="day in week" :key="day.date" cols="1">
          <div
            class="date-cell"
            :class="{
              'selected': isSelected(day.date),
              'today': isToday(day.date),
              'in-month': day.inMonth
            }"
            @click="selectDate(day.date)"
          >
            {{ day.dayOfMonth }}
          </div>
        </v-col>
      </v-row>
    </v-sheet>
  </template>
  
  <script>
  import { computed } from 'vue'
  
  export default {
    name: 'CustomCalendar',
    props: {
      year: {
        type: Number,
        required: true
      },
      month: {
        type: Number,
        required: true
      },
      selectedDate: {
        type: String,
        required: true
      }
    },
    setup(props, { emit }) {
      const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  
      const monthName = computed(() => {
        return new Date(props.year, props.month, 1).toLocaleString('ja-JP', { month: 'long' })
      })
  
      const calendarDays = computed(() => {
        const firstDay = new Date(props.year, props.month, 1)
        const lastDay = new Date(props.year, props.month + 1, 0)
        const days = []
  
        for (let i = 0; i < firstDay.getDay(); i++) {
          const prevMonthDay = new Date(props.year, props.month, -i)
          days.unshift({ date: prevMonthDay.toISOString().split('T')[0], dayOfMonth: prevMonthDay.getDate(), inMonth: false })
        }
  
        for (let i = 1; i <= lastDay.getDate(); i++) {
          const currentDate = new Date(props.year, props.month, i)
          days.push({ date: currentDate.toISOString().split('T')[0], dayOfMonth: i, inMonth: true })
        }
  
        while (days.length % 7 !== 0) {
          const nextMonthDay = new Date(props.year, props.month + 1, days.length - firstDay.getDay() + 1)
          days.push({ date: nextMonthDay.toISOString().split('T')[0], dayOfMonth: nextMonthDay.getDate(), inMonth: false })
        }
  
        return days.reduce((weeks, day, index) => {
          if (index % 7 === 0) weeks.push([])
          weeks[weeks.length - 1].push(day)
          return weeks
        }, [])
      })
  
      const isSelected = (date) => date === props.selectedDate
  
      const isToday = (date) => date === new Date().toISOString().split('T')[0]
  
      const selectDate = (date) => {
        emit('select-date', date)
      }
  
      return {
        weekdays,
        monthName,
        calendarDays,
        isSelected,
        isToday,
        selectDate
      }
    }
  }
  </script>
  
  <style scoped>
  .custom-calendar {
    width: 100%;
    max-width: 300px;
  }
  
  .calendar-header {
    font-weight: bold;
    font-size: 0.8em;
  }
  
  .date-cell {
    width: 24px;
    height: 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1px;
    font-size: 0.8em;
    cursor: pointer;
  }
  
  .date-cell.selected {
    background-color: rgba(var(--v-theme-primary), 0.1);
    font-weight: bold;
  }
  
  .date-cell.today {
    text-decoration: underline;
  }
  
  .date-cell:not(.in-month) {
    color: #ccc;
  }
  </style>