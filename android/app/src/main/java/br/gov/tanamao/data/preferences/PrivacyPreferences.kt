package br.gov.tanamao.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "privacy_settings")

/**
 * Privacy and consent preferences using DataStore
 */
@Singleton
class PrivacyPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    companion object {
        // Consent keys
        private val CONSENT_ACCEPTED = booleanPreferencesKey("consent_accepted")
        private val CONSENT_DATE = stringPreferencesKey("consent_date")
        private val CONSENT_VERSION = stringPreferencesKey("consent_version")

        // Data collection preferences
        private val ANALYTICS_ENABLED = booleanPreferencesKey("analytics_enabled")
        private val CRASH_REPORTS_ENABLED = booleanPreferencesKey("crash_reports_enabled")
        private val PERSONALIZATION_ENABLED = booleanPreferencesKey("personalization_enabled")
        private val LOCATION_ENABLED = booleanPreferencesKey("location_enabled")

        // Notification preferences
        private val NOTIFICATIONS_ENABLED = booleanPreferencesKey("notifications_enabled")
        private val PAYMENT_ALERTS_ENABLED = booleanPreferencesKey("payment_alerts_enabled")
        private val BENEFIT_ALERTS_ENABLED = booleanPreferencesKey("benefit_alerts_enabled")
        private val DEADLINE_ALERTS_ENABLED = booleanPreferencesKey("deadline_alerts_enabled")

        // Security
        private val BIOMETRIC_ENABLED = booleanPreferencesKey("biometric_enabled")
        private val SESSION_TIMEOUT_MINUTES = intPreferencesKey("session_timeout_minutes")

        // Current consent version
        const val CURRENT_CONSENT_VERSION = "1.0.0"
    }

    // Consent status
    val hasAcceptedConsent: Flow<Boolean> = dataStore.data.map { prefs ->
        prefs[CONSENT_ACCEPTED] == true &&
                prefs[CONSENT_VERSION] == CURRENT_CONSENT_VERSION
    }

    val consentDate: Flow<String?> = dataStore.data.map { prefs ->
        prefs[CONSENT_DATE]
    }

    // Privacy settings
    val privacySettings: Flow<PrivacySettings> = dataStore.data.map { prefs ->
        PrivacySettings(
            analyticsEnabled = prefs[ANALYTICS_ENABLED] ?: false,
            crashReportsEnabled = prefs[CRASH_REPORTS_ENABLED] ?: true,
            personalizationEnabled = prefs[PERSONALIZATION_ENABLED] ?: true,
            locationEnabled = prefs[LOCATION_ENABLED] ?: false
        )
    }

    // Notification settings
    val notificationSettings: Flow<NotificationSettings> = dataStore.data.map { prefs ->
        NotificationSettings(
            enabled = prefs[NOTIFICATIONS_ENABLED] ?: true,
            paymentAlerts = prefs[PAYMENT_ALERTS_ENABLED] ?: true,
            benefitAlerts = prefs[BENEFIT_ALERTS_ENABLED] ?: true,
            deadlineAlerts = prefs[DEADLINE_ALERTS_ENABLED] ?: true
        )
    }

    // Security settings
    val securitySettings: Flow<SecuritySettings> = dataStore.data.map { prefs ->
        SecuritySettings(
            biometricEnabled = prefs[BIOMETRIC_ENABLED] ?: false,
            sessionTimeoutMinutes = prefs[SESSION_TIMEOUT_MINUTES] ?: 15
        )
    }

    // Accept consent
    suspend fun acceptConsent() {
        dataStore.edit { prefs ->
            prefs[CONSENT_ACCEPTED] = true
            prefs[CONSENT_DATE] = LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME)
            prefs[CONSENT_VERSION] = CURRENT_CONSENT_VERSION
        }
    }

    // Revoke consent
    suspend fun revokeConsent() {
        dataStore.edit { prefs ->
            prefs[CONSENT_ACCEPTED] = false
            prefs[ANALYTICS_ENABLED] = false
            prefs[PERSONALIZATION_ENABLED] = false
            prefs[LOCATION_ENABLED] = false
        }
    }

    // Update privacy settings
    suspend fun updatePrivacySettings(settings: PrivacySettings) {
        dataStore.edit { prefs ->
            prefs[ANALYTICS_ENABLED] = settings.analyticsEnabled
            prefs[CRASH_REPORTS_ENABLED] = settings.crashReportsEnabled
            prefs[PERSONALIZATION_ENABLED] = settings.personalizationEnabled
            prefs[LOCATION_ENABLED] = settings.locationEnabled
        }
    }

    // Update notification settings
    suspend fun updateNotificationSettings(settings: NotificationSettings) {
        dataStore.edit { prefs ->
            prefs[NOTIFICATIONS_ENABLED] = settings.enabled
            prefs[PAYMENT_ALERTS_ENABLED] = settings.paymentAlerts
            prefs[BENEFIT_ALERTS_ENABLED] = settings.benefitAlerts
            prefs[DEADLINE_ALERTS_ENABLED] = settings.deadlineAlerts
        }
    }

    // Update security settings
    suspend fun updateSecuritySettings(settings: SecuritySettings) {
        dataStore.edit { prefs ->
            prefs[BIOMETRIC_ENABLED] = settings.biometricEnabled
            prefs[SESSION_TIMEOUT_MINUTES] = settings.sessionTimeoutMinutes
        }
    }

    // Request data deletion
    suspend fun requestDataDeletion(): Boolean {
        // In a real app, this would trigger a backend request
        dataStore.edit { prefs ->
            prefs.clear()
        }
        return true
    }

    // Export user data
    suspend fun exportUserData(): UserDataExport {
        // In a real app, this would compile all user data
        return UserDataExport(
            exportDate = LocalDateTime.now(),
            consentDate = null,
            preferences = emptyMap()
        )
    }
}

data class PrivacySettings(
    val analyticsEnabled: Boolean = false,
    val crashReportsEnabled: Boolean = true,
    val personalizationEnabled: Boolean = true,
    val locationEnabled: Boolean = false
)

data class NotificationSettings(
    val enabled: Boolean = true,
    val paymentAlerts: Boolean = true,
    val benefitAlerts: Boolean = true,
    val deadlineAlerts: Boolean = true
)

data class SecuritySettings(
    val biometricEnabled: Boolean = false,
    val sessionTimeoutMinutes: Int = 15
)

data class UserDataExport(
    val exportDate: LocalDateTime,
    val consentDate: LocalDateTime?,
    val preferences: Map<String, Any>
)
