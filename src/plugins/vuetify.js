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
          menu: '#6980B5' //607AB0,5872AD,4E688E,2A4161
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