package br.gov.tanamao

import br.gov.tanamao.domain.model.*
import java.time.LocalDate

/**
 * Test utilities for creating mock data.
 */
object TestUtils {

    fun createMockProgram(code: ProgramCode = ProgramCode.CADUNICO): Program {
        return Program(
            code = code,
            name = when (code) {
                ProgramCode.CADUNICO -> "Bolsa Família / CadÚnico"
                ProgramCode.BPC -> "BPC/LOAS"
                ProgramCode.FARMACIA_POPULAR -> "Farmácia Popular"
                ProgramCode.TSEE -> "Tarifa Social de Energia"
                ProgramCode.DIGNIDADE_MENSTRUAL -> "Dignidade Menstrual"
            },
            description = "Programa de teste",
            dataSourceUrl = "https://example.gov.br",
            updateFrequency = UpdateFrequency.MONTHLY,
            nationalStats = null
        )
    }

    fun createMockUserBenefit(
        id: String = "1",
        status: BenefitStatus = BenefitStatus.ACTIVE
    ): UserBenefit {
        return UserBenefit(
            id = id,
            programCode = "CADUNICO",
            programName = "Bolsa Família",
            status = status,
            monthlyValue = 600.0,
            nextPaymentDate = LocalDate.now().plusDays(5)
        )
    }

    fun createMockUserAlert(
        id: String = "a1",
        priority: AlertPriority = AlertPriority.NORMAL
    ): UserAlert {
        return UserAlert(
            id = id,
            type = AlertCategory.NEW_BENEFIT,
            title = "Test Alert",
            message = "This is a test alert",
            createdAt = LocalDate.now(),
            priority = priority
        )
    }

    fun createMockNationalStats(): NationalStats {
        return NationalStats(
            population = 215000000,
            cadUnicoFamilies = 40000000,
            totalMunicipalities = 5570,
            totalStates = 27,
            totalBeneficiaries = 20000000,
            totalFamilies = 15000000,
            totalValueBrl = 12000000000.0,
            avgCoverageRate = 0.75
        )
    }

    fun createMockMunicipality(): Municipality {
        return Municipality(
            ibgeCode = "3550308",
            name = "São Paulo",
            stateAbbreviation = "SP",
            stateName = "São Paulo",
            region = Region.SE,
            population = 12400000
        )
    }

    fun createMockMunicipalitySearchResult(): MunicipalitySearchResult {
        return MunicipalitySearchResult(
            ibgeCode = "3550308",
            name = "São Paulo",
            stateAbbreviation = "SP",
            population = 12400000
        )
    }
}
