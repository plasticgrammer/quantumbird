// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Vuetify
import { createVuetify } from 'vuetify'

export default createVuetify({
  defaults: {
    VCard: {
      elevation: 4
    },
    VRating: {
      hover: true
    }
  },
})