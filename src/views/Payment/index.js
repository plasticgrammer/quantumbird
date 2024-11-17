
async function handlePaymentSubmit() {
    try {
        // ...existing code...

        // 古い呼び出し
        // await store.dispatch('auth/updateSubscriptionAttributes', { ... })

        // 新しい呼び出し
        await store.dispatch('auth/updateSubscriptionInfo', {
            stripeCustomerId: response.subscription.stripeCustomerId
        })

        // ...existing code...
    } catch (error) {
        // ...existing code...
    }
}

// ...existing code...