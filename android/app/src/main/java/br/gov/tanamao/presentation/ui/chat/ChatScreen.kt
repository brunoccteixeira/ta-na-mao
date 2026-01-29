package br.gov.tanamao.presentation.ui.chat

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.components.chat.*
import br.gov.tanamao.presentation.theme.StatusActive
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.util.ImageUtils
import java.io.File

@Composable
fun ChatScreen(
    onNavigateBack: () -> Unit,
    initialMessage: String? = null,
    viewModel: ChatViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()

    // Enviar mensagem inicial quando a tela abrir
    LaunchedEffect(initialMessage) {
        if (!initialMessage.isNullOrBlank()) {
            viewModel.sendMessage(initialMessage)
        }
    }

    var inputText by remember { mutableStateOf("") }
    val focusManager = LocalFocusManager.current
    val focusRequester = remember { FocusRequester() }
    val keyboardController = LocalSoftwareKeyboardController.current

    // Image picker state
    var showImagePicker by remember { mutableStateOf(false) }
    var selectedImageBase64 by remember { mutableStateOf<String?>(null) }
    var cameraImageUri by remember { mutableStateOf<Uri?>(null) }

    // Camera launcher
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        if (success && cameraImageUri != null) {
            selectedImageBase64 = ImageUtils.processImageForUpload(context, cameraImageUri!!)
        }
    }

    // Gallery launcher
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            selectedImageBase64 = ImageUtils.processImageForUpload(context, it)
        }
    }

    // Permission launcher
    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Create temp file and launch camera
            val photoFile = File.createTempFile("prescription_", ".jpg", context.cacheDir)
            cameraImageUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                photoFile
            )
            cameraLauncher.launch(cameraImageUri)
        }
    }

    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(uiState.messages.size) {
        if (uiState.messages.isNotEmpty()) {
            listState.animateScrollToItem(uiState.messages.size - 1)
        }
    }

    // Auto-focus on input field and show keyboard when not loading
    LaunchedEffect(uiState.isLoading) {
        if (!uiState.isLoading && uiState.messages.isNotEmpty()) {
            kotlinx.coroutines.delay(300) // Small delay for UI to settle
            try {
                focusRequester.requestFocus()
                keyboardController?.show()
            } catch (_: Exception) {
                // Focus request may fail if component is not ready
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .imePadding() // Adjust layout when keyboard opens
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            ChatTopBar(
                onNavigateBack = onNavigateBack,
                onClearChat = viewModel::clearConversation
            )

            // Messages
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                state = listState,
                contentPadding = PaddingValues(
                    horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                    vertical = TaNaMaoDimens.spacing3
                ),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                items(
                    items = uiState.messages,
                    key = { it.id }
                ) { message ->
                    MessageBubble(
                        message = message,
                        onQuickReplyClick = { option ->
                            // Intercepta ação de upload de receita para abrir image picker
                            if (option.value == "upload_prescription") {
                                showImagePicker = true
                            } else {
                                viewModel.handleQuickReply(option)
                            }
                        },
                        onEligibilityAction = viewModel::handleEligibilityAction
                    )
                }

                // Loading indicator
                if (uiState.isLoading) {
                    item {
                        MessageBubble(
                            message = ChatMessage(
                                content = "",
                                sender = MessageSender.ASSISTANT,
                                type = MessageType.LOADING
                            )
                        )
                    }
                }
            }

            // Image preview (if selected)
            AnimatedVisibility(
                visible = selectedImageBase64 != null,
                enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
                exit = slideOutVertically(targetOffsetY = { it }) + fadeOut()
            ) {
                ImagePreviewBar(
                    imageBase64 = selectedImageBase64,
                    onRemove = { selectedImageBase64 = null }
                )
            }

            // Input area
            ChatInputBar(
                text = inputText,
                onTextChange = { inputText = it },
                onSend = {
                    if (selectedImageBase64 != null) {
                        // Send image
                        viewModel.sendImageMessage(selectedImageBase64!!)
                        selectedImageBase64 = null
                        inputText = ""
                    } else if (inputText.isNotBlank()) {
                        // Send text
                        viewModel.sendMessage(inputText)
                        inputText = ""
                    }
                    focusManager.clearFocus()
                },
                onAttachClick = { showImagePicker = true },
                isLoading = uiState.isLoading,
                hasImage = selectedImageBase64 != null,
                focusRequester = focusRequester
            )
        }
    }

    // Image picker bottom sheet
    if (showImagePicker) {
        ImagePickerSheet(
            onDismiss = { showImagePicker = false },
            onCameraClick = {
                // Check camera permission
                if (ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA)
                    == PackageManager.PERMISSION_GRANTED
                ) {
                    val photoFile = File.createTempFile("prescription_", ".jpg", context.cacheDir)
                    cameraImageUri = FileProvider.getUriForFile(
                        context,
                        "${context.packageName}.fileprovider",
                        photoFile
                    )
                    cameraLauncher.launch(cameraImageUri)
                } else {
                    cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                }
            },
            onGalleryClick = {
                galleryLauncher.launch("image/*")
            }
        )
    }
}

@Composable
private fun ChatTopBar(
    onNavigateBack: () -> Unit,
    onClearChat: () -> Unit
) {
    var showMenu by remember { mutableStateOf(false) }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(horizontal = TaNaMaoDimens.spacing2)
            .padding(vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        PropelIconButton(
            icon = Icons.Outlined.ArrowBack,
            onClick = onNavigateBack,
            style = PropelButtonStyle.Ghost
        )

        // Title and status
        Row(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Filled.SmartToy,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
            }

            Column {
                Text(
                    text = "Assistente Tá na Mão",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Row(
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(StatusActive)
                    )
                    Text(
                        text = "Online",
                        style = MaterialTheme.typography.labelSmall,
                        color = StatusActive
                    )
                }
            }
        }

        // Menu
        Box {
            PropelIconButton(
                icon = Icons.Outlined.MoreVert,
                onClick = { showMenu = true },
                style = PropelButtonStyle.Ghost
            )

            DropdownMenu(
                expanded = showMenu,
                onDismissRequest = { showMenu = false },
                modifier = Modifier.background(MaterialTheme.colorScheme.surface)
            ) {
                DropdownMenuItem(
                    text = { Text("Limpar conversa", color = MaterialTheme.colorScheme.onSurface) },
                    onClick = {
                        onClearChat()
                        showMenu = false
                    },
                    leadingIcon = {
                        Icon(
                            Icons.Outlined.Delete,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                )
            }
        }
    }
}

@Composable
private fun ChatInputBar(
    text: String,
    onTextChange: (String) -> Unit,
    onSend: () -> Unit,
    onAttachClick: () -> Unit,
    isLoading: Boolean,
    hasImage: Boolean,
    focusRequester: FocusRequester
) {
    val canSend = (text.isNotBlank() || hasImage) && !isLoading

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(
                horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                vertical = TaNaMaoDimens.spacing3
            ),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.Bottom
    ) {
        // Attachment button
        AttachmentButton(
            onClick = onAttachClick
        )

        // Text field
        OutlinedTextField(
            value = text,
            onValueChange = onTextChange,
            modifier = Modifier
                .weight(1f)
                .focusRequester(focusRequester),
            placeholder = {
                Text(
                    text = if (hasImage) "Adicionar legenda..." else "Digite sua mensagem...",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            },
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = MaterialTheme.colorScheme.surface,
                unfocusedContainerColor = MaterialTheme.colorScheme.surface,
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = Color.Transparent,
                cursorColor = MaterialTheme.colorScheme.primary,
                focusedTextColor = MaterialTheme.colorScheme.onSurface,
                unfocusedTextColor = MaterialTheme.colorScheme.onSurface
            ),
            shape = RoundedCornerShape(24.dp),
            keyboardOptions = KeyboardOptions(
                imeAction = ImeAction.Send
            ),
            keyboardActions = KeyboardActions(
                onSend = { if (canSend) onSend() }
            ),
            maxLines = 4,
            enabled = !isLoading
        )

        // Send button
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
                .background(
                    if (canSend) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant
                )
                .then(
                    if (canSend) {
                        Modifier.clickable(onClick = onSend)
                    } else Modifier
                ),
            contentAlignment = Alignment.Center
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    strokeWidth = 2.dp
                )
            } else {
                Icon(
                    imageVector = if (hasImage) Icons.Filled.Image else Icons.Filled.Send,
                    contentDescription = "Enviar",
                    tint = if (canSend) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}

/**
 * Suggested actions bar (can be shown above input)
 */
@Composable
fun SuggestedActionsBar(
    suggestions: List<String>,
    onSuggestionClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    AnimatedVisibility(
        visible = suggestions.isNotEmpty(),
        enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { it }) + fadeOut()
    ) {
        Row(
            modifier = modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(
                    horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                    vertical = TaNaMaoDimens.spacing2
                ),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            suggestions.take(3).forEach { suggestion ->
                SuggestionChip(
                    text = suggestion,
                    onClick = { onSuggestionClick(suggestion) }
                )
            }
        }
    }
}

@Composable
private fun SuggestionChip(
    text: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
            .background(MaterialTheme.colorScheme.surface)
            .padding(
                horizontal = TaNaMaoDimens.spacing3,
                vertical = TaNaMaoDimens.spacing2
            )
            .clickable(onClick = onClick)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
