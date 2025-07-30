"""
🔐 X自動反応ツール - 認証APIルーター（完全修正版）
ユーザー管理・APIキー管理・セッション管理
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, Field, ValidationError

from ..database.connection import get_db_session
from ..database.models import (
    User, UserCreate, UserResponse, UserUpdate, UserAPIKey,
    APIKeyCreate, APIKeyResponse,
    AutomationSettingsCreate, AutomationSettingsResponse
)
from ..auth.user_service import user_service, api_key_service, automation_service

# ログ設定
logger = logging.getLogger(__name__)

# セキュリティスキーム
security = HTTPBearer()

# ルーター作成
router = APIRouter(prefix="/api/auth", tags=["認証"])

# ===================================================================
# 📋 Pydantic Models
# ===================================================================

class LoginRequest(BaseModel):
    """ログインリクエスト（柔軟対応版）"""
    username_or_email: Optional[str] = Field(None, description="ユーザー名またはメールアドレス")
    username: Optional[str] = Field(None, description="ユーザー名（互換性用）")
    email: Optional[str] = Field(None, description="メールアドレス（互換性用）")
    password: str = Field(..., description="パスワード")
    
    def get_username_or_email(self) -> str:
        """フロントエンドの送信形式に柔軟対応"""
        if self.username_or_email:
            return self.username_or_email
        elif self.username:
            return self.username
        elif self.email:
            return self.email
        else:
            raise ValueError("ユーザー名またはメールアドレスが必要です")

class LoginResponse(BaseModel):
    """ログインレスポンス"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str = Field(..., description="現在のパスワード")
    new_password: str = Field(..., min_length=8, description="新しいパスワード")

class APIKeyTestRequest(BaseModel):
    """APIキーテストリクエスト"""
    user_password: str = Field(..., description="復号用ユーザーパスワード")

class ApiKeyValidationResponse(BaseModel):
    """APIキー検証レスポンス"""
    is_valid: bool
    x_username: Optional[str] = None
    x_user_id: Optional[str] = None
    permissions: Optional[list] = None
    error_message: Optional[str] = None

# ===================================================================
# 🔧 Dependency Functions
# ===================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """現在のユーザー取得（認証必須）"""
    user = await user_service.verify_session(credentials.credentials, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """アクティブユーザー取得"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="非アクティブなアカウントです"
        )
    return current_user

# ===================================================================
# 🔐 Authentication Endpoints
# ===================================================================

@router.post("/register", response_model=UserResponse, summary="ユーザー登録")
async def register_user(
    user_data: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
):
    """新規ユーザー登録"""
    try:
        logger.info(f"👤 ユーザー登録開始: {user_data.username}")
        
        # ユーザー名・メール重複チェック
        existing_user = await session.execute(
            select(User).where(
                (User.username == user_data.username) | 
                (User.email == user_data.email)
            )
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"❌ 重複ユーザー: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ユーザー名またはメールアドレスが既に使用されています"
            )
        
        # ユーザー作成
        new_user = await user_service.create_user(user_data, session)
        logger.info(f"✅ ユーザー登録完了: {new_user.username}")
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ユーザー登録エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー登録エラー: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse, summary="ログイン")  
async def login_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーログイン（詳細ログ付き）"""
    try:
        # リクエストボディを直接読み取り
        body = await request.body()
        logger.info(f"🔍 受信したリクエストボディ: {body.decode('utf-8')}")
        
        # リクエストヘッダー確認
        content_type = request.headers.get("content-type", "")
        logger.info(f"🔍 Content-Type: {content_type}")
        
        # JSON解析
        try:
            raw_data = json.loads(body.decode('utf-8'))
            logger.info(f"🔍 解析されたJSON: {raw_data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="無効なJSONフォーマットです"
            )
        
        # Pydanticバリデーション
        try:
            login_data = LoginRequest(**raw_data)
            logger.info(f"✅ Pydanticバリデーション成功")
        except ValidationError as e:
            logger.error(f"❌ Pydanticバリデーションエラー: {str(e)}")
            # より詳細なエラー情報を返す
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "リクエストデータが無効です",
                    "errors": e.errors(),
                    "received_data": raw_data
                }
            )
        
        # ユーザー名またはメールアドレス取得
        try:
            username_or_email = login_data.get_username_or_email()
            logger.info(f"🔍 ログイン試行ユーザー: {username_or_email}")
        except ValueError as e:
            logger.error(f"❌ ユーザー名取得エラー: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="ユーザー名またはメールアドレスが必要です"
            )
        
        # 認証
        logger.info(f"🔑 認証開始: {username_or_email}")
        user = await user_service.authenticate_user(
            username_or_email, 
            login_data.password, 
            session
        )
        
        if not user:
            logger.warning(f"❌ 認証失敗: {username_or_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザー名またはパスワードが正しくありません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ 認証成功: {user.username}")
        
        # セッション作成
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(f"🎫 セッション作成開始: user_id={user.id}, ip={client_ip}")
        
        session_data = await user_service.create_session(
            user.id, client_ip, user_agent, session
        )
        
        logger.info(f"✅ ログイン完了: {user.username}")
        
        return LoginResponse(
            **session_data,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ログインエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ログインエラー: {str(e)}"
        )

@router.post("/debug-login", summary="デバッグ用ログイン")
async def debug_login(request: Request):
    """デバッグ用：受信データを確認"""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info(f"🐛 Debug - Body: {body.decode('utf-8')}")
        logger.info(f"🐛 Debug - Headers: {headers}")
        
        return {
            "success": True,
            "body": body.decode('utf-8'),
            "headers": headers,
            "content_type": request.headers.get("content-type"),
            "method": request.method,
            "url": str(request.url)
        }
    except Exception as e:
        logger.error(f"🐛 Debug error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/logout", summary="ログアウト")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーログアウト"""
    try:
        logger.info(f"👋 ログアウト開始")
        success = await user_service.logout_user(credentials.credentials, session)
        
        if success:
            logger.info(f"✅ ログアウト成功")
            return {"message": "ログアウトしました"}
        else:
            logger.warning(f"⚠️ ログアウト失敗")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ログアウトに失敗しました"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ログアウトエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ログアウトエラー: {str(e)}"
        )

@router.get("/me", response_model=UserResponse, summary="ユーザー情報取得")
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """現在のユーザー情報取得"""
    return current_user

@router.put("/me", response_model=UserResponse, summary="ユーザー情報更新")
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """現在のユーザー情報更新"""
    try:
        logger.info(f"👤 ユーザー情報更新開始: {current_user.username}")
        
        # ユーザー情報更新
        stmt = select(User).where(User.id == current_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        
        # 更新可能フィールドのみ更新
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now(timezone.utc)  # 修正済み
        await session.commit()
        
        logger.info(f"✅ ユーザー情報更新完了: {current_user.username}")
        return UserResponse.model_validate(user)
        
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ ユーザー情報更新エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー情報更新エラー: {str(e)}"
        )

@router.post("/change-password", summary="パスワード変更")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """パスワード変更"""
    try:
        logger.info(f"🔐 パスワード変更開始: {current_user.username}")
        
        # 現在のパスワード確認
        authenticated_user = await user_service.authenticate_user(
            current_user.username, 
            password_data.current_password, 
            session
        )
        
        if not authenticated_user:
            logger.warning(f"❌ 現在のパスワード不一致: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="現在のパスワードが正しくありません"
            )
        
        # 新しいパスワードハッシュ化
        new_password_hash = user_service._hash_password(password_data.new_password)
        
        # パスワード更新
        stmt = select(User).where(User.id == current_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        
        user.password_hash = new_password_hash
        user.updated_at = datetime.now(timezone.utc)  # 修正済み
        
        await session.commit()
        
        logger.info(f"✅ パスワード変更完了: {current_user.username}")
        return {"message": "パスワードを変更しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ パスワード変更エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"パスワード変更エラー: {str(e)}"
        )

# ===================================================================
# 🔑 API Key Management Endpoints
# ===================================================================

@router.post("/api-keys", response_model=APIKeyResponse, summary="APIキー登録")
async def store_api_keys(
    api_data: APIKeyCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """X APIキー暗号化保存（運営者ブラインド）"""
    try:
        logger.info(f"🔐 APIキー登録開始: user_id={current_user.id}")
        
        # ユーザーパスワード確認
        authenticated_user = await user_service.authenticate_user(
            current_user.username, 
            api_data.user_password, 
            session
        )
        
        if not authenticated_user:
            logger.warning(f"❌ APIキー登録パスワード不一致: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="パスワードが正しくありません"
            )
        
        # APIキー暗号化保存
        api_key_response = await api_key_service.store_api_keys(
            current_user.id, api_data, session
        )
        
        logger.info(f"✅ APIキー登録完了: user_id={current_user.id}")
        return api_key_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ APIキー保存エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"APIキー保存エラー: {str(e)}"
        )

@router.get("/api-keys", response_model=APIKeyResponse, summary="APIキー状態取得")
async def get_api_key_status(
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """APIキー状態取得（復号なし）"""
    try:
        api_key_status = await api_key_service.get_api_key_status(current_user.id, session)
        
        if not api_key_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="APIキーが登録されていません"
            )
        
        return api_key_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ APIキー状態取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"APIキー状態取得エラー: {str(e)}"
        )

@router.post("/api-keys/test", response_model=ApiKeyValidationResponse, summary="APIキーテスト")
async def test_api_keys(
    test_data: APIKeyTestRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """APIキー接続テスト"""
    try:
        logger.info(f"🧪 APIキーテスト開始: user_id={current_user.id}")
        
        # APIキー復号
        api_keys = await api_key_service.get_decrypted_api_keys(
            current_user.id, test_data.user_password, session
        )
        
        if not api_keys:
            logger.warning(f"❌ APIキーテスト復号失敗: user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="APIキーの復号に失敗しました。パスワードを確認してください。"
            )
        
        # X API接続テスト（tweepy使用）
        try:
            import tweepy
            
            # OAuth 1.0a認証
            auth = tweepy.OAuth1UserHandler(
                api_keys["api_key"],
                api_keys["api_secret"],
                api_keys["access_token"],
                api_keys["access_token_secret"]
            )
            
            api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # 認証テスト（自分の情報取得）
            user_info = api.verify_credentials()
            
            if user_info:
                logger.info(f"✅ APIキーテスト成功: @{user_info.screen_name}")
                return ApiKeyValidationResponse(
                    is_valid=True,
                    x_username=user_info.screen_name,
                    x_user_id=str(user_info.id),
                    permissions=["read", "write"]  # TODO: 実際の権限確認
                )
            else:
                logger.warning(f"❌ X API認証失敗: user_id={current_user.id}")
                return ApiKeyValidationResponse(
                    is_valid=False,
                    error_message="X API認証に失敗しました"
                )
                
        except tweepy.TweepyException as e:
            logger.error(f"❌ X API エラー: {str(e)}")
            return ApiKeyValidationResponse(
                is_valid=False,
                error_message=f"X API エラー: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ APIキーテストエラー: {str(e)}")
        return ApiKeyValidationResponse(
            is_valid=False,
            error_message=f"APIキーテストエラー: {str(e)}"
        )

@router.delete("/api-keys", summary="APIキー削除")
async def delete_api_keys(
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """APIキー削除"""
    try:
        logger.info(f"🗑️ APIキー削除開始: user_id={current_user.id}")
        
        stmt = delete(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
        result = await session.execute(stmt)
        await session.commit()
        
        if result.rowcount > 0:
            logger.info(f"✅ APIキー削除完了: {result.rowcount}件削除")
            return {"message": "APIキーを削除しました"}
        else:
            logger.warning(f"⚠️ 削除対象APIキーなし: user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="削除するAPIキーが見つかりません"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ APIキー削除エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"APIキー削除エラー: {str(e)}"
        )

# ===================================================================
# ⚙️ Automation Settings Endpoints
# ===================================================================

@router.get("/automation", response_model=AutomationSettingsResponse, summary="自動化設定取得")
async def get_automation_settings(
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """自動化設定取得"""
    try:
        logger.info(f"⚙️ 自動化設定取得開始: user_id={current_user.id}")
        
        settings = await automation_service.get_automation_settings(current_user.id, session)
        
        if not settings:
            logger.warning(f"❌ 自動化設定なし: user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="自動化設定が見つかりません"
            )
        
        logger.info(f"✅ 自動化設定取得完了: user_id={current_user.id}")
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 自動化設定取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"自動化設定取得エラー: {str(e)}"
        )

@router.put("/automation", response_model=AutomationSettingsResponse, summary="自動化設定更新")
async def update_automation_settings(
    settings_data: AutomationSettingsCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """自動化設定更新"""
    try:
        logger.info(f"⚙️ 自動化設定更新開始: user_id={current_user.id}")
        
        updated_settings = await automation_service.update_automation_settings(
            current_user.id, settings_data, session
        )
        
        logger.info(f"✅ 自動化設定更新完了: user_id={current_user.id}")
        return updated_settings
        
    except Exception as e:
        logger.error(f"❌ 自動化設定更新エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"自動化設定更新エラー: {str(e)}"
        )

@router.post("/automation/toggle", summary="自動化ON/OFF切り替え")
async def toggle_automation(
    enabled: bool,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """自動化機能のON/OFF切り替え"""
    try:
        logger.info(f"🎛️ 自動化切り替え開始: user_id={current_user.id}, enabled={enabled}")
        
        success = await automation_service.toggle_automation(current_user.id, enabled, session)
        
        if success:
            logger.info(f"✅ 自動化切り替え完了: user_id={current_user.id}")
            return {"message": f"自動化機能を{'有効' if enabled else '無効'}にしました", "enabled": enabled}
        else:
            logger.warning(f"❌ 自動化切り替え失敗: user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="自動化設定の切り替えに失敗しました"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 自動化切り替えエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"自動化切り替えエラー: {str(e)}"
        )
