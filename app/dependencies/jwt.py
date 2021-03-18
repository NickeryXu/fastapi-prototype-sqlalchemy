from fastapi import Depends, Header
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from typing import Optional

# custom defind
from app.dependencies.db import get_db
from app.dependencies.oauth import oauth2_scheme
from app.models.user import User, TokenPayload
from app.crud.user import get_user
from app.core.config import jwt_token_prefix, algorithm, secret_key


# Header中authorization信息校验，校验token的前缀
def _get_authorization_token(authorization: str = Header(...)):
    token_prefix, token = authorization.split(" ")
    if token_prefix != jwt_token_prefix:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="无效的授权"
        )
    return token


# 解密token，从db中获取用户信息
async def _get_current_user(db: Session = Depends(get_db),
                            token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, str(secret_key), algorithms=[algorithm])
        # TokenPayload可校验解密后内容
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="无效的授权"
        )
    dbuser = get_user(db, user_id=token_data.id)
    if not dbuser:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    return dbuser


# 公开内容，无token可访问
def _get_authorization_token_optional(authorization: str = Header(None)):
    if authorization:
        return _get_authorization_token(authorization)
    return ""


# 可选项，用户信息
async def _get_current_user_optional(db: Session = Depends(get_db),
                                     token: str = Depends(_get_authorization_token_optional), ) -> Optional[User]:
    if token:
        return await _get_current_user(db, token)

    return None


# 获取当前用户信息，required=True,必须拥有token才可访问，False,公开内容
def get_current_user_authorizer(*, required: bool = True):
    if required:
        return _get_current_user
    else:
        return _get_current_user_optional
