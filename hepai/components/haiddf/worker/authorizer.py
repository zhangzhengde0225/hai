

from typing import Optional
from fastapi import Header, Depends
from fastapi import HTTPException

async def extract_api_key(
        authorization: Optional[str] = Header(None, alias="Authorization"),
        x_api_key: Optional[str] = Header(None, alias="x-api-key")
    ) -> Optional[str]:
    """
    Extract API key from either Authorization header (Bearer format) or x-api-key header
    Supports both formats:
    - Authorization: Bearer <token>
    - x-api-key: <token>
    """
    if authorization:
        # 去掉bearer前缀（如果有的话）
        if authorization.lower().startswith("bearer "):
            authorization = authorization[7:].strip()
        return authorization
    elif x_api_key:
        return x_api_key
    return None


class Authorizer:
    
    def __init__(self):
        self._secret_key = None 
    
    @property
    def secret_key(self):
        return self._secret_key
    
    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value
        
        
    async def api_key_auth(self, api_key: str = Depends(extract_api_key)):    
        if self._secret_key is None:
            return True
        if not api_key:
            raise HTTPException(status_code=401, detail="API key is missing")
        else:
            if api_key != self._secret_key:
                masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "*" * len(api_key)
                raise HTTPException(status_code=403, detail=f"Invalid API key: {masked_key}")
        return True
