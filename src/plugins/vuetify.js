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
          error: '#D32F2F',
          menu: '#5872AD' //6980B5,4E688E,2A4161
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