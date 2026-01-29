package br.gov.tanamao.presentation.ui.money

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MoneyScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun moneyScreen_displaysOverview() {
        composeTestRule.setContent {
            MoneyScreen(
                onNavigateBack = {},
                onNavigateToChat = {}
            )
        }

        composeTestRule.waitForIdle()

        // Verify screen displays money overview
        composeTestRule.onNodeWithText("Dinheiro Esquecido", substring = true).assertExists()
        composeTestRule.onNodeWithText("PIS", substring = true).assertExists()
    }

    @Test
    fun moneyScreen_displaysMoneyTypes() {
        composeTestRule.setContent {
            MoneyScreen(
                onNavigateBack = {},
                onNavigateToChat = {}
            )
        }

        composeTestRule.waitForIdle()

        // Verify all money types are displayed
        composeTestRule.onNodeWithText("PIS/PASEP", substring = true).assertExists()
        composeTestRule.onNodeWithText("SVR", substring = true).assertExists()
        composeTestRule.onNodeWithText("FGTS", substring = true).assertExists()
    }

    @Test
    fun moneyScreen_canNavigateToGuide() {
        var navigatedToChat = false
        var chatMessage: String? = null

        composeTestRule.setContent {
            MoneyScreen(
                onNavigateBack = {},
                onNavigateToChat = { message ->
                    navigatedToChat = true
                    chatMessage = message
                }
            )
        }

        composeTestRule.waitForIdle()

        // Click on guide button
        composeTestRule.onNodeWithText("Ver guia", substring = true)
            .onFirst()
            .performClick()

        // Verify navigation occurred
        assert(navigatedToChat)
        assert(chatMessage?.contains("guia", ignoreCase = true) == true)
    }
}



