/**
 * Error handling utilities for the frontend.
 */

export interface ApiError {
  message: string;
  details?: Record<string, unknown>;
  statusCode?: number;
}

/**
 * Parse error from API response.
 */
export function parseApiError(error: unknown): ApiError {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as { response?: { data?: unknown; status?: number } };
    const data = axiosError.response?.data;
    const statusCode = axiosError.response?.status;

    if (data && typeof data === 'object' && 'error' in data) {
      const errorData = data as { error: unknown; details?: Record<string, unknown> };
      return {
        message: String(errorData.error),
        details: errorData.details,
        statusCode,
      };
    }

    return {
      message: 'An error occurred while processing your request',
      statusCode,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message || 'An unexpected error occurred',
    };
  }

  return {
    message: 'An unexpected error occurred',
  };
}

/**
 * Get user-friendly error message.
 */
export function getUserFriendlyMessage(error: ApiError): string {
  const { message, statusCode } = error;

  // Map common HTTP status codes to user-friendly messages
  switch (statusCode) {
    case 400:
      return 'Invalid request. Please check your input and try again.';
    case 401:
      return 'You are not authorized to perform this action.';
    case 403:
      return 'Access denied. You do not have permission to access this resource.';
    case 404:
      return 'The requested resource was not found.';
    case 422:
      return 'Validation error. Please check your input.';
    case 500:
      return 'A server error occurred. Please try again later.';
    case 502:
      return 'Service temporarily unavailable. Please try again later.';
    case 503:
      return 'Service is currently unavailable. Please try again later.';
    default:
      return message || 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Log error for debugging.
 */
export function logError(error: unknown, context?: string): void {
  const apiError = parseApiError(error);
  console.error('Error occurred:', {
    context,
    message: apiError.message,
    details: apiError.details,
    statusCode: apiError.statusCode,
    originalError: error,
  });
}






