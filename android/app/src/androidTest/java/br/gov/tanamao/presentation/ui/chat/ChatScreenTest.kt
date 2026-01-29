package br.gov.tanamao.presentation.ui.chat

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ChatScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun chatScreen_displaysWelcomeMessage() {
        composeTestRule.setContent {
            ChatScreen(
                onNavigateBack = {}
            )
        }

        composeTestRule.waitForIdle()

        // Verify chat screen is displayed
        composeTestRule.onRoot().assertExists()
    }

    @Test
    fun chatScreen_displaysQuickReplies() {
        composeTestRule.setContent {
            ChatScreen(
                onNavigateBack = {}
            )
        }

        composeTestRule.waitForIdle()

        // Verify quick replies are displayed (at least one)
        composeTestRule.onAllNodesWithContentDescription("Quick reply", substring = true)
            .onFirst()
            .assertExists()
    }

    @Test
    fun chatScreen_canSendMessage() {
        composeTestRule.setContent {
            ChatScreen(
                onNavigateBack = {}
            )
        }

        composeTestRule.waitForIdle()

        // Find text input
        val textInput = composeTestRule.onNodeWithContentDescription("Message input", substring = true)
        textInput.assertExists()

        // Type message
        textInput.performTextInput("teste")

        // Verify text was entered
        textInput.assertTextContains("teste")
    }
}



