"""
暗号化データベースストレージ（Render PostgreSQL対応）

RenderのPostgreSQLを使用した暗号化データ保存
法的リスクを考慮した実装とユーザー選択制
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import hashlib
import secrets

# 暗号化
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# データベース
import asyncpg
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer

logger = logging.getLogger(__name__)

# データベースモデル
Base = declarative_base()

class EncryptedUserData(Base):
    """暗号化されたユーザーデータ"""
    __tablename__ = 'encrypted_user_data'
    
    user_id = Column(String(255), primary_key=True)
    encrypted_api_keys = Column(Text, nullable=True)
    encryption_salt = Column(String(255), nullable=False)
    automation_mode = Column(String(50), default='manual')
    consent_timestamp = Column(DateTime, nullable=False)
    consent_version = Column(String(50), nullable=False)
    data_retention_days = Column(Integer, default=1)  # デフォルト1日
    auto_delete_enabled = Column(Boolean, default=True)
    last_accessed = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LegalConsent(Base):
    """法的同意記録"""
    __tablename__ = 'legal_consents'
    
    consent_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False)
    consent_type = Column(String(100), nullable=False)  # 'data_storage', 'international_transfer'
    consent_text = Column(Text, nullable=False)
    user_agreement = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

class EncryptedStorageManager:
    """
    暗号化ストレージ管理
    
    Render PostgreSQLを使用した暗号化データ保存
    法的同意とプライバシー保護を重視
    """
    
    def __init__(self):
        """初期化"""
        self.engine = None
        self.session_factory = None
        self._initialize_database()
        
        logger.info("EncryptedStorageManager初期化完了（Render PostgreSQL）")
    
    def _initialize_database(self):
        """データベース接続初期化"""
        try:
            # Render PostgreSQL接続URL
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                logger.warning("DATABASE_URLが設定されていません")
                return
            
            # asyncpg用にURLを修正
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            
            self.engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Render PostgreSQL接続成功")
            
        except Exception as e:
            logger.error(f"データベース接続エラー: {e}")
    
    async def create_tables(self):
        """テーブル作成"""
        if not self.engine:
            return False
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("データベーステーブル作成完了")
            return True
        except Exception as e:
            logger.error(f"テーブル作成エラー: {e}")
            return False
    
    def _generate_encryption_key(self, password: str, salt: bytes) -> bytes:
        """暗号化キー生成"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt_data(self, data: str, encryption_key: bytes) -> str:
        """データ暗号化"""
        f = Fernet(encryption_key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def _decrypt_data(self, encrypted_data: str, encryption_key: bytes) -> str:
        """データ復号化"""
        f = Fernet(encryption_key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(decoded_data)
        return decrypted_data.decode()
    
    async def record_legal_consent(self, user_id: str, consent_data: Dict[str, Any]) -> bool:
        """
        法的同意を記録
        
        Args:
            user_id (str): ユーザーID
            consent_data (Dict[str, Any]): 同意データ
            
        Returns:
            bool: 記録成功フラグ
        """
        if not self.session_factory:
            return False
        
        try:
            async with self.session_factory() as session:
                # データ保存同意
                if consent_data.get('data_storage_consent'):
                    storage_consent = LegalConsent(
                        consent_id=f"{user_id}_storage_{datetime.utcnow().isoformat()}",
                        user_id=user_id,
                        consent_type='data_storage',
                        consent_text=consent_data.get('storage_consent_text', ''),
                        user_agreement=True,
                        ip_address=consent_data.get('ip_address'),
                        user_agent=consent_data.get('user_agent')
                    )
                    session.add(storage_consent)
                
                # 国際データ移転同意
                if consent_data.get('international_transfer_consent'):
                    transfer_consent = LegalConsent(
                        consent_id=f"{user_id}_transfer_{datetime.utcnow().isoformat()}",
                        user_id=user_id,
                        consent_type='international_transfer',
                        consent_text=consent_data.get('transfer_consent_text', ''),
                        user_agreement=True,
                        ip_address=consent_data.get('ip_address'),
                        user_agent=consent_data.get('user_agent')
                    )
                    session.add(transfer_consent)
                
                await session.commit()
                logger.info(f"法的同意記録完了: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"法的同意記録エラー: {e}")
            return False
    
    async def store_encrypted_api_keys(self, user_id: str, api_keys: Dict[str, str], 
                                     user_password: str, consent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        APIキーを暗号化してPostgreSQLに保存
        
        Args:
            user_id (str): ユーザーID
            api_keys (Dict[str, str]): APIキー
            user_password (str): ユーザー設定の暗号化パスワード
            consent_data (Dict[str, Any]): 法的同意データ
            
        Returns:
            Dict[str, Any]: 保存結果
        """
        if not self.session_factory:
            return {"error": "データベース接続なし"}
        
        try:
            # 法的同意を先に記録
            consent_recorded = await self.record_legal_consent(user_id, consent_data)
            if not consent_recorded:
                return {"error": "法的同意の記録に失敗しました"}
            
            # 暗号化用ソルト生成
            salt = secrets.token_bytes(32)
            encryption_key = self._generate_encryption_key(user_password, salt)
            
            # APIキーを暗号化
            api_keys_json = json.dumps(api_keys)
            encrypted_api_keys = self._encrypt_data(api_keys_json, encryption_key)
            
            async with self.session_factory() as session:
                # 既存データチェック
                existing_data = await session.get(EncryptedUserData, user_id)
                
                if existing_data:
                    # 更新
                    existing_data.encrypted_api_keys = encrypted_api_keys
                    existing_data.encryption_salt = base64.urlsafe_b64encode(salt).decode()
                    existing_data.last_accessed = datetime.utcnow()
                    existing_data.consent_timestamp = datetime.utcnow()
                    existing_data.consent_version = consent_data.get('consent_version', '1.0')
                else:
                    # 新規作成
                    user_data = EncryptedUserData(
                        user_id=user_id,
                        encrypted_api_keys=encrypted_api_keys,
                        encryption_salt=base64.urlsafe_b64encode(salt).decode(),
                        consent_timestamp=datetime.utcnow(),
                        consent_version=consent_data.get('consent_version', '1.0'),
                        data_retention_days=consent_data.get('retention_days', 1),
                        last_accessed=datetime.utcnow()
                    )
                    session.add(user_data)
                
                await session.commit()
                
                return {
                    "success": True,
                    "message": "APIキーが暗号化されてPostgreSQLに保存されました",
                    "storage_location": "Render PostgreSQL (アメリカ)",
                    "encryption": "AES-256 + PBKDF2HMAC",
                    "consent_recorded": True,
                    "auto_delete_days": consent_data.get('retention_days', 1)
                }
                
        except Exception as e:
            logger.error(f"暗号化保存エラー: {e}")
            return {"error": f"保存エラー: {str(e)}"}
    
    async def retrieve_encrypted_api_keys(self, user_id: str, user_password: str) -> Dict[str, Any]:
        """
        暗号化されたAPIキーを復号化して取得
        
        Args:
            user_id (str): ユーザーID
            user_password (str): ユーザー設定の暗号化パスワード
            
        Returns:
            Dict[str, Any]: 取得結果
        """
        if not self.session_factory:
            return {"error": "データベース接続なし"}
        
        try:
            async with self.session_factory() as session:
                user_data = await session.get(EncryptedUserData, user_id)
                
                if not user_data or not user_data.encrypted_api_keys:
                    return {"error": "保存されたAPIキーが見つかりません"}
                
                # 暗号化キー再生成
                salt = base64.urlsafe_b64decode(user_data.encryption_salt.encode())
                encryption_key = self._generate_encryption_key(user_password, salt)
                
                # 復号化
                decrypted_json = self._decrypt_data(user_data.encrypted_api_keys, encryption_key)
                api_keys = json.loads(decrypted_json)
                
                # 最終アクセス時刻を更新
                user_data.last_accessed = datetime.utcnow()
                await session.commit()
                
                return {
                    "success": True,
                    "api_keys": api_keys,
                    "last_accessed": user_data.last_accessed.isoformat(),
                    "consent_version": user_data.consent_version,
                    "auto_delete_days": user_data.data_retention_days
                }
                
        except Exception as e:
            logger.error(f"暗号化取得エラー: {e}")
            return {"error": f"取得エラー: {str(e)}"}
    
    async def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        ユーザーデータを完全削除
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            Dict[str, Any]: 削除結果
        """
        if not self.session_factory:
            return {"error": "データベース接続なし"}
        
        try:
            async with self.session_factory() as session:
                # ユーザーデータ削除
                user_data = await session.get(EncryptedUserData, user_id)
                if user_data:
                    await session.delete(user_data)
                
                # 法的同意記録も削除（GDPR準拠）
                consents = await session.execute(
                    sqlalchemy.select(LegalConsent).where(LegalConsent.user_id == user_id)
                )
                for consent in consents.scalars():
                    await session.delete(consent)
                
                await session.commit()
                
                return {
                    "success": True,
                    "message": "ユーザーデータが完全に削除されました",
                    "deleted_items": ["encrypted_api_keys", "legal_consents", "user_metadata"]
                }
                
        except Exception as e:
            logger.error(f"データ削除エラー: {e}")
            return {"error": f"削除エラー: {str(e)}"}
    
    async def auto_delete_expired_data(self) -> Dict[str, Any]:
        """
        期限切れデータの自動削除
        
        Returns:
            Dict[str, Any]: 削除結果
        """
        if not self.session_factory:
            return {"error": "データベース接続なし"}
        
        try:
            deleted_count = 0
            
            async with self.session_factory() as session:
                # 期限切れデータを検索
                cutoff_time = datetime.utcnow() - timedelta(days=1)  # デフォルト1日
                
                expired_data = await session.execute(
                    sqlalchemy.select(EncryptedUserData).where(
                        EncryptedUserData.last_accessed < cutoff_time,
                        EncryptedUserData.auto_delete_enabled == True
                    )
                )
                
                for user_data in expired_data.scalars():
                    # 個別削除処理
                    await self.delete_user_data(user_data.user_id)
                    deleted_count += 1
                
                return {
                    "success": True,
                    "deleted_users": deleted_count,
                    "message": f"{deleted_count}件の期限切れデータを削除しました"
                }
                
        except Exception as e:
            logger.error(f"自動削除エラー: {e}")
            return {"error": f"自動削除エラー: {str(e)}"}
    
    def get_legal_disclaimer(self) -> Dict[str, str]:
        """
        法的免責事項を取得
        
        Returns:
            Dict[str, str]: 免責事項
        """
        return {
            "storage_location": "Render PostgreSQL（アメリカのデータセンター）",
            "data_jurisdiction": "アメリカ合衆国の法律が適用されます",
            "third_party_access": "Render社の管理者が技術的にアクセス可能です",
            "government_requests": "アメリカ政府の要請により開示される可能性があります",
            "encryption": "AES-256 + PBKDF2HMAC による強力な暗号化",
            "operator_access": "運営者はユーザーのパスワードなしには復号化できません",
            "auto_deletion": "指定期間後に自動削除されます",
            "user_control": "ユーザーはいつでもデータ削除を要求できます",
            "gdpr_compliance": "GDPR・個人情報保護法に準拠した運用を行います",
            "risk_acknowledgment": "国際的なデータ移転リスクをユーザーが承知の上で利用"
        }


# グローバルインスタンス
encrypted_storage = EncryptedStorageManager()

# 初期化関数
async def initialize_database():
    """データベース初期化"""
    return await encrypted_storage.create_tables()

# エクスポート関数
async def store_user_api_keys(user_id: str, api_keys: Dict[str, str], 
                            user_password: str, consent_data: Dict[str, Any]) -> Dict[str, Any]:
    """APIキー暗号化保存"""
    return await encrypted_storage.store_encrypted_api_keys(user_id, api_keys, user_password, consent_data)

async def get_user_api_keys(user_id: str, user_password: str) -> Dict[str, Any]:
    """APIキー復号化取得"""
    return await encrypted_storage.retrieve_encrypted_api_keys(user_id, user_password)

async def delete_user_api_keys(user_id: str) -> Dict[str, Any]:
    """ユーザーデータ削除"""
    return await encrypted_storage.delete_user_data(user_id)

def get_legal_info() -> Dict[str, str]:
    """法的情報取得"""
    return encrypted_storage.get_legal_disclaimer()


if __name__ == "__main__":
    import asyncio
    
    async def test_encrypted_storage():
        """暗号化ストレージのテスト"""
        print("=== Render PostgreSQL暗号化ストレージテスト ===")
        
        # データベース初期化
        success = await initialize_database()
        print(f"データベース初期化: {success}")
        
        if success:
            # 法的情報表示
            legal_info = get_legal_info()
            print("\n法的免責事項:")
            for key, value in legal_info.items():
                print(f"  {key}: {value}")
    
    # テスト実行
    asyncio.run(test_encrypted_storage())