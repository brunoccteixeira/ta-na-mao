package br.gov.tanamao.presentation.ui.details

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.Municipality
import br.gov.tanamao.domain.model.Region
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.MunicipalityRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class MunicipalityViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var repository: MunicipalityRepository
    private lateinit var viewModel: MunicipalityViewModel

    @Before
    fun setup() {
        repository = mockk()
        viewModel = MunicipalityViewModel(repository)
    }

    @Test
    fun `loadMunicipality should update state with municipality on success`() = runTest {
        // Given
        val ibgeCode = "3550308"
        val mockMunicipality = Municipality(
            ibgeCode = ibgeCode,
            name = "São Paulo",
            stateAbbreviation = "SP",
            stateName = "São Paulo",
            region = Region.SE,
            population = 12325232
        )
        coEvery { repository.getMunicipality(ibgeCode) } returns Result.Success(mockMunicipality)
        coEvery { repository.getMunicipalityPrograms(ibgeCode) } returns Result.Success(emptyList())

        // When
        viewModel.loadMunicipality(ibgeCode)

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.municipality)
            assertEquals(ibgeCode, state.municipality?.ibgeCode)
        }
    }

    @Test
    fun `loadMunicipality should update state with error on failure`() = runTest {
        // Given
        val ibgeCode = "3550308"
        val appError = AppError.NotFound("Municipality not found")
        coEvery { repository.getMunicipality(ibgeCode) } returns Result.Error(appError)

        // When
        viewModel.loadMunicipality(ibgeCode)

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.error)
        }
    }

    @Test
    fun `initial state should not be loading`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNull(state.municipality)
            assertNull(state.error)
        }
    }
}
