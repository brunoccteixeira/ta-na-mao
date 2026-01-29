package br.gov.tanamao

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import br.gov.tanamao.data.preferences.ThemeMode
import br.gov.tanamao.data.preferences.ThemePreferences
import br.gov.tanamao.presentation.navigation.TaNaMaoApp
import br.gov.tanamao.presentation.theme.TaNaMaoTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Main entry point for the Tá na Mão Android app.
 *
 * Features:
 * - Propel-style dark theme design
 * - Bottom navigation with 4 tabs (Home, Search, Chat, Profile)
 * - Benefit wallet and eligibility checking
 * - AI-powered chat assistant
 * - LGPD-compliant privacy settings
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var themePreferences: ThemePreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        // Install splash screen before super.onCreate
        installSplashScreen()

        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            val themeMode by themePreferences.themeMode.collectAsState(initial = ThemeMode.SYSTEM)
            val darkTheme = when (themeMode) {
                ThemeMode.SYSTEM -> isSystemInDarkTheme()
                ThemeMode.LIGHT -> false
                ThemeMode.DARK -> true
            }

            TaNaMaoTheme(darkTheme = darkTheme) {
                TaNaMaoApp()
            }
        }
    }
}
