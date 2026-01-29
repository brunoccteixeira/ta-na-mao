package br.gov.tanamao.presentation.ui.onboarding

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.TaNaMaoDimens

@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    onSkip: () -> Unit = onComplete
) {
    var currentStep by remember { mutableStateOf(0) }

    val steps = listOf(
        OnboardingStep(
            title = "Bem-vindo ao Tá na Mão",
            description = "Conectamos você aos benefícios sociais que você tem direito",
            icon = Icons.Outlined.AccountBalance
        ),
        OnboardingStep(
            title = "Dinheiro Esquecido",
            description = "R$ 42 bilhões disponíveis em PIS/PASEP, SVR e FGTS",
            icon = Icons.Outlined.Payments
        ),
        OnboardingStep(
            title = "Assistente Inteligente",
            description = "Nosso assistente IA ajuda você a descobrir seus direitos e preparar documentos",
            icon = Icons.Outlined.SmartToy
        ),
        OnboardingStep(
            title = "Pronto para começar!",
            description = "Vamos verificar seus benefícios e dinheiro disponível",
            icon = Icons.Outlined.CheckCircle
        )
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Skip button
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(TaNaMaoDimens.screenPaddingHorizontal)
                    .padding(top = TaNaMaoDimens.spacing4),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(onClick = onSkip) {
                    Text("Pular")
                }
            }

            // Content
            AnimatedContent(
                targetState = currentStep,
                transitionSpec = {
                    fadeIn() + slideInHorizontally { width ->
                        if (targetState > initialState) width else -width
                    } togetherWith fadeOut() + slideOutHorizontally { width ->
                        if (targetState > initialState) -width else width
                    }
                },
                label = "onboarding_step"
            ) { step ->
                OnboardingStepContent(
                    step = steps[step],
                    modifier = Modifier.weight(1f)
                )
            }

            // Indicators
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(TaNaMaoDimens.spacing4),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                steps.forEachIndexed { index, _ ->
                    IndicatorDot(
                        isSelected = index == currentStep,
                        modifier = Modifier.padding(horizontal = TaNaMaoDimens.spacing1)
                    )
                }
            }

            // Navigation buttons
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(TaNaMaoDimens.screenPaddingHorizontal)
                    .padding(bottom = TaNaMaoDimens.spacing4),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                if (currentStep > 0) {
                    OutlinedButton(onClick = { currentStep-- }) {
                        Text("Anterior")
                    }
                } else {
                    Spacer(modifier = Modifier.width(1.dp))
                }

                if (currentStep < steps.size - 1) {
                    PropelButton(
                        text = "Próximo",
                        trailingIcon = Icons.Outlined.ArrowForward,
                        onClick = { currentStep++ },
                        style = PropelButtonStyle.Primary
                    )
                } else {
                    PropelButton(
                        text = "Começar",
                        leadingIcon = Icons.Outlined.Check,
                        onClick = onComplete,
                        style = PropelButtonStyle.Primary
                    )
                }
            }
        }
    }
}

@Composable
private fun OnboardingStepContent(
    step: OnboardingStep,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.screenPaddingHorizontal),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Icon
        Box(
            modifier = Modifier
                .size(120.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.primaryContainer),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = step.icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(64.dp)
            )
        }

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

        // Title
        Text(
            text = step.title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onBackground
        )

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))

        // Description
        Text(
            text = step.description,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun IndicatorDot(
    isSelected: Boolean,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(if (isSelected) 12.dp else 8.dp)
            .clip(CircleShape)
            .background(
                if (isSelected) MaterialTheme.colorScheme.primary
                else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.3f)
            )
    )
}

data class OnboardingStep(
    val title: String,
    val description: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)



