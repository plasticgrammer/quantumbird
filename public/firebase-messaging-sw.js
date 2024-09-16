self.addEventListener('push', function (event) {
  if (event.data) {
    const payload = event.data.json()
    console.log('Received push notification:', payload)

    // FCMから受け取ったデータ構造に合わせて処理
    const notificationData = payload.notification

    if (notificationData) {
      const title = notificationData.title || 'New Notification'
      const options = {
        body: notificationData.body || '',
        icon: [
          '/apple-touch-icon.png',
          '/favicon-32x32.png'
        ],
        //badge: '/favicon-32x32.png'
      }

      event.waitUntil(
        self.registration.showNotification(title, options)
          .then(() => {
            console.log('Notification displayed successfully')
          })
          .catch((error) => {
            console.error('Error displaying notification:', error)
          })
      )
    }
  }
})

function getNotificationTitle(data) {
  switch (data.type) {
    case 'new_report':
      return '新しいレポートが提出されました'
    case 'updated_report':
      return 'レポートが更新されました'
    default:
      return '通知'
  }
}

self.addEventListener('notificationclick', function (event) {
  event.notification.close()
  event.waitUntil(clients.openWindow('/admin/reports'))
})