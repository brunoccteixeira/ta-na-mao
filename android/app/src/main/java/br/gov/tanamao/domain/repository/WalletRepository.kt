package br.gov.tanamao.domain.repository

import br.gov.tanamao.domain.model.*
import kotlinx.coroutines.flow.Flow

/**
 * Repository for user's benefit wallet data
 */
interface WalletRepository {

    /**
     * Get the user's complete wallet data
     */
    suspend fun getWallet(): Result<Wallet>

    /**
     * Get wallet data as a Flow for real-time updates
     */
    fun observeWallet(): Flow<Result<Wallet>>

    /**
     * Get a specific benefit's details
     */
    suspend fun getBenefitDetail(benefitId: String): Result<BenefitDetail>

    /**
     * Get payment history with pagination
     */
    suspend fun getPaymentHistory(
        limit: Int = 50,
        offset: Int = 0
    ): Result<List<PaymentHistoryItem>>

    /**
     * Refresh wallet data from server
     */
    suspend fun refreshWallet(): Result<Unit>

    /**
     * Check eligibility for a specific program
     */
    suspend fun checkEligibility(programCode: String): Result<EligibilityDetails>

    /**
     * Start application process for a benefit
     */
    suspend fun startApplication(programCode: String): Result<String>
}
