package br.gov.tanamao

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for Tá na Mão Android app.
 *
 * This class is annotated with @HiltAndroidApp to enable Hilt dependency injection.
 */
@HiltAndroidApp
class TaNaMaoApp : Application() {

    override fun onCreate() {
        super.onCreate()
        // Initialize any app-wide services here
    }
}
