package br.gov.tanamao.presentation.ui.benefit

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.WalletRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class BenefitDetailViewModel @Inject constructor(
    private val walletRepository: WalletRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val benefitId: String = savedStateHandle.get<String>("benefitId") ?: ""

    private val _uiState = MutableStateFlow(BenefitDetailUiState())
    val uiState: StateFlow<BenefitDetailUiState> = _uiState.asStateFlow()

    init {
        loadBenefitDetail()
    }

    fun refresh() {
        loadBenefitDetail()
    }

    fun toggleFaqExpanded(index: Int) {
        _uiState.update { state ->
            val newExpanded = state.expandedFaqIndex.toMutableSet()
            if (index in newExpanded) {
                newExpanded.remove(index)
            } else {
                newExpanded.add(index)
            }
            state.copy(expandedFaqIndex = newExpanded)
        }
    }

    private fun loadBenefitDetail() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            when (val result = walletRepository.getBenefitDetail(benefitId)) {
                is Result.Success -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            benefitDetail = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    // Fallback to default data
                    loadDefaultBenefitDetail()
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = result.exception.getUserMessage()
                        )
                    }
                }
                Result.Loading -> {
                    _uiState.update { it.copy(isLoading = true) }
                }
            }
        }
    }

    private fun loadDefaultBenefitDetail() {
        val defaultBenefit = UserBenefit(
            id = benefitId,
            programCode = benefitId,
            programName = getProgramName(benefitId),
            status = BenefitStatus.ACTIVE
        )

        val defaultDetail = BenefitDetail(
            benefit = defaultBenefit,
            description = getProgramDescription(benefitId),
            requirements = getRequirements(benefitId),
            documents = getDocuments(benefitId),
            howToApply = getHowToApply(benefitId),
            contacts = getContacts(benefitId),
            faq = getFaq(benefitId)
        )

        _uiState.update {
            it.copy(
                benefitDetail = defaultDetail
            )
        }
    }

    // ============ Helper methods for default data ============

    private fun getProgramName(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Bolsa Familia"
        "BPC" -> "BPC/LOAS"
        "FARMACIA_POPULAR" -> "Farmacia Popular"
        "TSEE" -> "Tarifa Social de Energia"
        "DIGNIDADE_MENSTRUAL" -> "Dignidade Menstrual"
        "AUXILIO_GAS" -> "Auxilio Gas"
        "PIS_PASEP" -> "Abono PIS/PASEP"
        else -> code.replace("_", " ")
    }

    private fun getProgramDescription(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Programa de transferencia de renda que ajuda familias em situacao de pobreza e extrema pobreza a superarem a vulnerabilidade social."
        "BPC" -> "Beneficio de Prestacao Continuada que garante um salario minimo mensal para idosos acima de 65 anos e pessoas com deficiencia de baixa renda."
        "FARMACIA_POPULAR" -> "Programa que oferece medicamentos gratuitos ou com ate 90% de desconto em farmacias credenciadas em todo o Brasil."
        "TSEE" -> "Desconto na conta de energia eletrica para familias inscritas no CadUnico com renda de ate meio salario minimo."
        "DIGNIDADE_MENSTRUAL" -> "Programa que fornece absorventes e produtos de higiene menstrual gratuitamente para pessoas em situacao de vulnerabilidade."
        "AUXILIO_GAS" -> "Auxilio para compra de botijao de gas (GLP) para familias inscritas no CadUnico."
        "PIS_PASEP" -> "Abono salarial anual para trabalhadores com carteira assinada que recebem ate 2 salarios minimos."
        else -> "Programa social do governo federal brasileiro."
    }

    private fun getRequirements(code: String): List<String> = when (code) {
        "BOLSA_FAMILIA" -> listOf(
            "Renda familiar per capita de ate R$ 218,00",
            "Estar inscrito no CadUnico com dados atualizados",
            "Manter criancas e adolescentes na escola",
            "Manter vacinacao em dia",
            "Acompanhamento de saude de gestantes"
        )
        "BPC" -> listOf(
            "Ter 65 anos ou mais OU ter deficiencia de longo prazo",
            "Renda familiar per capita inferior a 1/4 do salario minimo",
            "Nao receber outro beneficio previdenciario",
            "Estar inscrito no CadUnico"
        )
        "FARMACIA_POPULAR" -> listOf(
            "Ter CPF valido",
            "Apresentar receita medica valida (ate 180 dias)",
            "Medicamento deve estar na lista do programa"
        )
        "TSEE" -> listOf(
            "Estar inscrito no CadUnico",
            "Renda familiar per capita de ate 1/2 salario minimo",
            "Ou receber BPC",
            "Ou ter familiar com doenca que necessite de aparelhos eletricos vitais"
        )
        else -> listOf(
            "Estar inscrito no CadUnico",
            "Atender aos criterios de renda do programa"
        )
    }

    private fun getDocuments(code: String): List<String> = when (code) {
        "BOLSA_FAMILIA" -> listOf(
            "RG ou Certidao de Nascimento de todos da familia",
            "CPF de todos os maiores de idade",
            "Comprovante de residencia atualizado",
            "Carteira de Trabalho (se tiver)",
            "Comprovante de matricula escolar das criancas"
        )
        "BPC" -> listOf(
            "RG e CPF do requerente",
            "Comprovante de residencia",
            "Laudo medico (para PCD)",
            "Comprovante de renda de todos da familia",
            "Formularios do INSS preenchidos"
        )
        "FARMACIA_POPULAR" -> listOf(
            "CPF",
            "Receita medica valida"
        )
        else -> listOf(
            "RG ou CNH",
            "CPF",
            "Comprovante de residencia",
            "Comprovante de renda"
        )
    }

    private fun getHowToApply(code: String): String = when (code) {
        "BOLSA_FAMILIA" -> "Va ao CRAS (Centro de Referencia de Assistencia Social) mais proximo com seus documentos. O cadastramento e gratuito e o beneficio e concedido automaticamente para quem atende aos criterios."
        "BPC" -> "Agende atendimento no INSS pelo telefone 135 ou pelo app/site Meu INSS. Voce pode tambem ir presencialmente a uma agencia do INSS com os documentos necessarios."
        "FARMACIA_POPULAR" -> "Va a uma farmacia credenciada com sua receita medica e CPF. Nao e necessario cadastro previo. Consulte as farmacias credenciadas no site do Ministerio da Saude."
        "TSEE" -> "O desconto e aplicado automaticamente na conta de luz para quem esta inscrito no CadUnico. Mantenha seu cadastro atualizado no CRAS para garantir o beneficio."
        else -> "Procure o CRAS mais proximo para mais informacoes sobre como solicitar este beneficio."
    }

    private fun getContacts(code: String): List<ContactInfo> = listOf(
        ContactInfo(
            type = ContactType.PHONE,
            value = "121",
            label = "Disque Social"
        ),
        ContactInfo(
            type = ContactType.PHONE,
            value = "135",
            label = "Central INSS"
        ),
        ContactInfo(
            type = ContactType.WEBSITE,
            value = "https://www.gov.br/cidadania",
            label = "Portal Gov.br"
        )
    )

    private fun getFaq(code: String): List<FaqItem> = when (code) {
        "BOLSA_FAMILIA" -> listOf(
            FaqItem(
                "Quando recebo o pagamento?",
                "O pagamento e feito nos ultimos 10 dias uteis do mes, de acordo com o final do seu NIS (Numero de Identificacao Social)."
            ),
            FaqItem(
                "Posso trabalhar e continuar recebendo?",
                "Sim! Existe a Regra de Protecao que permite manter o beneficio por ate 2 anos apos conseguir emprego formal."
            ),
            FaqItem(
                "O que pode bloquear meu beneficio?",
                "Falta de atualizacao do CadUnico, criancas fora da escola, falta de acompanhamento de saude ou informacoes incorretas."
            )
        )
        "BPC" -> listOf(
            FaqItem(
                "Preciso contribuir para o INSS?",
                "Nao, o BPC nao exige contribuicao previa ao INSS. E um beneficio assistencial, nao previdenciario."
            ),
            FaqItem(
                "Posso acumular com aposentadoria?",
                "Nao, o BPC nao pode ser acumulado com aposentadoria ou outros beneficios previdenciarios."
            ),
            FaqItem(
                "De quanto em quanto tempo preciso renovar?",
                "O beneficio e revisado a cada 2 anos para verificar se voce ainda atende aos criterios."
            )
        )
        "FARMACIA_POPULAR" -> listOf(
            FaqItem(
                "Quais medicamentos sao gratuitos?",
                "Medicamentos para hipertensao, diabetes e asma sao 100% gratuitos. Outros tem ate 90% de desconto."
            ),
            FaqItem(
                "A receita tem validade?",
                "Sim, a receita medica e valida por 180 dias (6 meses) para retirada dos medicamentos."
            )
        )
        else -> listOf(
            FaqItem(
                "Onde posso tirar duvidas?",
                "Ligue para o Disque Social 121 ou procure o CRAS mais proximo da sua residencia."
            ),
            FaqItem(
                "Quanto tempo demora para receber?",
                "O prazo varia de acordo com cada programa. Consulte o CRAS para informacoes especificas."
            )
        )
    }
}

data class BenefitDetailUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val benefitDetail: BenefitDetail? = null,
    val expandedFaqIndex: Set<Int> = emptySet()
) {
    val benefit: UserBenefit?
        get() = benefitDetail?.benefit

    val programName: String
        get() = benefitDetail?.benefit?.programName ?: ""

    val description: String
        get() = benefitDetail?.description ?: ""

    val requirements: List<String>
        get() = benefitDetail?.requirements ?: emptyList()

    val documents: List<String>
        get() = benefitDetail?.documents ?: emptyList()

    val howToApply: String
        get() = benefitDetail?.howToApply ?: ""

    val contacts: List<ContactInfo>
        get() = benefitDetail?.contacts ?: emptyList()

    val faq: List<FaqItem>
        get() = benefitDetail?.faq ?: emptyList()
}
