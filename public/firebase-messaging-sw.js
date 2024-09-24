self.addEventListener('push', function (event) {
  if (event.data) {
    const payload = event.data.json()
    console.log('Received push notification:', payload)

    // FCMから受け取ったデータ構造に合わせて処理
    const notificationData = payload.notification
    const customData = payload.data || {}

    if (notificationData) {
      const contextPath = getContextPath()
      const title = notificationData.title || 'New Notification'
      const options = {
        body: notificationData.body || '',
        icon: `${contextPath}apple-touch-icon.png`,
        data: customData
        //badge: '${contextPath}favicon-32x32.png'
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

function getContextPath() {
  return self.registration.scope.replace(self.location.origin, '')
}

self.addEventListener('notificationclick', function (event) {
  event.notification.close()

  const contextPath = getContextPath()
  const customData = event.notification.data || {}
  const weekString = customData.weekString || ''
  let url = `${contextPath}admin/reports`
  if (weekString) {
    url += `/${encodeURIComponent(weekString)}`
  }
  event.waitUntil(clients.openWindow(url))
})