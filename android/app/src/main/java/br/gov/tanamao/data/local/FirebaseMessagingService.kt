package br.gov.tanamao.data.local

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class TaNaMaoMessagingService : FirebaseMessagingService() {

    @Inject
    lateinit var notificationManager: NotificationManager

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        Log.d(TAG, "From: ${remoteMessage.from}")

        // Check if message contains data payload
        if (remoteMessage.data.isNotEmpty()) {
            Log.d(TAG, "Message data payload: ${remoteMessage.data}")
            handleDataMessage(remoteMessage.data)
        }

        // Check if message contains notification payload
        remoteMessage.notification?.let {
            Log.d(TAG, "Message Notification Body: ${it.body}")
            handleNotificationMessage(it.title ?: "Tá na Mão", it.body ?: "")
        }
    }

    private fun handleDataMessage(data: Map<String, String>) {
        val type = data["type"] ?: return
        val title = data["title"] ?: "Tá na Mão"
        val message = data["message"] ?: ""
        val deepLink = data["deep_link"]

        val notificationType = when (type) {
            "payment" -> NotificationType.PAYMENT
            "deadline" -> NotificationType.DEADLINE
            "money" -> NotificationType.MONEY
            "alert" -> NotificationType.ALERT
            else -> NotificationType.ALERT
        }

        notificationManager.showNotification(
            title = title,
            message = message,
            type = notificationType,
            deepLink = deepLink
        )
    }

    private fun handleNotificationMessage(title: String, body: String) {
        notificationManager.showNotification(
            title = title,
            message = body,
            type = NotificationType.ALERT
        )
    }

    override fun onNewToken(token: String) {
        Log.d(TAG, "Refreshed token: $token")
        // Send token to backend
        sendRegistrationToServer(token)
    }

    private fun sendRegistrationToServer(token: String) {
        // NOTE: FCM token registration endpoint not yet implemented in backend
        // When endpoint is available, implement as follows:
        // 1. Add endpoint to TaNaMaoApi: @POST("user/fcm-token") suspend fun registerFcmToken(@Body request: FcmTokenRequest)
        // 2. Inject TaNaMaoApi or UserRepository here
        // 3. Call API in coroutine scope
        // 4. Handle success/error appropriately
        //
        // For now, token is logged and can be retrieved from logs when needed
        Log.d(TAG, "FCM Token to register: $token")
        Log.d(TAG, "Token will be sent to backend when endpoint is available")
    }

    companion object {
        private const val TAG = "TaNaMaoMessagingService"
    }
}



