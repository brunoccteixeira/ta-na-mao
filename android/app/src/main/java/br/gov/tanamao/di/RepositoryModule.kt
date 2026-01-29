package br.gov.tanamao.di

import br.gov.tanamao.data.repository.AgentRepositoryImpl
import br.gov.tanamao.data.repository.AggregationRepositoryImpl
import br.gov.tanamao.data.repository.MunicipalityRepositoryImpl
import br.gov.tanamao.data.repository.ProgramRepositoryImpl
import br.gov.tanamao.data.repository.WalletRepositoryImpl
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AggregationRepository
import br.gov.tanamao.domain.repository.MunicipalityRepository
import br.gov.tanamao.domain.repository.ProgramRepository
import br.gov.tanamao.domain.repository.WalletRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindProgramRepository(
        impl: ProgramRepositoryImpl
    ): ProgramRepository

    @Binds
    @Singleton
    abstract fun bindMunicipalityRepository(
        impl: MunicipalityRepositoryImpl
    ): MunicipalityRepository

    @Binds
    @Singleton
    abstract fun bindAggregationRepository(
        impl: AggregationRepositoryImpl
    ): AggregationRepository

    @Binds
    @Singleton
    abstract fun bindAgentRepository(
        impl: AgentRepositoryImpl
    ): AgentRepository

    @Binds
    @Singleton
    abstract fun bindWalletRepository(
        impl: WalletRepositoryImpl
    ): WalletRepository
}
