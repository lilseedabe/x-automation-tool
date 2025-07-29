"""
👤 X自動反応ツール - ユーザー管理サービス
運営者ブラインド設計・暗号化対応
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from uuid import UUID

import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import jwt

from ..database.models import (
    User, UserAPIKey, AutomationSettings, UserSession,
    UserCreate, UserResponse, APIKeyCreate, APIKeyResponse,
    AutomationSettingsCreate, AutomationSettingsResponse
)
from ..database.connection import get_db_session
import logging

logger = logging.getLogger(__name__)

class UserService:
    """ユーザー管理サービス"""
    
    def __init__(self):
        self.jwt_secret = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = 24
        self.refresh_token_expire_days = 30
    
    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> UserResponse:
        """新規ユーザー作成"""
        try:
            # パスワードハッシュ化
            password_hash = self._hash_password(user_data.password)
            
            # ユーザー作成
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                timezone=user_data.timezone,
                language=user_data.language
            )
            
            session.add(db_user)
            await session.flush()  # IDを取得するため
            
            # デフォルト自動化設定作成
            automation_settings = AutomationSettings(
                user_id=db_user.id,
                is_enabled=False  # 最初は無効
            )
            session.add(automation_settings)
            
            await session.commit()
            
            logger.info(f"👤 新規ユーザー作成: {user_data.username}")
            return UserResponse.model_validate(db_user)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ ユーザー作成エラー: {str(e)}")
            raise
    
    async def authenticate_user(self, username_or_email: str, password: str, session: AsyncSession) -> Optional[UserResponse]:
        """ユーザー認証"""
        try:
            # ユーザー検索（username または email）
            stmt = select(User).where(
                (User.username == username_or_email) | 
                (User.email == username_or_email)
            ).where(User.is_active == True)
            
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # パスワード検証
            if not self._verify_password(password, user.password_hash):
                return None
            
            # 最終ログイン時刻更新
            user.last_login = datetime.now(timezone.utc)
            await session.commit()
            
            logger.info(f"🔑 ユーザー認証成功: {user.username}")
            return UserResponse.model_validate(user)
            
        except Exception as e:
            logger.error(f"❌ ユーザー認証エラー: {str(e)}")
            return None
    
    async def create_session(self, user_id: UUID, ip_address: str, user_agent: str, session: AsyncSession) -> Dict[str, str]:
        """セッション作成（JWT + DB保存）"""
        try:
            # JWT トークン生成
            access_token = self._create_access_token(user_id)
            refresh_token = secrets.token_urlsafe(32)
            
            # セッション情報をDBに保存
            db_session = UserSession(
                user_id=user_id,
                session_token=access_token[:50],  # 先頭50文字のみ保存（識別用）
                refresh_token=refresh_token,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=self.jwt_expire_hours),
                refresh_expires_at=datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            session.add(db_session)
            await session.commit()
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.jwt_expire_hours * 3600
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ セッション作成エラー: {str(e)}")
            raise
    
    async def verify_session(self, token: str, session: AsyncSession) -> Optional[UserResponse]:
        """セッション検証"""
        try:
            # JWT デコード
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = UUID(payload.get("sub"))
            
            # ユーザー存在確認
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # セッション存在確認
            token_prefix = token[:50]
            stmt = select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.session_token == token_prefix,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.now(timezone.utc)
            )
            result = await session.execute(stmt)
            user_session = result.scalar_one_or_none()
            
            if not user_session:
                return None
            
            # 最終アクセス時刻更新
            user_session.last_accessed = datetime.now(timezone.utc)
            await session.commit()
            
            return UserResponse.model_validate(user)
            
        except jwt.ExpiredSignatureError:
            logger.warning("🔑 期限切れトークン")
            return None
        except jwt.JWTError as e:
            logger.warning(f"🔑 無効なトークン: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ セッション検証エラー: {str(e)}")
            return None
    
    async def logout_user(self, token: str, session: AsyncSession) -> bool:
        """ユーザーログアウト"""
        try:
            token_prefix = token[:50]
            stmt = update(UserSession).where(
                UserSession.session_token == token_prefix
            ).values(is_active=False)
            
            await session.execute(stmt)
            await session.commit()
            
            logger.info("🔑 ユーザーログアウト")
            return True
            
        except Exception as e:
            logger.error(f"❌ ログアウトエラー: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """パスワード検証"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _create_access_token(self, user_id: UUID) -> str:
        """JWTアクセストークン作成"""
        expire = datetime.now(timezone.utc) + timedelta(hours=self.jwt_expire_hours)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

class APIKeyService:
    """APIキー管理サービス（運営者ブラインド設計）"""
    
    def __init__(self):
        self.encryption_algorithm = "AES-256-GCM"
    
    async def store_api_keys(self, user_id: UUID, api_data: APIKeyCreate, session: AsyncSession) -> APIKeyResponse:
        """APIキー暗号化保存（運営者ブラインド）"""
        try:
            # ユーザーパスワードベースの暗号化キー生成
            encryption_key, salt = self._derive_encryption_key(api_data.user_password, user_id)
            
            # APIキー暗号化
            encrypted_api_key = self._encrypt_data(api_data.api_key, encryption_key)
            encrypted_api_secret = self._encrypt_data(api_data.api_secret, encryption_key)
            encrypted_access_token = self._encrypt_data(api_data.access_token, encryption_key)
            encrypted_access_token_secret = self._encrypt_data(api_data.access_token_secret, encryption_key)
            
            # 既存APIキー削除（1ユーザー1セット）
            await session.execute(delete(UserAPIKey).where(UserAPIKey.user_id == user_id))
            
            # 暗号化されたAPIキー保存
            db_api_key = UserAPIKey(
                user_id=user_id,
                encrypted_api_key=encrypted_api_key,
                encrypted_api_secret=encrypted_api_secret,
                encrypted_access_token=encrypted_access_token,
                encrypted_access_token_secret=encrypted_access_token_secret,
                key_salt=salt,
                encryption_algorithm=self.encryption_algorithm
            )
            
            session.add(db_api_key)
            await session.commit()
            
            logger.info(f"🔐 APIキー暗号化保存完了: user_id={user_id}")
            return APIKeyResponse.model_validate(db_api_key)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ APIキー保存エラー: {str(e)}")
            raise
    
    async def get_decrypted_api_keys(self, user_id: UUID, user_password: str, session: AsyncSession) -> Optional[Dict[str, str]]:
        """APIキー復号（ユーザーパスワード必要）"""
        try:
            # APIキー取得
            stmt = select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.is_active == True
            )
            result = await session.execute(stmt)
            api_key_record = result.scalar_one_or_none()
            
            if not api_key_record:
                return None
            
            # 暗号化キー復元
            encryption_key = self._derive_encryption_key_from_salt(user_password, user_id, api_key_record.key_salt)
            
            # 復号
            api_key = self._decrypt_data(api_key_record.encrypted_api_key, encryption_key)
            api_secret = self._decrypt_data(api_key_record.encrypted_api_secret, encryption_key)
            access_token = self._decrypt_data(api_key_record.encrypted_access_token, encryption_key)
            access_token_secret = self._decrypt_data(api_key_record.encrypted_access_token_secret, encryption_key)
            
            # 最終使用時刻更新
            api_key_record.last_used = datetime.now(timezone.utc)
            api_key_record.usage_count += 1
            await session.commit()
            
            return {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }
            
        except Exception as e:
            logger.error(f"❌ APIキー復号エラー: {str(e)}")
            return None
    
    async def get_api_key_status(self, user_id: UUID, session: AsyncSession) -> Optional[APIKeyResponse]:
        """APIキー状態取得（復号なし）"""
        try:
            stmt = select(UserAPIKey).where(UserAPIKey.user_id == user_id)
            result = await session.execute(stmt)
            api_key_record = result.scalar_one_or_none()
            
            if not api_key_record:
                return None
            
            return APIKeyResponse.model_validate(api_key_record)
            
        except Exception as e:
            logger.error(f"❌ APIキー状態取得エラー: {str(e)}")
            return None
    
    def _derive_encryption_key(self, password: str, user_id: UUID) -> Tuple[bytes, bytes]:
        """ユーザーパスワードから暗号化キー導出"""
        # ユーザー固有のソルト生成
        salt = hashlib.sha256(f"{user_id}{secrets.token_hex(16)}".encode()).digest()
        
        # PBKDF2でキー導出
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        return key, salt
    
    def _derive_encryption_key_from_salt(self, password: str, user_id: UUID, salt: bytes) -> bytes:
        """既存ソルトから暗号化キー復元"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _encrypt_data(self, data: str, key: bytes) -> bytes:
        """AES-256-GCM暗号化"""
        # ランダムなnonce生成
        nonce = secrets.token_bytes(12)
        
        # 暗号化
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
        
        # nonce + tag + ciphertext の形式で保存
        return nonce + encryptor.tag + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> str:
        """AES-256-GCM復号"""
        # nonce, tag, ciphertext を分離
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # 復号
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode('utf-8')

class AutomationService:
    """自動化設定管理サービス"""
    
    async def get_automation_settings(self, user_id: UUID, session: AsyncSession) -> Optional[AutomationSettingsResponse]:
        """自動化設定取得"""
        try:
            stmt = select(AutomationSettings).where(AutomationSettings.user_id == user_id)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            
            if not settings:
                return None
            
            return AutomationSettingsResponse.model_validate(settings)
            
        except Exception as e:
            logger.error(f"❌ 自動化設定取得エラー: {str(e)}")
            return None
    
    async def update_automation_settings(self, user_id: UUID, settings_data: AutomationSettingsCreate, session: AsyncSession) -> AutomationSettingsResponse:
        """自動化設定更新"""
        try:
            stmt = select(AutomationSettings).where(AutomationSettings.user_id == user_id)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            
            if not settings:
                # 新規作成
                settings = AutomationSettings(user_id=user_id, **settings_data.model_dump())
                session.add(settings)
            else:
                # 更新
                for field, value in settings_data.model_dump().items():
                    setattr(settings, field, value)
                settings.updated_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            logger.info(f"⚙️ 自動化設定更新: user_id={user_id}")
            return AutomationSettingsResponse.model_validate(settings)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 自動化設定更新エラー: {str(e)}")
            raise
    
    async def toggle_automation(self, user_id: UUID, enabled: bool, session: AsyncSession) -> bool:
        """自動化ON/OFF切り替え"""
        try:
            stmt = update(AutomationSettings).where(
                AutomationSettings.user_id == user_id
            ).values(
                is_enabled=enabled,
                updated_at=datetime.now(timezone.utc)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                logger.info(f"🎛️ 自動化{'有効' if enabled else '無効'}: user_id={user_id}")
                return True
            
            return False
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 自動化切り替えエラー: {str(e)}")
            return False

# シングルトンインスタンス
user_service = UserService()
api_key_service = APIKeyService()
automation_service = AutomationService()