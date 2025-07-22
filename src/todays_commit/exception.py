from fastapi import HTTPException


class ExpiredTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Expired token")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")


class ForbiddenInvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Forbidden (Invalid token)")


class ForbiddenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="권한이 없습니다.")


class ValidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=200, detail="Valid token")


class BadRequestException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Bad request")
