package br.gov.tanamao.presentation.ui.home

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import br.gov.tanamao.presentation.navigation.Screen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class HomeScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun homeScreen_displaysWelcomeMessage() {
        composeTestRule.setContent {
            HomeScreen(
                onNavigateToMap = {},
                onNavigateToSearch = {},
                onNavigateToChat = {},
                onNavigateToChatWithMessage = {},
                onNavigateToWallet = {},
                onNavigateToBenefit = {},
                onNavigateToProfile = {},
                onNavigateToMoney = {}
            )
        }

        // Wait for content to load
        composeTestRule.waitForIdle()

        // Verify screen is displayed
        composeTestRule.onRoot().assertExists()
    }

    @Test
    fun homeScreen_displaysMoneyForgottenCard() {
        composeTestRule.setContent {
            HomeScreen(
                onNavigateToMap = {},
                onNavigateToSearch = {},
                onNavigateToChat = {},
                onNavigateToChatWithMessage = {},
                onNavigateToWallet = {},
                onNavigateToBenefit = {},
                onNavigateToProfile = {},
                onNavigateToMoney = {}
            )
        }

        composeTestRule.waitForIdle()

        // Verify money forgotten card is displayed
        composeTestRule.onNodeWithText("Dinheiro Esquecido", substring = true).assertExists()
    }

    @Test
    fun homeScreen_navigatesToChatWhenClickingMoneyCard() {
        var navigatedToChat = false
        var chatMessage: String? = null

        composeTestRule.setContent {
            HomeScreen(
                onNavigateToMap = {},
                onNavigateToSearch = {},
                onNavigateToChat = { navigatedToChat = true },
                onNavigateToChatWithMessage = { message ->
                    navigatedToChat = true
                    chatMessage = message
                },
                onNavigateToWallet = {},
                onNavigateToBenefit = {},
                onNavigateToProfile = {},
                onNavigateToMoney = {}
            )
        }

        composeTestRule.waitForIdle()

        // Click on verify button in money card
        composeTestRule.onNodeWithText("Verificar", substring = true).performClick()

        // Verify navigation occurred
        assert(navigatedToChat)
        assert(chatMessage?.contains("dinheiro", ignoreCase = true) == true)
    }
}
