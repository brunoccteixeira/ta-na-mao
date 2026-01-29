package br.gov.tanamao.presentation.navigation

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import br.gov.tanamao.presentation.components.BottomNavDestination
import br.gov.tanamao.presentation.components.PropelBottomNavBar
import br.gov.tanamao.presentation.theme.BackgroundPrimary
import br.gov.tanamao.presentation.ui.alerts.AlertsScreen
import br.gov.tanamao.presentation.ui.chat.ChatScreen
import br.gov.tanamao.presentation.ui.consent.ConsentScreen
import br.gov.tanamao.presentation.ui.details.MunicipalityScreen
import br.gov.tanamao.presentation.ui.home.HomeScreen
import br.gov.tanamao.presentation.ui.map.MapScreen
import br.gov.tanamao.presentation.ui.search.SearchScreen
import br.gov.tanamao.presentation.ui.settings.PrivacySettingsScreen
import br.gov.tanamao.presentation.ui.settings.SettingsScreen
import br.gov.tanamao.presentation.ui.wallet.WalletScreen
import br.gov.tanamao.presentation.ui.money.MoneyScreen
import br.gov.tanamao.presentation.ui.benefit.BenefitDetailScreen
import br.gov.tanamao.presentation.ui.cras.CrasPreparationScreen
import br.gov.tanamao.presentation.ui.profile.ProfileScreen
import br.gov.tanamao.presentation.ui.history.HistoryScreen
import br.gov.tanamao.presentation.ui.onboarding.OnboardingScreen

/**
 * Navigation screens for the app.
 */
sealed class Screen(val route: String) {
    // Main tabs
    object Home : Screen("home")
    object Search : Screen("search")
    object Chat : Screen("chat?initialMessage={initialMessage}") {
        fun createRoute(initialMessage: String? = null): String {
            return if (initialMessage != null) {
                "chat?initialMessage=${java.net.URLEncoder.encode(initialMessage, "UTF-8")}"
            } else {
                "chat"
            }
        }
    }
    object Profile : Screen("profile")

    // Secondary screens
    object Map : Screen("map")
    object Wallet : Screen("wallet")
    object Alerts : Screen("alerts")
    object Consent : Screen("consent")
    object PrivacySettings : Screen("privacy_settings")
    object Settings : Screen("settings")
    object Municipality : Screen("municipality/{ibgeCode}") {
        fun createRoute(ibgeCode: String) = "municipality/$ibgeCode"
    }
    object BenefitDetail : Screen("benefit/{benefitId}") {
        fun createRoute(benefitId: String) = "benefit/$benefitId"
    }
    object Money : Screen("money")
    object CrasPreparation : Screen("cras_preparation/{program}") {
        fun createRoute(program: String) = "cras_preparation/${java.net.URLEncoder.encode(program, "UTF-8")}"
    }
    object History : Screen("history")
    object Onboarding : Screen("onboarding")
}

/**
 * Main tabs that show in bottom navigation
 */
val mainTabs = listOf(
    Screen.Home,
    Screen.Search,
    Screen.Chat,
    Screen.Profile
)

/**
 * Main app scaffold with bottom navigation
 */
@Composable
fun TaNaMaoApp(
    navController: NavHostController = rememberNavController(),
    startDestination: String = Screen.Home.route
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // Determine if we should show bottom nav
    val showBottomNav = currentRoute in mainTabs.map { it.route }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        // Navigation content
        TaNaMaoNavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier.fillMaxSize()
        )

        // Bottom Navigation
        AnimatedVisibility(
            visible = showBottomNav,
            enter = slideInVertically(initialOffsetY = { it }),
            exit = slideOutVertically(targetOffsetY = { it }),
            modifier = Modifier.align(androidx.compose.ui.Alignment.BottomCenter)
        ) {
            PropelBottomNavBar(
                currentRoute = currentRoute ?: Screen.Home.route,
                onNavigate = { destination ->
                    val route = when (destination) {
                        BottomNavDestination.Home -> Screen.Home.route
                        BottomNavDestination.Search -> Screen.Search.route
                        BottomNavDestination.Chat -> Screen.Chat.route
                        BottomNavDestination.Profile -> Screen.Profile.route
                    }
                    navController.navigate(route) {
                        popUpTo(navController.graph.findStartDestination().id) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }
    }
}

/**
 * Navigation host with all routes
 */
@Composable
fun TaNaMaoNavHost(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController(),
    startDestination: String = Screen.Home.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier,
        enterTransition = {
            fadeIn(animationSpec = tween(200)) +
                    slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Start, tween(300))
        },
        exitTransition = {
            fadeOut(animationSpec = tween(200)) +
                    slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Start, tween(300))
        },
        popEnterTransition = {
            fadeIn(animationSpec = tween(200)) +
                    slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.End, tween(300))
        },
        popExitTransition = {
            fadeOut(animationSpec = tween(200)) +
                    slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.End, tween(300))
        }
    ) {
        // Main Tabs
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToMap = { navController.navigate(Screen.Map.route) },
                onNavigateToSearch = { navController.navigate(Screen.Search.route) },
                onNavigateToChat = { navController.navigate(Screen.Chat.createRoute()) },
                onNavigateToChatWithMessage = { message ->
                    navController.navigate(Screen.Chat.createRoute(message))
                },
                onNavigateToWallet = { navController.navigate(Screen.Wallet.route) },
                onNavigateToBenefit = { id -> navController.navigate(Screen.BenefitDetail.createRoute(id)) },
                onNavigateToProfile = { navController.navigate(Screen.Profile.route) },
                onNavigateToMoney = { navController.navigate(Screen.Money.route) }
            )
        }

        composable(Screen.Search.route) {
            SearchScreen(
                onNavigateToMunicipality = { ibgeCode ->
                    navController.navigate(Screen.Municipality.createRoute(ibgeCode))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(
            route = "chat?initialMessage={initialMessage}",
            arguments = listOf(
                navArgument("initialMessage") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val initialMessage = backStackEntry.arguments?.getString("initialMessage")?.let {
                java.net.URLDecoder.decode(it, "UTF-8")
            }
            ChatScreen(
                onNavigateBack = { navController.popBackStack() },
                initialMessage = initialMessage
            )
        }

        composable(Screen.Profile.route) {
            ProfileScreen(
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) },
                onNavigateToPrivacy = { navController.navigate(Screen.PrivacySettings.route) },
                onNavigateToWallet = { navController.navigate(Screen.Wallet.route) },
                onNavigateToHistory = { navController.navigate(Screen.History.route) },
                onNavigateToMoney = { navController.navigate(Screen.Money.route) },
                onNavigateToChat = { message ->
                    navController.navigate(Screen.Chat.createRoute(message))
                }
            )
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // Secondary Screens
        composable(Screen.Map.route) {
            MapScreen(
                onNavigateToMunicipality = { ibgeCode ->
                    navController.navigate(Screen.Municipality.createRoute(ibgeCode))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Wallet.route) {
            WalletScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToBenefit = { id -> navController.navigate(Screen.BenefitDetail.createRoute(id)) },
                onNavigateToChat = { navController.navigate(Screen.Chat.route) }
            )
        }

        composable(Screen.Money.route) {
            MoneyScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToChat = { message ->
                    navController.navigate(Screen.Chat.createRoute(message))
                }
            )
        }

        composable(
            route = Screen.CrasPreparation.route,
            arguments = listOf(
                navArgument("program") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val program = backStackEntry.arguments?.getString("program")?.let {
                java.net.URLDecoder.decode(it, "UTF-8")
            } ?: return@composable
            CrasPreparationScreen(
                program = program,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Alerts.route) {
            AlertsScreen(
                onNavigateBack = { navController.popBackStack() },
                onAlertClick = { /* Handle alert click */ }
            )
        }

        composable(Screen.Consent.route) {
            ConsentScreen(
                onAccept = { navController.navigate(Screen.Home.route) },
                onDecline = { /* Handle decline */ }
            )
        }

        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = { navController.navigate(Screen.Home.route) },
                onSkip = { navController.navigate(Screen.Home.route) }
            )
        }

        composable(Screen.PrivacySettings.route) {
            PrivacySettingsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Screen.History.route) {
            HistoryScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.Municipality.route,
            arguments = listOf(
                navArgument("ibgeCode") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val ibgeCode = backStackEntry.arguments?.getString("ibgeCode") ?: return@composable
            MunicipalityScreen(
                ibgeCode = ibgeCode,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.BenefitDetail.route,
            arguments = listOf(
                navArgument("benefitId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val benefitId = backStackEntry.arguments?.getString("benefitId") ?: return@composable
            BenefitDetailScreen(
                benefitId = benefitId,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToChat = { message ->
                    navController.navigate(Screen.Chat.createRoute(message))
                },
                onNavigateToCras = { program ->
                    navController.navigate(Screen.CrasPreparation.createRoute(program))
                }
            )
        }
    }
}
