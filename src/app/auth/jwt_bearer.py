from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from src.app.config.settings import settings

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            payload = self.verify_jwt(token=credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> dict:
        print("sds")
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            print("Decoded Payload:", payload)
            return payload
        except JWTError as e:
            print(f"JWTError: {e}")
            return None