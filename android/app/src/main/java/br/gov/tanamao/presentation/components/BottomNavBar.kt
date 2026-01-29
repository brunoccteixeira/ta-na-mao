package br.gov.tanamao.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*

/**
 * Navigation destinations for bottom nav
 */
enum class BottomNavDestination(
    val route: String,
    val label: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    Home(
        route = "home",
        label = "Início",
        selectedIcon = Icons.Filled.Home,
        unselectedIcon = Icons.Outlined.Home
    ),
    Search(
        route = "search",
        label = "Buscar",
        selectedIcon = Icons.Filled.Search,
        unselectedIcon = Icons.Outlined.Search
    ),
    Chat(
        route = "chat",
        label = "Assistente",
        selectedIcon = Icons.Filled.Chat,
        unselectedIcon = Icons.Outlined.Chat
    ),
    Profile(
        route = "profile",
        label = "Perfil",
        selectedIcon = Icons.Filled.Person,
        unselectedIcon = Icons.Outlined.Person
    )
}

/**
 * Propel-styled bottom navigation bar
 *
 * Design:
 * - Dark background matching app theme
 * - Orange accent for selected item
 * - Subtle icons with labels
 * - Smooth animations on selection
 */
@Composable
fun PropelBottomNavBar(
    currentRoute: String,
    onNavigate: (BottomNavDestination) -> Unit,
    modifier: Modifier = Modifier,
    showLabels: Boolean = true
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(TaNaMaoDimens.bottomNavHeight + 16.dp) // Extra for safe area
            .background(BackgroundSecondary)
    ) {
        // Top border
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(Divider)
        )

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(TaNaMaoDimens.bottomNavHeight)
                .padding(horizontal = TaNaMaoDimens.spacing2),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            BottomNavDestination.entries.forEach { destination ->
                val isSelected = currentRoute == destination.route

                BottomNavItem(
                    destination = destination,
                    isSelected = isSelected,
                    showLabel = showLabels,
                    onClick = { onNavigate(destination) },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun BottomNavItem(
    destination: BottomNavDestination,
    isSelected: Boolean,
    showLabel: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }

    val scale by animateFloatAsState(
        targetValue = if (isSelected) 1f else 0.95f,
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "nav_scale"
    )

    val iconColor by animateColorAsState(
        targetValue = if (isSelected) AccentOrange else TextTertiary,
        label = "nav_icon_color"
    )

    val labelColor by animateColorAsState(
        targetValue = if (isSelected) AccentOrange else TextTertiary,
        label = "nav_label_color"
    )

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = onClick
            )
            .padding(vertical = TaNaMaoDimens.spacing2)
            .scale(scale),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Selection indicator
        Box(
            modifier = Modifier
                .width(32.dp)
                .height(3.dp)
                .clip(RoundedCornerShape(1.5.dp))
                .background(
                    if (isSelected) AccentOrange else androidx.compose.ui.graphics.Color.Transparent
                )
        )

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))

        // Icon
        Icon(
            imageVector = if (isSelected) destination.selectedIcon else destination.unselectedIcon,
            contentDescription = destination.label,
            tint = iconColor,
            modifier = Modifier.size(TaNaMaoDimens.bottomNavIconSize)
        )

        // Label
        if (showLabel) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = destination.label,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                color = labelColor
            )
        }
    }
}

/**
 * Compact bottom nav (icons only)
 */
@Composable
fun PropelBottomNavBarCompact(
    currentRoute: String,
    onNavigate: (BottomNavDestination) -> Unit,
    modifier: Modifier = Modifier
) {
    PropelBottomNavBar(
        currentRoute = currentRoute,
        onNavigate = onNavigate,
        modifier = modifier,
        showLabels = false
    )
}

/**
 * Bottom nav with notification badge
 */
@Composable
fun PropelBottomNavBarWithBadge(
    currentRoute: String,
    onNavigate: (BottomNavDestination) -> Unit,
    badges: Map<BottomNavDestination, Int>,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(TaNaMaoDimens.bottomNavHeight + 16.dp)
            .background(BackgroundSecondary)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(Divider)
        )

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(TaNaMaoDimens.bottomNavHeight)
                .padding(horizontal = TaNaMaoDimens.spacing2),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            BottomNavDestination.entries.forEach { destination ->
                val isSelected = currentRoute == destination.route
                val badgeCount = badges[destination] ?: 0

                BottomNavItemWithBadge(
                    destination = destination,
                    isSelected = isSelected,
                    badgeCount = badgeCount,
                    onClick = { onNavigate(destination) },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun BottomNavItemWithBadge(
    destination: BottomNavDestination,
    isSelected: Boolean,
    badgeCount: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val iconColor by animateColorAsState(
        targetValue = if (isSelected) AccentOrange else TextTertiary,
        label = "nav_icon_color"
    )

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(vertical = TaNaMaoDimens.spacing2),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box {
            Icon(
                imageVector = if (isSelected) destination.selectedIcon else destination.unselectedIcon,
                contentDescription = destination.label,
                tint = iconColor,
                modifier = Modifier.size(TaNaMaoDimens.bottomNavIconSize)
            )

            if (badgeCount > 0) {
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .offset(x = 6.dp, y = (-4).dp)
                        .size(if (badgeCount > 9) 20.dp else 16.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(AccentOrange),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (badgeCount > 99) "99+" else badgeCount.toString(),
                        style = TaNaMaoTextStyles.badge,
                        color = TextOnAccent
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = destination.label,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
            color = iconColor
        )
    }
}
