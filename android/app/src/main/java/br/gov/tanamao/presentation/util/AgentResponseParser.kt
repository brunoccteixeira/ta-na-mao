package br.gov.tanamao.presentation.util

import br.gov.tanamao.domain.model.*
import java.time.LocalDate
import java.util.regex.Pattern

/**
 * Utility class for parsing structured data from agent responses
 */
object AgentResponseParser {

    /**
     * Convert Brazilian currency string to Double
     * Handles formats like "R$ 1.234,56" or "1.234,56"
     */
    fun parseBrazilianCurrency(valueStr: String?): Double? {
        if (valueStr == null) return null
        return valueStr
            .replace("R$", "")
            .replace(" ", "")
            .trim()
            .replace(".", "") // Remove thousands separator
            .replace(",", ".") // Replace decimal comma with dot
            .toDoubleOrNull()
    }

    /**
     * Parse money check result from agent response
     */
    fun parseMoneyCheckResult(response: String, toolsUsed: List<String>): MoneyCheckResult? {
        if (!toolsUsed.contains("consultar_dinheiro_esquecido") &&
            !response.contains("dinheiro", ignoreCase = true) &&
            !response.contains("PIS", ignoreCase = true) &&
            !response.contains("SVR", ignoreCase = true) &&
            !response.contains("FGTS", ignoreCase = true)
        ) {
            return null
        }

        val hasMoney = response.contains("tem dinheiro", ignoreCase = true) ||
                response.contains("disponível", ignoreCase = true) ||
                response.contains("valor", ignoreCase = true) ||
                response.contains("R$", ignoreCase = true)

        // Extract total amount - improved patterns
        val totalAmount = extractTotalAmount(response)

        // Extract money types
        val types = mutableListOf<MoneyTypeResult>()
        
        // Check for PIS/PASEP - improved extraction
            val pisAmount = extractAmountForType(response, "PIS|PASEP")
        if (pisAmount != null || response.contains("PIS", ignoreCase = true) || response.contains("PASEP", ignoreCase = true)) {
            val deadline = extractDeadline(response, "PIS|PASEP")
            types.add(
                MoneyTypeResult(
                    type = "PIS_PASEP",
                    hasMoney = pisAmount != null && pisAmount > 0,
                    amount = pisAmount,
                    status = when {
                        pisAmount != null && pisAmount > 0 -> "Disponível"
                        deadline != null -> "Verificar (prazo: $deadline)"
                        else -> "Não encontrado"
                    },
                    nextSteps = listOf("Acesse o site da Caixa ou Banco do Brasil", "Use o app Repis Cidadão")
                )
            )
        }

        // Check for SVR - improved extraction
        val svrAmount = extractAmountForType(response, "SVR|Valores a Receber|Valores a receber")
        if (svrAmount != null || response.contains("SVR", ignoreCase = true) || response.contains("Valores a Receber", ignoreCase = true)) {
            types.add(
                MoneyTypeResult(
                    type = "SVR",
                    hasMoney = svrAmount != null && svrAmount > 0,
                    amount = svrAmount,
                    status = if (svrAmount != null && svrAmount > 0) "Disponível" else "Verificar",
                    nextSteps = listOf("Acesse o site do Banco Central", "Ative resgate automático via Pix")
                )
            )
        }

        // Check for FGTS - improved extraction
            val fgtsAmount = extractAmountForType(response, "FGTS")
        if (fgtsAmount != null || response.contains("FGTS", ignoreCase = true)) {
            val deadline = extractDeadline(response, "FGTS")
            types.add(
                MoneyTypeResult(
                    type = "FGTS",
                    hasMoney = fgtsAmount != null && fgtsAmount > 0,
                    amount = fgtsAmount,
                    status = when {
                        fgtsAmount != null && fgtsAmount > 0 -> "Disponível"
                        deadline != null -> "Verificar (prazo: $deadline)"
                        else -> "Não encontrado"
                    },
                    nextSteps = listOf("Acesse o app FGTS ou site da Caixa", "Verifique saque-aniversário até 30/12/2025")
                )
            )
        }

        // Extract URLs/links if mentioned
        val links = extractLinks(response)

        return MoneyCheckResult(
            hasMoney = hasMoney,
            totalAmount = totalAmount,
            types = types,
            message = response
        )
    }
    
    /**
     * Extract total amount from response - improved
     */
    private fun extractTotalAmount(response: String): Double? {
        val patterns = listOf(
            Pattern.compile("""total[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""soma[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE)
        )
        
        for (pattern in patterns) {
            val matcher = pattern.matcher(response)
            if (matcher.find()) {
                val valueStr = matcher.group(1)
                val value = parseBrazilianCurrency(valueStr)
                if (value != null && value > 0) {
                    return value
                }
            }
        }
        
        return null
    }
    
    /**
     * Extract deadline/expiration date for a money type
     */
    private fun extractDeadline(response: String, typePattern: String): String? {
        val pattern = Pattern.compile(
            """$typePattern[^.]*(?:prazo|até|deadline|expira)[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})""",
            Pattern.CASE_INSENSITIVE
        )
        val matcher = pattern.matcher(response)
        if (matcher.find()) {
            return matcher.group(1)
        }
        return null
    }
    
    /**
     * Extract URLs/links from response
     */
    private fun extractLinks(response: String): List<String> {
        val links = mutableListOf<String>()
        val urlPattern = Pattern.compile("""https?://[^\s]+""")
        val matcher = urlPattern.matcher(response)
        while (matcher.find()) {
            links.add(matcher.group())
        }
        return links
    }

    /**
     * Parse CRAS preparation from agent response
     */
    fun parseCrasPreparation(response: String, program: String): CrasPreparation? {
        if (!response.contains("CRAS", ignoreCase = true) &&
            !response.contains("checklist", ignoreCase = true) &&
            !response.contains("documento", ignoreCase = true)
        ) {
            return null
        }

        // Extract documents from response
        val documents = extractDocuments(response)
        
        // Extract estimated time
        val timePattern = Pattern.compile("(\\d+)\\s*(?:min|minuto)", Pattern.CASE_INSENSITIVE)
        val timeMatcher = timePattern.matcher(response)
        val estimatedTime = if (timeMatcher.find()) {
            timeMatcher.group(1)?.toIntOrNull() ?: 30
        } else 30

        // Extract tips
        val tips = extractTips(response)

        return CrasPreparation(
            program = program,
            checklist = DocumentChecklist(
                title = "Documentos necessários para $program",
                documents = documents,
                totalDocuments = documents.size,
                estimatedTime = estimatedTime
            ),
            estimatedTime = estimatedTime,
            tips = tips
        )
    }

    /**
     * Parse user benefits from meus_dados response
     */
    fun parseUserBenefits(response: String): List<UserBenefit> {
        val benefits = mutableListOf<UserBenefit>()
        
        // Pattern for benefits with values - improved to catch more variations
        val benefitPattern = Pattern.compile(
            """(Bolsa\s+Família|BPC|LOAS|Farmácia\s+Popular|TSEE|Tarifa\s+Social|Auxílio\s+Brasil|Dignidade\s+Menstrual)[:\s]+(?:R\$\s*)?([\d.,]+)?""",
            Pattern.CASE_INSENSITIVE
        )
        val matcher = benefitPattern.matcher(response)
        
        while (matcher.find()) {
            val name = matcher.group(1) ?: continue
            val valueStr = matcher.group(2)
            val value = parseBrazilianCurrency(valueStr)
            
            val programCode = when {
                name.contains("Bolsa", ignoreCase = true) || name.contains("Auxílio Brasil", ignoreCase = true) -> "BOLSA_FAMILIA"
                name.contains("BPC", ignoreCase = true) || name.contains("LOAS", ignoreCase = true) -> "BPC"
                name.contains("Farmácia", ignoreCase = true) -> "FARMACIA_POPULAR"
                name.contains("TSEE", ignoreCase = true) || name.contains("Tarifa", ignoreCase = true) -> "TSEE"
                name.contains("Dignidade", ignoreCase = true) -> "DIGNIDADE_MENSTRUAL"
                else -> null
            }
            
            if (programCode != null) {
                // Extract status from context around the benefit
                val contextStart = maxOf(0, matcher.start() - 100)
                val contextEnd = minOf(response.length, matcher.end() + 100)
                val context = response.substring(contextStart, contextEnd)
                
                val status = extractBenefitStatus(context, name)
                val (lastPayment, nextPayment) = extractPaymentDates(response, name)
                
                benefits.add(
                    UserBenefit(
                        id = programCode,
                        programCode = programCode,
                        programName = name.trim(),
                        status = status,
                        monthlyValue = value,
                        lastPaymentDate = lastPayment,
                        nextPaymentDate = nextPayment
                    )
                )
            }
        }
        
        return benefits
    }
    
    /**
     * Extract user name from response
     */
    fun extractUserName(response: String): String? {
        val patterns = listOf(
            Pattern.compile("""(?:Olá|Oi|Olá,|Bem-vindo,|Seus dados,)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""nome[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""usuário[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)""", Pattern.CASE_INSENSITIVE)
        )
        
        for (pattern in patterns) {
            val matcher = pattern.matcher(response)
            if (matcher.find()) {
                val name = matcher.group(1)?.trim()
                if (name != null && name.length > 1 && name.length < 50) {
                    return name
                }
            }
        }
        
        return null
    }
    
    /**
     * Extract total received amount from response
     */
    fun extractTotalReceived(response: String): Double? {
        val patterns = listOf(
            Pattern.compile("""total[:\s]+(?:recebido|já recebeu|recebeu)[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""total[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""soma[:\s]+total[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE),
            Pattern.compile("""você[:\s]+já[:\s]+recebeu[:\s]+R\$\s*([\d.,]+)""", Pattern.CASE_INSENSITIVE)
        )
        
        for (pattern in patterns) {
            val matcher = pattern.matcher(response)
            if (matcher.find()) {
                val valueStr = matcher.group(1)
                val value = parseBrazilianCurrency(valueStr)
                if (value != null && value > 0) {
                    return value
                }
            }
        }
        
        return null
    }
    
    /**
     * Extract payment dates for a specific program
     */
    fun extractPaymentDates(response: String, programName: String): Pair<LocalDate?, LocalDate?> {
        // Find context around the program name
        val programIndex = response.indexOf(programName, ignoreCase = true)
        if (programIndex == -1) return Pair(null, null)
        
        val contextStart = maxOf(0, programIndex - 200)
        val contextEnd = minOf(response.length, programIndex + programName.length + 200)
        val context = response.substring(contextStart, contextEnd)
        
        var lastPayment: LocalDate? = null
        var nextPayment: LocalDate? = null
        
        // Pattern for dates: DD/MM/YYYY or DD/MM/YY
        val datePattern = Pattern.compile("""(\d{1,2})/(\d{1,2})/(\d{2,4})""")
        
        // Look for "último pagamento" or "last payment"
        val lastPaymentPattern = Pattern.compile("""(?:último|last)[:\s]+(?:pagamento|payment)[:\s]+(\d{1,2})/(\d{1,2})/(\d{2,4})""", Pattern.CASE_INSENSITIVE)
        val lastMatcher = lastPaymentPattern.matcher(context)
        if (lastMatcher.find()) {
            lastPayment = parseDate(lastMatcher.group(1), lastMatcher.group(2), lastMatcher.group(3))
        }
        
        // Look for "próximo pagamento" or "next payment"
        val nextPaymentPattern = Pattern.compile("""(?:próximo|next)[:\s]+(?:pagamento|payment)[:\s]+(\d{1,2})/(\d{1,2})/(\d{2,4})""", Pattern.CASE_INSENSITIVE)
        val nextMatcher = nextPaymentPattern.matcher(context)
        if (nextMatcher.find()) {
            nextPayment = parseDate(nextMatcher.group(1), nextMatcher.group(2), nextMatcher.group(3))
        }
        
        // If not found with keywords, try to find dates near the program name
        if (lastPayment == null && nextPayment == null) {
            val dateMatcher = datePattern.matcher(context)
            val dates = mutableListOf<LocalDate>()
            while (dateMatcher.find() && dates.size < 2) {
                val date = parseDate(dateMatcher.group(1), dateMatcher.group(2), dateMatcher.group(3))
                if (date != null) {
                    dates.add(date)
                }
            }
            if (dates.size == 2) {
                dates.sort()
                lastPayment = dates[0]
                nextPayment = dates[1]
            } else if (dates.size == 1) {
                // Assume it's next payment if it's in the future
                if (dates[0].isAfter(LocalDate.now())) {
                    nextPayment = dates[0]
                } else {
                    lastPayment = dates[0]
                }
            }
        }
        
        return Pair(lastPayment, nextPayment)
    }
    
    /**
     * Extract benefit status from context
     */
    private fun extractBenefitStatus(context: String, programName: String): BenefitStatus {
        val lowerContext = context.lowercase()
        
        return when {
            lowerContext.contains("recebendo", ignoreCase = true) ||
            lowerContext.contains("ativo", ignoreCase = true) ||
            lowerContext.contains("em pagamento", ignoreCase = true) -> BenefitStatus.ACTIVE
            
            lowerContext.contains("pendente", ignoreCase = true) ||
            lowerContext.contains("aguardando", ignoreCase = true) ||
            lowerContext.contains("em análise", ignoreCase = true) -> BenefitStatus.PENDING
            
            lowerContext.contains("elegível", ignoreCase = true) ||
            lowerContext.contains("pode receber", ignoreCase = true) ||
            lowerContext.contains("tem direito", ignoreCase = true) -> BenefitStatus.ELIGIBLE
            
            lowerContext.contains("bloqueado", ignoreCase = true) ||
            lowerContext.contains("suspenso", ignoreCase = true) -> BenefitStatus.BLOCKED
            
            lowerContext.contains("não elegível", ignoreCase = true) ||
            lowerContext.contains("não tem direito", ignoreCase = true) -> BenefitStatus.NOT_ELIGIBLE
            
            else -> BenefitStatus.ACTIVE // Default assumption
        }
    }
    
    /**
     * Parse date string to LocalDate
     */
    private fun parseDate(day: String, month: String, year: String): LocalDate? {
        return try {
            val dayInt = day.toInt()
            val monthInt = month.toInt()
            val yearInt = if (year.length == 2) {
                2000 + year.toInt()
            } else {
                year.toInt()
            }
            LocalDate.of(yearInt, monthInt, dayInt)
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Parse alerts from gerar_alertas_beneficios response
     */
    fun parseAlerts(response: String): List<UserAlert> {
        val alerts = mutableListOf<UserAlert>()
        
        // Pattern for different alert types
        val alertPatterns = listOf(
            Triple(
                Pattern.compile("""CadÚnico.*desatualizado|Cadastro.*desatualizado""", Pattern.CASE_INSENSITIVE),
                AlertCategory.ACTION_REQUIRED,
                "Atualizar CadÚnico"
            ),
            Triple(
                Pattern.compile("""pagamento.*atrasado|atraso.*pagamento""", Pattern.CASE_INSENSITIVE),
                AlertCategory.DEADLINE,
                "Verificar pagamento"
            ),
            Triple(
                Pattern.compile("""novo.*benefício|elegível.*benefício""", Pattern.CASE_INSENSITIVE),
                AlertCategory.NEW_BENEFIT,
                "Ver benefícios"
            )
        )
        
        alertPatterns.forEachIndexed { index, (pattern, category, actionLabel) ->
            val matcher = pattern.matcher(response)
            if (matcher.find()) {
                val context = extractContext(response, matcher.start(), matcher.end())
                
                alerts.add(
                    UserAlert(
                        id = "${category.name}_$index",
                        type = category,
                        title = when (category) {
                            AlertCategory.ACTION_REQUIRED -> "Ação necessária"
                            AlertCategory.DEADLINE -> "Prazo importante"
                            AlertCategory.NEW_BENEFIT -> "Novo benefício disponível"
                            else -> "Alerta"
                        },
                        message = context.take(200),
                        actionLabel = actionLabel,
                        actionRoute = "chat",
                        createdAt = LocalDate.now(),
                        priority = AlertPriority.HIGH
                    )
                )
            }
        }
        
        return alerts
    }

    // Helper functions


    private fun extractAmountForType(response: String, typePattern: String): Double? {
        val pattern = Pattern.compile(
            "$typePattern[^R]*R\\$\\s*([\\d.,]+)",
            Pattern.CASE_INSENSITIVE
        )
        val matcher = pattern.matcher(response)
        return if (matcher.find()) {
            parseBrazilianCurrency(matcher.group(1))
        } else null
    }

    private fun extractDocuments(response: String): List<DocumentItem> {
        val documents = mutableListOf<DocumentItem>()
        
        // Common document patterns
        val docPatterns = listOf(
            "RG" to "Documento de identidade",
            "CPF" to "Cadastro de Pessoa Física",
            "Comprovante de residência" to "Conta de luz ou água",
            "Comprovante de renda" to "Últimos 3 meses",
            "Certidão" to "Certidão de nascimento ou casamento",
            "Laudo médico" to "Laudo médico (se aplicável)"
        )
        
        docPatterns.forEach { (name, description) ->
            val pattern = Pattern.compile(name, Pattern.CASE_INSENSITIVE)
            if (pattern.matcher(response).find()) {
                documents.add(
                    DocumentItem(
                        name = name,
                        description = description,
                        isRequired = true,
                        isProvided = false
                    )
                )
            }
        }
        
        // If no documents found, add default ones
        if (documents.isEmpty()) {
            documents.addAll(
                listOf(
                    DocumentItem("RG de todos da casa", "Documento de identidade", true, false),
                    DocumentItem("CPF de todos da casa", "Cadastro de Pessoa Física", true, false),
                    DocumentItem("Comprovante de residência", "Conta de luz ou água", true, false)
                )
            )
        }
        
        return documents
    }

    private fun extractTips(response: String): List<String> {
        val tips = mutableListOf<String>()
        
        // Look for tip patterns
        val tipPattern = Pattern.compile("""(?:dica|sugestão|recomendação)[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)
        val matcher = tipPattern.matcher(response)
        
        while (matcher.find() && tips.size < 5) {
            val tip = matcher.group(1)?.trim()
            if (tip != null && tip.length > 10) {
                tips.add(tip)
            }
        }
        
        // Default tips if none found
        if (tips.isEmpty()) {
            tips.addAll(
                listOf(
                    "Chegue cedo para evitar filas",
                    "Leve todos os documentos originais",
                    "Se possível, agende horário antes"
                )
            )
        }
        
        return tips
    }

    private fun extractContext(text: String, start: Int, end: Int): String {
        val contextStart = maxOf(0, start - 50)
        val contextEnd = minOf(text.length, end + 50)
        return text.substring(contextStart, contextEnd)
    }
    
    /**
     * Parse money result - alias for parseMoneyCheckResult
     */
    fun parseMoneyResult(response: String, toolsUsed: List<String>): MessageMetadata.MoneyResult? {
        val moneyCheck = parseMoneyCheckResult(response, toolsUsed) ?: return null
        
        return MessageMetadata.MoneyResult(
            totalAmount = moneyCheck.totalAmount,
            types = moneyCheck.types
        )
    }
    
    /**
     * Parse medicine result from prescription processing
     */
    fun parseMedicineResult(response: String, toolsUsed: List<String>): MessageMetadata.MedicineResult? {
        if (!toolsUsed.contains("processar_receita") &&
            !response.contains("medicamento", ignoreCase = true) &&
            !response.contains("remédio", ignoreCase = true)
        ) {
            return null
        }
        
        val medicines = mutableListOf<MedicineInfo>()
        
        // Pattern to find medicine names
        val medicinePattern = Pattern.compile(
            """(?:medicamento|remédio)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)""",
            Pattern.CASE_INSENSITIVE
        )
        val matcher = medicinePattern.matcher(response)
        
        while (matcher.find()) {
            val name = matcher.group(1)?.trim() ?: continue
            
            // Check if available
            val contextStart = maxOf(0, matcher.start() - 50)
            val contextEnd = minOf(response.length, matcher.end() + 50)
            val context = response.substring(contextStart, contextEnd)
            
            val isAvailable = context.contains("disponível", ignoreCase = true) ||
                    context.contains("elegível", ignoreCase = true) ||
                    context.contains("gratuito", ignoreCase = true)
            
            // Extract dosage if mentioned
            val dosagePattern = Pattern.compile("""dosagem[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)
            val dosageMatcher = dosagePattern.matcher(context)
            val dosage = if (dosageMatcher.find()) dosageMatcher.group(1)?.trim() else null
            
            medicines.add(
                MedicineInfo(
                    name = name,
                    isAvailable = isAvailable,
                    dosage = dosage
                )
            )
        }
        
        return if (medicines.isNotEmpty()) {
            MessageMetadata.MedicineResult(medicines = medicines)
        } else null
    }
    
    /**
     * Parse eligibility result
     */
    fun parseEligibilityResult(response: String, toolsUsed: List<String>): MessageMetadata.EligibilityResult? {
        if (!toolsUsed.contains("verificar_elegibilidade") &&
            !response.contains("elegível", ignoreCase = true) &&
            !response.contains("tem direito", ignoreCase = true)
        ) {
            return null
        }
        
        // Extract program name
        val programPattern = Pattern.compile(
            """(?:para|do|de)\s+(Bolsa\s+Família|BPC|LOAS|Farmácia\s+Popular|TSEE)""",
            Pattern.CASE_INSENSITIVE
        )
        val programMatcher = programPattern.matcher(response)
        val programName = if (programMatcher.find()) {
            programMatcher.group(1) ?: "Benefício"
        } else {
            "Benefício"
        }
        
        val programCode = when {
            programName.contains("Bolsa", ignoreCase = true) -> "BOLSA_FAMILIA"
            programName.contains("BPC", ignoreCase = true) || programName.contains("LOAS", ignoreCase = true) -> "BPC"
            programName.contains("Farmácia", ignoreCase = true) -> "FARMACIA_POPULAR"
            programName.contains("TSEE", ignoreCase = true) -> "TSEE"
            else -> "UNKNOWN"
        }
        
        // Determine eligibility
        val isEligible = response.contains("elegível", ignoreCase = true) ||
                response.contains("tem direito", ignoreCase = true) ||
                response.contains("pode receber", ignoreCase = true)
        
        // Extract score if mentioned (0.0 to 1.0)
        val scorePattern = Pattern.compile("""(?:score|pontuação)[:\s]+([\d.]+)""", Pattern.CASE_INSENSITIVE)
        val scoreMatcher = scorePattern.matcher(response)
        val score = if (scoreMatcher.find()) {
            scoreMatcher.group(1)?.toFloatOrNull() ?: if (isEligible) 0.8f else 0.2f
        } else {
            if (isEligible) 0.8f else 0.2f
        }
        
        // Extract criteria
        val criteria = extractEligibilityCriteria(response)
        
        // Extract recommendation
        val recommendationPattern = Pattern.compile("""(?:recomendação|próximo passo)[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)
        val recommendationMatcher = recommendationPattern.matcher(response)
        val recommendation = if (recommendationMatcher.find()) {
            recommendationMatcher.group(1)?.trim()
        } else {
            if (isEligible) "Você pode solicitar este benefício" else "Você não atende aos critérios no momento"
        }
        
        return MessageMetadata.EligibilityResult(
            programCode = programCode,
            programName = programName,
            isEligible = isEligible,
            score = score,
            criteria = criteria,
            recommendation = recommendation ?: ""
        )
    }
    
    /**
     * Parse document list
     */
    fun parseDocumentList(response: String, toolsUsed: List<String>): List<DocumentItem>? {
        if (!toolsUsed.contains("gerar_checklist") &&
            !response.contains("documento", ignoreCase = true) &&
            !response.contains("checklist", ignoreCase = true)
        ) {
            return null
        }
        
        return extractDocuments(response)
    }
    
    /**
     * Parse location card
     */
    fun parseLocationCard(response: String, toolsUsed: List<String>): MessageMetadata.LocationCard? {
        if (!toolsUsed.contains("buscar_cras") &&
            !toolsUsed.contains("buscar_farmacia") &&
            !response.contains("endereço", ignoreCase = true) &&
            !response.contains("localização", ignoreCase = true)
        ) {
            return null
        }
        
        // Extract name
        val namePattern = Pattern.compile("""(?:CRAS|Farmácia|Unidade)[:\s]+([A-Z][^.\n]+)""", Pattern.CASE_INSENSITIVE)
        val nameMatcher = namePattern.matcher(response)
        val name = if (nameMatcher.find()) {
            nameMatcher.group(1)?.trim() ?: "Local"
        } else {
            "Local"
        }
        
        // Extract address
        val addressPattern = Pattern.compile("""(?:endereço|address)[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)
        val addressMatcher = addressPattern.matcher(response)
        val address = if (addressMatcher.find()) {
            addressMatcher.group(1)?.trim() ?: ""
        } else {
            ""
        }
        
        // Extract coordinates (latitude, longitude)
        val coordPattern = Pattern.compile("""(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)""")
        val coordMatcher = coordPattern.matcher(response)
        var latitude = 0.0
        var longitude = 0.0
        if (coordMatcher.find()) {
            latitude = coordMatcher.group(1)?.toDoubleOrNull() ?: 0.0
            longitude = coordMatcher.group(2)?.toDoubleOrNull() ?: 0.0
        }
        
        // Extract phone
        val phonePattern = Pattern.compile("""(?:telefone|phone)[:\s]+([\d\s\-\(\)]+)""", Pattern.CASE_INSENSITIVE)
        val phoneMatcher = phonePattern.matcher(response)
        val phone = if (phoneMatcher.find()) {
            phoneMatcher.group(1)?.trim()
        } else null
        
        // Extract distance
        val distancePattern = Pattern.compile("""(\d+(?:\.\d+)?)\s*(?:km|metros|m)""", Pattern.CASE_INSENSITIVE)
        val distanceMatcher = distancePattern.matcher(response)
        val distance = if (distanceMatcher.find()) {
            distanceMatcher.group(0)?.trim()
        } else null
        
        if (name.isNotEmpty() && address.isNotEmpty()) {
            return MessageMetadata.LocationCard(
                name = name,
                address = address,
                distance = distance,
                latitude = latitude,
                longitude = longitude,
                phone = phone
            )
        }
        
        return null
    }
    
    /**
     * Extract eligibility criteria from response
     */
    private fun extractEligibilityCriteria(response: String): List<EligibilityCriterion> {
        val criteria = mutableListOf<EligibilityCriterion>()
        
        // Common criteria patterns
        val criteriaPatterns = listOf(
            Triple("renda", "Renda per capita", Pattern.compile("""renda[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)),
            Triple("idade", "Idade", Pattern.compile("""idade[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE)),
            Triple("cadastro", "CadÚnico atualizado", Pattern.compile("""cadastro[:\s]+([^.\n]+)""", Pattern.CASE_INSENSITIVE))
        )
        
        criteriaPatterns.forEach { (key, name, pattern) ->
            val matcher = pattern.matcher(response)
            if (matcher.find()) {
                val details = matcher.group(1)?.trim()
                val isMet = !(details?.contains("não", ignoreCase = true) ?: false)
                
                criteria.add(
                    EligibilityCriterion(
                        name = name,
                        description = details ?: "",
                        isMet = isMet,
                        details = details
                    )
                )
            }
        }
        
        return criteria
    }
}



