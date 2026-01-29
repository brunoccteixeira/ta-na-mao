package br.gov.tanamao.presentation.ui.search

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.*
import br.gov.tanamao.presentation.util.formatNumber

@Composable
fun SearchScreen(
    onNavigateToMunicipality: (String) -> Unit,
    onNavigateBack: () -> Unit,
    viewModel: SearchViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            SearchTopBar(onNavigateBack = onNavigateBack)

            // Search Field
            SearchInputField(
                query = uiState.query,
                onQueryChange = viewModel::onQueryChange,
                isLoading = uiState.isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
            )

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))

            // Results count
            AnimatedVisibility(
                visible = uiState.results.isNotEmpty(),
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Text(
                    text = "${uiState.results.size} municípios encontrados",
                    style = MaterialTheme.typography.labelMedium,
                    color = TextTertiary,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))

            // Results
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                    vertical = TaNaMaoDimens.spacing2
                ),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                items(
                    items = uiState.results,
                    key = { it.ibgeCode }
                ) { result ->
                    MunicipalitySearchCard(
                        name = result.name,
                        stateAbbreviation = result.stateAbbreviation,
                        ibgeCode = result.ibgeCode,
                        population = result.population,
                        onClick = { onNavigateToMunicipality(result.ibgeCode) }
                    )
                }

                // Empty state
                if (uiState.results.isEmpty() && uiState.query.length >= 2 && !uiState.isLoading) {
                    item {
                        EmptySearchState(query = uiState.query)
                    }
                }

                // Initial hint
                if (uiState.query.length < 2 && uiState.results.isEmpty()) {
                    item {
                        SearchHintState()
                    }
                }

                item {
                    Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight))
                }
            }
        }

        // Loading overlay
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 200.dp)
            ) {
                CircularProgressIndicator(
                    color = AccentOrange,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }
}

@Composable
private fun SearchTopBar(onNavigateBack: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(horizontal = TaNaMaoDimens.spacing2)
            .padding(vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
        verticalAlignment = Alignment.CenterVertically
    ) {
        PropelIconButton(
            icon = Icons.Outlined.ArrowBack,
            onClick = onNavigateBack,
            style = PropelButtonStyle.Ghost
        )

        Text(
            text = "Buscar Município",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )
    }
}

@Composable
private fun SearchInputField(
    query: String,
    onQueryChange: (String) -> Unit,
    isLoading: Boolean,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier,
        placeholder = {
            Text(
                text = "Digite o nome do município...",
                color = TextTertiary
            )
        },
        leadingIcon = {
            Icon(
                imageVector = Icons.Outlined.Search,
                contentDescription = null,
                tint = if (query.isNotEmpty()) AccentOrange else TextTertiary
            )
        },
        trailingIcon = {
            AnimatedVisibility(
                visible = query.isNotEmpty(),
                enter = fadeIn(),
                exit = fadeOut()
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = AccentOrange,
                        strokeWidth = 2.dp
                    )
                } else {
                    PropelIconButton(
                        icon = Icons.Outlined.Clear,
                        onClick = { onQueryChange("") },
                        style = PropelButtonStyle.Ghost,
                        size = 36.dp
                    )
                }
            }
        },
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = BackgroundInput,
            unfocusedContainerColor = BackgroundTertiary,
            focusedBorderColor = AccentOrange,
            unfocusedBorderColor = Color.Transparent,
            cursorColor = AccentOrange,
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary
        ),
        shape = RoundedCornerShape(TaNaMaoDimens.cardRadius),
        singleLine = true
    )
}

@Composable
private fun MunicipalitySearchCard(
    name: String,
    stateAbbreviation: String,
    ibgeCode: String,
    population: Int?,
    onClick: () -> Unit
) {
    PropelCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick,
        elevation = PropelCardElevation.Standard
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // State badge
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(AccentOrangeSubtle),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = stateAbbreviation,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = AccentOrange
                    )
                }

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = name,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "IBGE: $ibgeCode",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextTertiary
                        )

                        population?.let { pop ->
                            Text(
                                text = "•",
                                color = TextTertiary
                            )
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.People,
                                    contentDescription = null,
                                    tint = TextTertiary,
                                    modifier = Modifier.size(14.dp)
                                )
                                Text(
                                    text = pop.formatNumber(),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextSecondary
                                )
                            }
                        }
                    }
                }
            }

            Icon(
                imageVector = Icons.Outlined.ChevronRight,
                contentDescription = "Ver detalhes",
                tint = TextTertiary,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

@Composable
private fun EmptySearchState(query: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.spacing6),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(BackgroundTertiary),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Outlined.SearchOff,
                contentDescription = null,
                tint = TextTertiary,
                modifier = Modifier.size(32.dp)
            )
        }

        Text(
            text = "Nenhum município encontrado",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimary
        )

        Text(
            text = "Não encontramos resultados para \"$query\". Tente outro termo.",
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary
        )
    }
}

@Composable
private fun SearchHintState() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.spacing6),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(AccentOrangeSubtle),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Outlined.Search,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(32.dp)
            )
        }

        Text(
            text = "Busque por município",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimary
        )

        Text(
            text = "Digite pelo menos 2 caracteres para ver os resultados",
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary
        )
    }
}
