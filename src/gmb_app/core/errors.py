class AppError(Exception):
    def __init__(self, message, code="app_error", retryable=False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class AuthError(AppError):
    def __init__(self, message, retryable=False):
        super().__init__(message, code="auth_error", retryable=retryable)


class IntegrationError(AppError):
    def __init__(self, message, retryable=True):
        super().__init__(message, code="integration_error", retryable=retryable)


class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, code="validation_error", retryable=False)
