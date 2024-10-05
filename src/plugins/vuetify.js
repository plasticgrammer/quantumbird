// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Vuetify
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#039BE5',
          secondary: '#00ACC1',
          error: '#D32F2F'
        },
      },
    },
  },
  defaults: {
    VCard: {
      elevation: 4,
    },
    VRating: {
      hover: true
    }
  },
})