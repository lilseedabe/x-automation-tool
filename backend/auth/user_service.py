"""
👤 X自動反応ツール - ユーザー管理サービス（セッション重複修正版）
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
from jwt import InvalidTokenError  # 🔧 JWT例外を明示的にimport

from ..database.models import (
    User, UserAPIKey, AutomationSettings, UserSession,
    UserCreate, UserResponse, APIKeyCreate, APIKeyResponse,
    AutomationSettingsCreate, AutomationSettingsResponse
)
from ..database.connection import get_db_session
import logging

logger = logging.getLogger(__name__)

class UserService:
    """ユーザー管理サービス（修正版）"""
    
    def __init__(self):
        self.jwt_secret = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = 24
        self.refresh_token_expire_days = 30
        
        # デバッグ用ログ
        logger.info(f"🔧 UserService初期化 - JWT Secret設定: {'設定済み' if len(self.jwt_secret) > 20 else '未設定'}")
    
    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> UserResponse:
        """新規ユーザー作成"""
        try:
            logger.info(f"👤 ユーザー作成開始: {user_data.username}")
            
            # パスワードハッシュ化
            password_hash = self._hash_password(user_data.password)
            logger.debug(f"🔐 パスワードハッシュ化完了: {user_data.username}")
            
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
            logger.debug(f"👤 ユーザーDB保存完了: {db_user.id}")
            
            # デフォルト自動化設定作成
            automation_settings = AutomationSettings(
                user_id=db_user.id,
                is_enabled=False  # 最初は無効
            )
            session.add(automation_settings)
            
            await session.commit()
            
            logger.info(f"✅ 新規ユーザー作成完了: {user_data.username} (ID: {db_user.id})")
            return UserResponse.model_validate(db_user)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ ユーザー作成エラー: {str(e)}")
            raise
    
    async def authenticate_user(self, username_or_email: str, password: str, session: AsyncSession) -> Optional[UserResponse]:
        """ユーザー認証"""
        try:
            logger.info(f"🔑 認証開始: {username_or_email}")
            
            # ユーザー検索（username または email）
            stmt = select(User).where(
                (User.username == username_or_email) | 
                (User.email == username_or_email)
            ).where(User.is_active == True)
            
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"❌ ユーザーが見つかりません: {username_or_email}")
                return None
            
            logger.debug(f"👤 ユーザー発見: ID={user.id}, username={user.username}")
            
            # パスワード検証
            if not self._verify_password(password, user.password_hash):
                logger.warning(f"❌ パスワード不一致: {username_or_email}")
                return None
            
            logger.debug(f"✅ パスワード検証成功: {user.username}")
            
            # 最終ログイン時刻更新
            user.last_login = datetime.now(timezone.utc)
            await session.commit()
            
            logger.info(f"✅ ユーザー認証成功: {user.username} (ID: {user.id})")
            return UserResponse.model_validate(user)
            
        except Exception as e:
            logger.error(f"❌ ユーザー認証エラー ({username_or_email}): {str(e)}")
            return None
    
    async def create_session(self, user_id: UUID, ip_address: str, user_agent: str, session: AsyncSession) -> Dict[str, str]:
        """セッション作成（重複回避版）"""
        try:
            logger.info(f"🎫 セッション作成開始: user_id={user_id}")
            
            # 🔧 修正1: 既存のアクティブセッションを無効化（重複回避）
            logger.debug(f"🧹 既存セッションクリーンアップ: user_id={user_id}")
            cleanup_stmt = update(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).values(
                is_active=False,
                updated_at=datetime.now(timezone.utc)
            )
            cleanup_result = await session.execute(cleanup_stmt)
            if cleanup_result.rowcount > 0:
                logger.info(f"🗑️ 既存セッション無効化: {cleanup_result.rowcount}件")
            
            # 🔧 修正2: ユニークなセッショントークン生成
            timestamp = int(datetime.now().timestamp() * 1000)  # ミリ秒精度
            session_token = f"{user_id}_{secrets.token_urlsafe(16)}_{timestamp}"
            
            # 🔧 修正3: JWT生成（ランダム要素追加）
            jwt_payload = {
                "sub": str(user_id),
                "exp": datetime.now(timezone.utc) + timedelta(hours=self.jwt_expire_hours),
                "iat": datetime.now(timezone.utc),
                "jti": secrets.token_hex(8),  # ランダムなJWT ID
                "type": "access"
            }
            access_token = jwt.encode(jwt_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            refresh_token = secrets.token_urlsafe(32)
            
            logger.debug(f"🎫 トークン生成完了: session_token={session_token[:30]}...")
            
            # セッション情報をDBに保存
            db_session = UserSession(
                user_id=user_id,
                session_token=session_token,  # ユニークなセッショントークン
                refresh_token=refresh_token,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=self.jwt_expire_hours),
                refresh_expires_at=datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            session.add(db_session)
            await session.commit()
            
            logger.info(f"✅ セッション作成完了: user_id={user_id}, session_id={db_session.id}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.jwt_expire_hours * 3600
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ セッション作成エラー (user_id={user_id}): {str(e)}")
            raise
    
    async def verify_session(self, token: str, session: AsyncSession) -> Optional[UserResponse]:
        """セッション検証（JWT重視版）"""
        try:
            logger.debug(f"🔍 セッション検証開始: {token[:20]}...")
            
            # 🔧 修正: JWT検証を優先（DBセッションチェックは簡素化）
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                user_id = UUID(payload.get("sub"))
                logger.debug(f"🎫 JWT検証成功: user_id={user_id}")
            except jwt.ExpiredSignatureError:
                logger.warning("⏰ JWT期限切れ")
                return None
            except InvalidTokenError as e:
                logger.warning(f"❌ JWT無効: {str(e)}")
                return None
            
            # ユーザー存在確認
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"❌ ユーザーが見つからないか非アクティブ: {user_id}")
                return None
            
            logger.debug(f"✅ セッション検証完了: {user.username}")
            return UserResponse.model_validate(user)
            
        except Exception as e:
            logger.error(f"❌ セッション検証エラー: {str(e)}")
            return None
    
    async def verify_session_simple(self, token: str, session: AsyncSession) -> Optional[UserResponse]:
        """簡素化されたセッション検証（デバッグ用）"""
        try:
            logger.debug(f"🔍 簡易セッション検証: {token[:20]}...")
            
            # JWT デコードのみでセッション検証
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = UUID(payload.get("sub"))
            
            # ユーザー存在確認
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(f"✅ 簡易セッション検証成功: {user.username}")
                return UserResponse.model_validate(user)
            
            return None
            
        except (jwt.ExpiredSignatureError, InvalidTokenError) as e:
            logger.warning(f"❌ 簡易セッション検証失敗: {str(e)}")
            return None
    
    async def logout_user(self, token: str, session: AsyncSession) -> bool:
        """ユーザーログアウト（修正版）"""
        try:
            logger.info(f"👋 ログアウト開始: {token[:20] if token else 'None'}...")
            
            # 🔧 修正: トークンの存在確認
            if not token or token == "null" or token == "undefined":
                logger.warning("❌ 無効なトークンのためログアウト処理をスキップ")
                return False
            
            # 🔧 修正: JWTからuser_idを取得してセッション無効化
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                user_id = UUID(payload.get("sub"))
                logger.debug(f"🎫 JWT解析成功: user_id={user_id}")
            except InvalidTokenError as e:
                logger.warning(f"❌ JWT無効のためログアウト処理をスキップ: {str(e)}")
                return False
            
            # ユーザーの全アクティブセッションを無効化
            stmt = update(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).values(
                is_active=False,
                updated_at=datetime.now(timezone.utc)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ ログアウト成功: {result.rowcount}件のセッション無効化")
                return True
            else:
                logger.warning("⚠️ ログアウト: アクティブセッションなし")
                return True  # エラーではないのでTrue
            
        except Exception as e:
            logger.error(f"❌ ログアウトエラー: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        try:
            salt = bcrypt.gensalt(rounds=12)  # セキュリティ強化
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ パスワードハッシュ化エラー: {str(e)}")
            raise
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """パスワード検証"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"❌ パスワード検証エラー: {str(e)}")
            return False
    
    def _create_access_token(self, user_id: UUID) -> str:
        """JWTアクセストークン作成"""
        try:
            now = datetime.now(timezone.utc)
            expire = now + timedelta(hours=self.jwt_expire_hours)
            payload = {
                "sub": str(user_id),
                "exp": expire,
                "iat": now,
                "jti": secrets.token_hex(8),  # ランダム要素
                "type": "access"
            }
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            logger.debug(f"🎫 JWT作成成功: user_id={user_id}, expires={expire}")
            return token
        except Exception as e:
            logger.error(f"❌ JWT作成エラー: {str(e)}")
            raise

class APIKeyService:
    """APIキー管理サービス（運営者ブラインド設計）"""
    
    def __init__(self):
        self.encryption_algorithm = "AES-256-GCM"
        # セッションベースAPIキーキャッシュ（メモリ内）
        self._api_key_cache: Dict[str, Dict[str, str]] = {}
        self._cache_expires: Dict[str, datetime] = {}
        logger.info("🔐 APIKeyService初期化完了")
    
    def _generate_cache_key(self, user_id: UUID, session_token: str) -> str:
        """キャッシュキー生成"""
        return f"{user_id}_{hash(session_token)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """キャッシュ有効性確認"""
        if cache_key not in self._cache_expires:
            return False
        return datetime.now(timezone.utc) < self._cache_expires[cache_key]
    
    def _cache_api_keys(self, cache_key: str, api_keys: Dict[str, str], expires_at: datetime):
        """APIキーをキャッシュに保存"""
        self._api_key_cache[cache_key] = api_keys.copy()
        self._cache_expires[cache_key] = expires_at
        logger.debug(f"🔐 APIキーキャッシュ保存: key={cache_key[:20]}...")
    
    def _get_cached_api_keys(self, cache_key: str) -> Optional[Dict[str, str]]:
        """キャッシュからAPIキー取得"""
        if self._is_cache_valid(cache_key):
            logger.debug(f"🔐 APIキーキャッシュヒット: key={cache_key[:20]}...")
            return self._api_key_cache.get(cache_key)
        else:
            # 期限切れキャッシュを削除
            if cache_key in self._api_key_cache:
                del self._api_key_cache[cache_key]
            if cache_key in self._cache_expires:
                del self._cache_expires[cache_key]
            return None
    
    def _clear_user_cache(self, user_id: UUID):
        """ユーザーのキャッシュをクリア"""
        keys_to_remove = [key for key in self._api_key_cache.keys() if key.startswith(str(user_id))]
        for key in keys_to_remove:
            if key in self._api_key_cache:
                del self._api_key_cache[key]
            if key in self._cache_expires:
                del self._cache_expires[key]
        logger.debug(f"🧹 ユーザーキャッシュクリア: user_id={user_id}, {len(keys_to_remove)}件削除")
    
    async def store_api_keys(self, user_id: UUID, api_data: APIKeyCreate, session: AsyncSession) -> APIKeyResponse:
        """APIキー暗号化保存（運営者ブラインド）"""
        try:
            logger.info(f"🔐 APIキー保存開始: user_id={user_id}")
            
            # ユーザーパスワードベースの暗号化キー生成
            encryption_key, salt = self._derive_encryption_key(api_data.user_password, user_id)
            
            # APIキー暗号化
            encrypted_api_key = self._encrypt_data(api_data.api_key, encryption_key)
            encrypted_api_secret = self._encrypt_data(api_data.api_secret, encryption_key)
            encrypted_access_token = self._encrypt_data(api_data.access_token, encryption_key)
            encrypted_access_token_secret = self._encrypt_data(api_data.access_token_secret, encryption_key)
            
            # 既存APIキー削除（1ユーザー1セット）
            delete_result = await session.execute(delete(UserAPIKey).where(UserAPIKey.user_id == user_id))
            if delete_result.rowcount > 0:
                logger.info(f"🗑️ 既存APIキー削除: {delete_result.rowcount}件")
            
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
            
            logger.info(f"✅ APIキー暗号化保存完了: user_id={user_id}")
            return APIKeyResponse.model_validate(db_api_key)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ APIキー保存エラー (user_id={user_id}): {str(e)}")
            raise
    
    async def get_decrypted_api_keys(self, user_id: UUID, user_password: str, session: AsyncSession, session_token: Optional[str] = None) -> Optional[Dict[str, str]]:
        """APIキー復号（ユーザーパスワード必要・キャッシュ対応）"""
        try:
            logger.info(f"🔓 APIキー復号開始: user_id={user_id}")
            
            # キャッシュチェック（セッショントークンがある場合）
            if session_token:
                cache_key = self._generate_cache_key(user_id, session_token)
                cached_keys = self._get_cached_api_keys(cache_key)
                if cached_keys:
                    logger.info(f"✅ APIキーキャッシュから取得: user_id={user_id}")
                    return cached_keys
            
            # APIキー取得
            stmt = select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.is_active == True
            )
            result = await session.execute(stmt)
            api_key_record = result.scalar_one_or_none()
            
            if not api_key_record:
                logger.warning(f"❌ APIキーレコードが見つかりません: user_id={user_id}")
                return None
            
            # 暗号化キー復元
            try:
                encryption_key = self._derive_encryption_key_from_salt(user_password, user_id, api_key_record.key_salt)
            except Exception as e:
                logger.error(f"❌ 暗号化キー復元エラー: {str(e)}")
                return None
            
            # 復号
            try:
                api_key = self._decrypt_data(api_key_record.encrypted_api_key, encryption_key)
                api_secret = self._decrypt_data(api_key_record.encrypted_api_secret, encryption_key)
                access_token = self._decrypt_data(api_key_record.encrypted_access_token, encryption_key)
                access_token_secret = self._decrypt_data(api_key_record.encrypted_access_token_secret, encryption_key)
            except Exception as e:
                logger.error(f"❌ APIキー復号エラー: {str(e)}")
                return None
            
            # 復号結果
            decrypted_keys = {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }
            
            # キャッシュに保存（セッショントークンがある場合）
            if session_token:
                cache_key = self._generate_cache_key(user_id, session_token)
                # キャッシュ有効期限は6時間
                cache_expires = datetime.now(timezone.utc) + timedelta(hours=6)
                self._cache_api_keys(cache_key, decrypted_keys, cache_expires)
            
            # 最終使用時刻更新
            api_key_record.last_used = datetime.now(timezone.utc)
            api_key_record.usage_count += 1
            await session.commit()
            
            logger.info(f"✅ APIキー復号完了: user_id={user_id}")
            return decrypted_keys
            
        except Exception as e:
            logger.error(f"❌ APIキー復号エラー (user_id={user_id}): {str(e)}")
            return None
    
    async def get_cached_api_keys_by_token(self, user_id: UUID, session_token: str) -> Optional[Dict[str, str]]:
        """セッショントークンからキャッシュされたAPIキー取得"""
        try:
            cache_key = self._generate_cache_key(user_id, session_token)
            cached_keys = self._get_cached_api_keys(cache_key)
            if cached_keys:
                logger.info(f"✅ セッションAPIキーキャッシュヒット: user_id={user_id}")
                return cached_keys
            else:
                logger.debug(f"⚠️ セッションAPIキーキャッシュミス: user_id={user_id}")
                return None
        except Exception as e:
            logger.error(f"❌ セッションAPIキー取得エラー: {str(e)}")
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
            logger.error(f"❌ APIキー状態取得エラー (user_id={user_id}): {str(e)}")
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
    
    def __init__(self):
        logger.info("⚙️ AutomationService初期化完了")
    
    async def get_automation_settings(self, user_id: UUID, session: AsyncSession) -> Optional[AutomationSettingsResponse]:
        """自動化設定取得"""
        try:
            stmt = select(AutomationSettings).where(AutomationSettings.user_id == user_id)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            
            if not settings:
                logger.info(f"⚙️ 自動化設定が見つかりません: user_id={user_id}")
                return None
            
            return AutomationSettingsResponse.model_validate(settings)
            
        except Exception as e:
            logger.error(f"❌ 自動化設定取得エラー (user_id={user_id}): {str(e)}")
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
                logger.info(f"⚙️ 新規自動化設定作成: user_id={user_id}")
            else:
                # 更新
                for field, value in settings_data.model_dump().items():
                    setattr(settings, field, value)
                settings.updated_at = datetime.now(timezone.utc)
                logger.info(f"⚙️ 自動化設定更新: user_id={user_id}")
            
            await session.commit()
            
            return AutomationSettingsResponse.model_validate(settings)
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 自動化設定更新エラー (user_id={user_id}): {str(e)}")
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
            else:
                logger.warning(f"⚠️ 自動化設定が見つかりません: user_id={user_id}")
                return False
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 自動化切り替えエラー (user_id={user_id}): {str(e)}")
            return False

# シングルトンインスタンス
user_service = UserService()
api_key_service = APIKeyService()
automation_service = AutomationService()
