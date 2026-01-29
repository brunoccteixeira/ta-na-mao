package br.gov.tanamao

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class MainActivityTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun app_launches() {
        // Verify that the app launches successfully
        composeTestRule.onNodeWithText("Tá na Mão", substring = true).assertIsDisplayed()
    }

    @Test
    fun navigation_works() {
        // Test navigation between screens
        composeTestRule.onNodeWithText("Home", substring = true).assertIsDisplayed()
        
        // Navigate to search
        composeTestRule.onNodeWithText("Buscar", substring = true).performClick()
        composeTestRule.onNodeWithText("Buscar", substring = true).assertIsDisplayed()
    }
}






