import { initializeApp } from 'firebase/app'

const firebaseConfig = {
  apiKey: process.env.VUE_APP_FIREBASE_API_KEY,
  authDomain: 'fluxweek-b9d9a.firebaseapp.com',
  projectId: 'fluxweek-b9d9a',
  storageBucket: 'fluxweek-b9d9a.appspot.com',
  messagingSenderId: '940087264635',
  appId: '1:940087264635:web:3bc11acbabfe4439fce9de',
  measurementId: 'G-V6WMXXDDKX'
}

export const app = initializeApp(firebaseConfig)