from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(self, **kwargs):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"}, **kwargs)


class InvalidTokenException(UnauthorizedException):
    def __init__(self, **kwargs):
        super().__init__(detail="Не валидный токен", **kwargs)


class ExpireTokenException(UnauthorizedException):
    def __init__(self, **kwargs):
        super().__init__(detail="Токен просрочен", **kwargs)
