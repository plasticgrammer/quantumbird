self.addEventListener('push', function (event) {
  if (event.data) {
    const payload = event.data.json()
    console.log('Received push notification:', payload)

    // FCMから受け取ったデータ構造に合わせて処理
    const notificationData = payload.notification
    const customData = payload.data || {}

    if (notificationData) {
      const title = notificationData.title || 'New Notification'
      const options = {
        body: notificationData.body || '',
        icon: '/apple-touch-icon.png',
        data: customData
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
      return '新しい週次報告が登録されました'
    case 'updated_report':
      return '週次報告が更新されました'
    default:
      return '通知'
  }
}

self.addEventListener('notificationclick', function (event) {
  event.notification.close()

  const customData = event.notification.data || {}
  const weekString = customData.weekString || ''
  let url = '/admin/reports'
  if (weekString) {
    // URLにweekStringパラメータを追加
    url += `/${encodeURIComponent(weekString)}`
  }  
  event.waitUntil(clients.openWindow(url))
})