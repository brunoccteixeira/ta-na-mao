package br.gov.tanamao.domain.model

/**
 * A generic result wrapper for async operations.
 */
sealed class Result<out T> {
    /**
     * Operation is in progress.
     */
    object Loading : Result<Nothing>()

    /**
     * Operation completed successfully with data.
     */
    data class Success<T>(val data: T) : Result<T>()

    /**
     * Operation failed with an error.
     */
    data class Error(val exception: AppError) : Result<Nothing>()

    /**
     * Check if result is successful.
     */
    val isSuccess: Boolean get() = this is Success

    /**
     * Check if result is loading.
     */
    val isLoading: Boolean get() = this is Loading

    /**
     * Check if result is an error.
     */
    val isError: Boolean get() = this is Error

    /**
     * Get data or null.
     */
    fun getOrNull(): T? = when (this) {
        is Success -> data
        else -> null
    }

    /**
     * Get data or default value.
     */
    fun getOrDefault(default: @UnsafeVariance T): T = when (this) {
        is Success -> data
        else -> default
    }

    /**
     * Map the result to another type.
     */
    fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Loading -> Loading
        is Success -> Success(transform(data))
        is Error -> this
    }
}

/**
 * Application error types.
 */
sealed class AppError : Exception() {
    data class Network(override val message: String = "Sem conexão com a internet") : AppError()
    data class Server(val code: Int, override val message: String) : AppError()
    data class NotFound(override val message: String = "Recurso não encontrado") : AppError()
    data class Timeout(override val message: String = "Tempo de conexão esgotado") : AppError()
    data class Unknown(override val cause: Throwable) : AppError()

    /**
     * Get user-friendly message.
     */
    fun getUserMessage(): String = when (this) {
        is Network -> "Verifique sua conexão com a internet"
        is Server -> "Erro no servidor. Tente novamente mais tarde"
        is NotFound -> "Dados não encontrados"
        is Timeout -> "Conexão demorou muito. Tente novamente"
        is Unknown -> "Erro inesperado. Tente novamente"
    }
}
