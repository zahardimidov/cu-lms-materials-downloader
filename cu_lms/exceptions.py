class ApiError(Exception):
    """Базовая ошибка API."""


class UnauthorizedError(ApiError):
    """401/отсутствует или неверный Cookie."""


class NotFoundError(ApiError):
    """Ресурс не найден."""
