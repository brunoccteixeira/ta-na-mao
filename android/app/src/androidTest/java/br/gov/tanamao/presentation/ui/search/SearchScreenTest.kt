package br.gov.tanamao.presentation.ui.search

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import br.gov.tanamao.HiltTestActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SearchScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<HiltTestActivity>()

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun searchScreen_displaysSearchField() {
        // Given - SearchScreen is displayed
        composeTestRule.setContent {
            // SearchScreen() // Uncomment when SearchScreen composable is available
        }

        // Then - Search field should be visible
        // composeTestRule.onNodeWithContentDescription("Search").assertIsDisplayed()
    }

    @Test
    fun searchScreen_performsSearch() {
        // Given - SearchScreen is displayed
        composeTestRule.setContent {
            // SearchScreen()
        }

        // When - User types in search field
        // composeTestRule.onNodeWithContentDescription("Search")
        //     .performTextInput("São Paulo")

        // Then - Results should appear after debounce
        // composeTestRule.waitForIdle()
        // composeTestRule.onNodeWithText("São Paulo").assertIsDisplayed()
    }

    @Test
    fun searchScreen_showsLoadingState() {
        // Given - SearchScreen with loading state
        composeTestRule.setContent {
            // SearchScreen(viewModel = viewModelWithLoadingState)
        }

        // Then - Loading indicator should be visible
        // composeTestRule.onNodeWithContentDescription("Loading").assertIsDisplayed()
    }

    @Test
    fun searchScreen_showsEmptyState() {
        // Given - SearchScreen with no results
        composeTestRule.setContent {
            // SearchScreen(viewModel = viewModelWithEmptyResults)
        }

        // Then - Empty state message should be visible
        // composeTestRule.onNodeWithText("Nenhum resultado encontrado").assertIsDisplayed()
    }
}

