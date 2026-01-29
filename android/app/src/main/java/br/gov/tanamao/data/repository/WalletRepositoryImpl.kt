package br.gov.tanamao.data.repository

import br.gov.tanamao.di.IoDispatcher
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.WalletRepository
import br.gov.tanamao.presentation.util.AgentResponseParser
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
import java.time.LocalDate
import java.time.YearMonth
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WalletRepositoryImpl @Inject constructor(
    private val agentRepository: AgentRepository,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : WalletRepository {

    override suspend fun getWallet(): Result<Wallet> = withContext(dispatcher) {
        try {
            // Call agent with "meus dados" to get user benefits
            when (val result = agentRepository.sendMessage("meus dados", "")) {
                is Result.Success -> {
                    val response = result.data.message
                    val wallet = parseWalletFromResponse(response)
                    Result.Success(wallet)
                }
                is Result.Error -> {
                    Result.Error(result.exception)
                }
                Result.Loading -> {
                    Result.Loading
                }
            }
        } catch (e: Exception) {
            Result.Error(AppError.Unknown(e))
        }
    }

    override fun observeWallet(): Flow<Result<Wallet>> = flow {
        emit(Result.Loading)
        emit(getWallet())
    }.flowOn(dispatcher)

    override suspend fun getBenefitDetail(benefitId: String): Result<BenefitDetail> =
        withContext(dispatcher) {
            try {
                // Call agent asking for specific benefit details
                val message = "detalhes do benefício $benefitId"
                when (val result = agentRepository.sendMessage(message, "")) {
                    is Result.Success -> {
                        val response = result.data.message
                        val detail = parseBenefitDetailFromResponse(response, benefitId)
                        Result.Success(detail)
                    }
                    is Result.Error -> {
                        Result.Error(result.exception)
                    }
                    Result.Loading -> {
                        Result.Loading
                    }
                }
            } catch (e: Exception) {
                Result.Error(AppError.Unknown(e))
            }
        }

    override suspend fun getPaymentHistory(limit: Int, offset: Int): Result<List<PaymentHistoryItem>> =
        withContext(dispatcher) {
            try {
                // Call agent for payment history
                when (val result = agentRepository.sendMessage("histórico de pagamentos", "")) {
                    is Result.Success -> {
                        val response = result.data.message
                        val history = parsePaymentHistoryFromResponse(response)
                        Result.Success(history.drop(offset).take(limit))
                    }
                    is Result.Error -> {
                        Result.Error(result.exception)
                    }
                    Result.Loading -> {
                        Result.Loading
                    }
                }
            } catch (e: Exception) {
                Result.Error(AppError.Unknown(e))
            }
        }

    override suspend fun refreshWallet(): Result<Unit> = withContext(dispatcher) {
        // Force refresh by getting wallet again
        when (getWallet()) {
            is Result.Success -> Result.Success(Unit)
            is Result.Error -> Result.Error(AppError.Unknown(Exception("Failed to refresh")))
            Result.Loading -> Result.Loading
        }
    }

    override suspend fun checkEligibility(programCode: String): Result<EligibilityDetails> =
        withContext(dispatcher) {
            try {
                val message = "verificar elegibilidade para $programCode"
                when (val result = agentRepository.sendMessage(message, "")) {
                    is Result.Success -> {
                        val response = result.data.message
                        val eligibility = parseEligibilityFromResponse(response)
                        Result.Success(eligibility)
                    }
                    is Result.Error -> {
                        Result.Error(result.exception)
                    }
                    Result.Loading -> {
                        Result.Loading
                    }
                }
            } catch (e: Exception) {
                Result.Error(AppError.Unknown(e))
            }
        }

    override suspend fun startApplication(programCode: String): Result<String> =
        withContext(dispatcher) {
            try {
                val message = "como solicitar $programCode"
                when (val result = agentRepository.sendMessage(message, "")) {
                    is Result.Success -> {
                        Result.Success(result.data.message)
                    }
                    is Result.Error -> {
                        Result.Error(result.exception)
                    }
                    Result.Loading -> {
                        Result.Loading
                    }
                }
            } catch (e: Exception) {
                Result.Error(AppError.Unknown(e))
            }
        }

    // ============ Private parsing methods ============

    private fun parseWalletFromResponse(response: String): Wallet {
        // Use AgentResponseParser to extract benefits
        val benefits = AgentResponseParser.parseUserBenefits(response)

        // Separate by status
        val activeBenefits = benefits.filter { it.status == BenefitStatus.ACTIVE }
        val eligibleBenefits = benefits.filter { it.status == BenefitStatus.ELIGIBLE }
        val pendingBenefits = benefits.filter { it.status == BenefitStatus.PENDING }

        // Calculate summary
        val totalMonthly = activeBenefits.mapNotNull { it.monthlyValue }.sum()
        val nextPayment = activeBenefits
            .mapNotNull { it.nextPaymentDate }
            .minOrNull()
        val nextPaymentValue = activeBenefits
            .filter { it.nextPaymentDate == nextPayment }
            .mapNotNull { it.monthlyValue }
            .sum()

        val summary = WalletSummary(
            totalMonthlyValue = totalMonthly,
            activeBenefitsCount = activeBenefits.size,
            eligibleBenefitsCount = eligibleBenefits.size,
            pendingBenefitsCount = pendingBenefits.size,
            nextPaymentDate = nextPayment,
            nextPaymentValue = if (nextPaymentValue > 0) nextPaymentValue else null
        )

        // Generate mock payment history based on active benefits
        val paymentHistory = generatePaymentHistory(activeBenefits)

        return Wallet(
            summary = summary,
            activeBenefits = activeBenefits,
            eligibleBenefits = eligibleBenefits,
            pendingBenefits = pendingBenefits,
            paymentHistory = paymentHistory
        )
    }

    private fun parseBenefitDetailFromResponse(response: String, benefitId: String): BenefitDetail {
        // Try to extract benefit from response
        val benefits = AgentResponseParser.parseUserBenefits(response)
        val benefit = benefits.find { it.id == benefitId || it.programCode == benefitId }
            ?: UserBenefit(
                id = benefitId,
                programCode = benefitId,
                programName = getProgramName(benefitId),
                status = BenefitStatus.ACTIVE
            )

        // Extract documents from response
        val documents = AgentResponseParser.parseDocumentList(response, emptyList())
            ?.map { it.name } ?: getDefaultDocuments(benefitId)

        return BenefitDetail(
            benefit = benefit,
            description = getProgramDescription(benefitId),
            requirements = getRequirements(benefitId),
            documents = documents,
            howToApply = getHowToApply(benefitId),
            contacts = getContacts(benefitId),
            faq = getFaq(benefitId)
        )
    }

    private fun parsePaymentHistoryFromResponse(response: String): List<PaymentHistoryItem> {
        val benefits = AgentResponseParser.parseUserBenefits(response)
        return generatePaymentHistory(benefits.filter { it.status == BenefitStatus.ACTIVE })
    }

    private fun parseEligibilityFromResponse(response: String): EligibilityDetails {
        val eligibilityResult = AgentResponseParser.parseEligibilityResult(response, listOf("verificar_elegibilidade"))

        return EligibilityDetails(
            criteria = eligibilityResult?.criteria ?: emptyList(),
            assessmentDate = LocalDate.now(),
            overallScore = eligibilityResult?.score ?: 0.5f,
            recommendation = eligibilityResult?.recommendation
        )
    }

    private fun generatePaymentHistory(activeBenefits: List<UserBenefit>): List<PaymentHistoryItem> {
        val history = mutableListOf<PaymentHistoryItem>()
        val today = LocalDate.now()

        // Generate last 6 months of payment history for each active benefit
        activeBenefits.forEach { benefit ->
            for (i in 1..6) {
                val paymentDate = today.minusMonths(i.toLong()).withDayOfMonth(10)
                val reference = YearMonth.from(paymentDate)

                history.add(
                    PaymentHistoryItem(
                        id = "${benefit.id}_${reference}",
                        programCode = benefit.programCode,
                        programName = benefit.programName,
                        date = paymentDate,
                        value = benefit.monthlyValue ?: 0.0,
                        reference = reference,
                        status = PaymentStatus.PAID
                    )
                )
            }
        }

        return history.sortedByDescending { it.date }
    }

    // ============ Helper methods for default data ============

    private fun getProgramName(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Bolsa Familia"
        "BPC" -> "BPC/LOAS"
        "FARMACIA_POPULAR" -> "Farmacia Popular"
        "TSEE" -> "Tarifa Social de Energia"
        "DIGNIDADE_MENSTRUAL" -> "Dignidade Menstrual"
        "AUXILIO_GAS" -> "Auxilio Gas"
        else -> code
    }

    private fun getProgramDescription(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Programa de transferencia de renda que ajuda familias em situacao de pobreza e extrema pobreza."
        "BPC" -> "Beneficio de Prestacao Continuada para idosos acima de 65 anos e pessoas com deficiencia."
        "FARMACIA_POPULAR" -> "Programa que oferece medicamentos gratuitos ou com ate 90% de desconto."
        "TSEE" -> "Desconto na conta de energia eletrica para familias de baixa renda."
        "DIGNIDADE_MENSTRUAL" -> "Programa que fornece absorventes e produtos de higiene menstrual."
        else -> "Programa social do governo federal."
    }

    private fun getRequirements(code: String): List<String> = when (code) {
        "BOLSA_FAMILIA" -> listOf(
            "Renda familiar per capita de ate R$ 218,00",
            "Cadastro atualizado no CadUnico",
            "Manter criancas na escola",
            "Manter vacinacao em dia"
        )
        "BPC" -> listOf(
            "Idade acima de 65 anos OU ter deficiencia",
            "Renda familiar per capita inferior a 1/4 do salario minimo",
            "Nao receber outro beneficio da Previdencia Social",
            "Cadastro no CadUnico"
        )
        "FARMACIA_POPULAR" -> listOf(
            "Receita medica valida",
            "CPF do paciente",
            "Medicamento deve estar na lista do programa"
        )
        "TSEE" -> listOf(
            "Cadastro no CadUnico com renda de ate 1/2 salario minimo",
            "Ou receber BPC",
            "Ou ter doente que use equipamentos eletricos vitais"
        )
        else -> listOf("Cadastro no CadUnico", "Documentos pessoais")
    }

    private fun getDefaultDocuments(code: String): List<String> = listOf(
        "RG ou CNH",
        "CPF",
        "Comprovante de residencia",
        "Comprovante de renda"
    )

    private fun getHowToApply(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Va ao CRAS mais proximo com seus documentos para atualizar o CadUnico. O beneficio e concedido automaticamente para quem atende aos criterios."
        "BPC" -> "Agende atendimento no INSS pelo telefone 135 ou pelo app Meu INSS. Leve laudo medico se for pessoa com deficiencia."
        "FARMACIA_POPULAR" -> "Va a uma farmacia credenciada com sua receita medica e CPF. Nao precisa cadastro previo."
        "TSEE" -> "O desconto e aplicado automaticamente na conta de luz para quem esta no CadUnico. Mantenha seu cadastro atualizado."
        else -> "Procure o CRAS mais proximo para mais informacoes."
    }

    private fun getContacts(code: String): List<ContactInfo> = listOf(
        ContactInfo(
            type = ContactType.PHONE,
            value = "121",
            label = "Disque Social"
        ),
        ContactInfo(
            type = ContactType.WEBSITE,
            value = "https://www.gov.br/cidadania",
            label = "Portal do Cidadao"
        )
    )

    private fun getFaq(code: String): List<FaqItem> = when (code) {
        "BOLSA_FAMILIA" -> listOf(
            FaqItem(
                "Quando recebo o pagamento?",
                "O pagamento e feito nos ultimos 10 dias uteis do mes, conforme o final do NIS."
            ),
            FaqItem(
                "Posso trabalhar e receber?",
                "Sim, existe a regra de protecao que permite manter o beneficio por ate 2 anos apos conseguir emprego."
            )
        )
        "BPC" -> listOf(
            FaqItem(
                "Preciso contribuir para o INSS?",
                "Nao, o BPC nao exige contribuicao previa."
            ),
            FaqItem(
                "Posso acumular com aposentadoria?",
                "Nao, o BPC nao pode ser acumulado com outros beneficios previdenciarios."
            )
        )
        else -> listOf(
            FaqItem(
                "Onde posso tirar duvidas?",
                "Ligue para o Disque Social 121 ou procure o CRAS mais proximo."
            )
        )
    }
}
