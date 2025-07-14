from fastapi import HTTPException, status



class HTTP401Exception(HTTPException):
    def __init__(self, detail: str = "Not authenticated", headers: dict | None = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class HTTP403Exception(HTTPException):
    def __init__(self, detail: str = "Forbidden", headers: dict | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)
