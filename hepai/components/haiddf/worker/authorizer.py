

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
        self._admin_password = None  # 管理员密码

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def admin_password(self):
        return self._admin_password

    @admin_password.setter
    def admin_password(self, value):
        self._admin_password = value


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

    async def admin_auth(self, admin_key: str = Depends(extract_api_key)):
        """
        管理员认证（用于模型管理功能）

        Args:
            admin_key: 从请求头中提取的管理员密码

        Returns:
            True if authentication successful

        Raises:
            HTTPException: 401 if password is missing, 403 if password is invalid
        """
        if self._admin_password is None:
            return True  # 如果未启用认证，允许访问
        if not admin_key:
            raise HTTPException(status_code=401, detail="Admin password is missing")
        if admin_key != self._admin_password:
            raise HTTPException(status_code=403, detail="Invalid admin password")
        return True
