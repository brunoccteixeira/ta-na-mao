package br.gov.tanamao.data.local

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import br.gov.tanamao.MainActivity
import br.gov.tanamao.R
import br.gov.tanamao.domain.model.AlertCategory
import br.gov.tanamao.presentation.navigation.Screen
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationManager @Inject constructor(
    private val context: Context
) {
    private val notificationManager =
        context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    init {
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channels = listOf(
                NotificationChannel(
                    CHANNEL_ALERTS,
                    "Alertas de Benefícios",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notificações sobre pagamentos, prazos e novos benefícios"
                },
                NotificationChannel(
                    CHANNEL_PAYMENTS,
                    "Pagamentos",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notificações sobre pagamentos recebidos"
                },
                NotificationChannel(
                    CHANNEL_DEADLINES,
                    "Prazos Importantes",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notificações sobre prazos e deadlines"
                },
                NotificationChannel(
                    CHANNEL_MONEY,
                    "Dinheiro Esquecido",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notificações sobre dinheiro esquecido disponível"
                }
            )

            channels.forEach { channel ->
                notificationManager.createNotificationChannel(channel)
            }
        }
    }

    fun showNotification(
        title: String,
        message: String,
        type: NotificationType,
        deepLink: String? = null
    ) {
        val channelId = when (type) {
            NotificationType.ALERT -> CHANNEL_ALERTS
            NotificationType.PAYMENT -> CHANNEL_PAYMENTS
            NotificationType.DEADLINE -> CHANNEL_DEADLINES
            NotificationType.MONEY -> CHANNEL_MONEY
        }

        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            deepLink?.let { putExtra("deep_link", it) }
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(
                when (type) {
                    NotificationType.DEADLINE, NotificationType.ALERT -> NotificationCompat.PRIORITY_HIGH
                    else -> NotificationCompat.PRIORITY_DEFAULT
                }
            )
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }

    fun showPaymentNotification(amount: Double, benefitName: String) {
        showNotification(
            title = "Pagamento recebido!",
            message = "$benefitName: ${amount.formatAsCurrency()} disponível",
            type = NotificationType.PAYMENT,
            deepLink = Screen.Wallet.route
        )
    }

    fun showDeadlineNotification(title: String, message: String, deadline: String) {
        showNotification(
            title = "⚠️ $title",
            message = "$message\nPrazo: $deadline",
            type = NotificationType.DEADLINE,
            deepLink = Screen.Alerts.route
        )
    }

    fun showMoneyFoundNotification(amount: Double) {
        showNotification(
            title = "💰 Dinheiro encontrado!",
            message = "Você tem R$ ${amount.formatAsCurrency()} disponível para resgate",
            type = NotificationType.MONEY,
            deepLink = Screen.Money.route
        )
    }

    fun showNewBenefitNotification(benefitName: String) {
        showNotification(
            title = "Novo benefício disponível!",
            message = "Você pode ter direito a $benefitName",
            type = NotificationType.ALERT,
            deepLink = Screen.Chat.createRoute("tenho direito a $benefitName")
        )
    }

    companion object {
        private const val CHANNEL_ALERTS = "alerts"
        private const val CHANNEL_PAYMENTS = "payments"
        private const val CHANNEL_DEADLINES = "deadlines"
        private const val CHANNEL_MONEY = "money"
    }
}

enum class NotificationType {
    ALERT,
    PAYMENT,
    DEADLINE,
    MONEY
}

private fun Double.formatAsCurrency(): String {
    return "R$ %.2f".format(this).replace(".", ",")
}

