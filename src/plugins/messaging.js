import { getMessaging } from 'firebase/messaging'
import { app } from '../config/firebase-config'

export const messaging = getMessaging(app)