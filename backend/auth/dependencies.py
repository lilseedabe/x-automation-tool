"""
🔐 X自動反応ツール - 認証依存関数
FastAPI依存関数（Dependency）を提供
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .user_service import user_service
from ..database.connection import get_db_session
from ..database.models import UserResponse
import logging

logger = logging.getLogger(__name__)

# HTTPBearer認証設定
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """現在の認証済みユーザーを取得"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # トークンからユーザー検証
    user = await user_service.verify_session(credentials.credentials, session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが無効または期限切れです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """現在のアクティブユーザーを取得"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効です"
        )
    
    return current_user

# エイリアス（後方互換性）
get_current_active_user_alias = get_current_active_user