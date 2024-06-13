from fastapi import HTTPException, status


class BadRequestHTTPException(HTTPException):
    def __init__(self, msg=None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg or "Bad request",
        )


class AuthFailedHTTPException(HTTPException):
    def __init__(self, msg=None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg or "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenExpiredHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundHTTPException(HTTPException):
    def __init__(self, msg=None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg or "Requested resource is not found",
        )
