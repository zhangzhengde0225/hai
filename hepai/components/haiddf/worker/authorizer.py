

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
        self._admin_key = None

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def admin_key(self):
        return self._admin_key

    @admin_key.setter
    def admin_key(self, value):
        self._admin_key = value

    async def api_key_auth(self, api_key: str = Depends(extract_api_key)):
        if self._secret_key is None:
            return True
        if not api_key:
            raise HTTPException(status_code=401, detail="API key is missing")
        if api_key != self._secret_key:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "*" * len(api_key)
            raise HTTPException(status_code=403, detail=f"Invalid API key: {masked_key}")
        return True

    async def admin_auth(self, key: str = Depends(extract_api_key)):
        """管理员认证：admin_key 或 secret_key 均可通过。未设置 admin_key 时允许所有访问。"""
        if self._admin_key is None:
            return True
        if not key:
            raise HTTPException(status_code=401, detail="Admin key is missing")
        if key == self._admin_key:
            return True
        if self._secret_key and key == self._secret_key:
            return True
        raise HTTPException(status_code=403, detail="Invalid admin key")
