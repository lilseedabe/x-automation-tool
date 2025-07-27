"""
API認証情報管理モジュール

このモジュールは以下の機能を提供します：
- API認証情報の暗号化保存
- X API、Groq AI API等の認証情報管理
- セキュアなキー管理
- アクセス権限制御
"""

import os
import json
import base64
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime

# 暗号化関連
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ログ
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# データモデル
# =============================================================================

class APICredentials:
    """API認証情報モデル"""
    
    def __init__(self, service: str, credentials: Dict[str, str], metadata: Dict[str, Any] = None):
        self.service = service
        self.credentials = credentials
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

# =============================================================================
# API認証情報管理クラス
# =============================================================================

class APIManager:
    """
    API認証情報管理クラス
    
    各ユーザーのAPI認証情報を暗号化して安全に保存・管理します。
    """
    
    def __init__(self, data_path: str = "./data"):
        """
        初期化
        
        Args:
            data_path (str): データファイルの保存パス
        """
        self.data_path = Path(data_path)
        
        # 暗号化キーの初期化
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # データディレクトリ作成
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("APIManager初期化完了")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """暗号化キーの取得または生成"""
        # 環境変数から暗号化キーを取得
        env_key = os.getenv("ENCRYPTION_KEY")
        
        if env_key and len(env_key) >= 32:
            # 環境変数からキーを導出
            password = env_key.encode()
            salt = b'salt1234567890ab'  # 本番環境では動的に生成
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
        else:
            # キーファイルから読み込み、存在しない場合は生成
            key_file = self.data_path / ".encryption_key"
            
            if key_file.exists():
                try:
                    with open(key_file, 'rb') as f:
                        return f.read()
                except Exception as e:
                    logger.warning(f"暗号化キーの読み込みに失敗: {e}")
            
            # 新しいキーを生成
            key = Fernet.generate_key()
            try:
                with open(key_file, 'wb') as f:
                    f.write(key)
                # ファイルの権限を制限
                os.chmod(key_file, 0o600)
                logger.info("新しい暗号化キーを生成しました")
            except Exception as e:
                logger.error(f"暗号化キーの保存に失敗: {e}")
            
            return key
    
    def _get_user_api_file(self, user_id: str) -> Path:
        """ユーザーのAPI認証情報ファイルパスを取得"""
        user_dir = self.data_path / "users" / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "api_keys.json"
    
    def _encrypt_data(self, data: str) -> str:
        """データの暗号化"""
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"データ暗号化エラー: {e}")
            raise
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """データの復号化"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"データ復号化エラー: {e}")
            raise
    
    def _load_user_apis(self, user_id: str) -> Dict[str, Any]:
        """ユーザーのAPI認証情報を読み込み"""
        api_file = self._get_user_api_file(user_id)
        
        if not api_file.exists():
            return {
                "services": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"API認証情報の読み込みエラー: {e}")
            return {"services": {}, "metadata": {}}
    
    def _save_user_apis(self, user_id: str, data: Dict[str, Any]):
        """ユーザーのAPI認証情報を保存"""
        api_file = self._get_user_api_file(user_id)
        
        try:
            with open(api_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # ファイルの権限を制限
            os.chmod(api_file, 0o600)
        except Exception as e:
            logger.error(f"API認証情報の保存エラー: {e}")
            raise
    
    def store_api_credentials(self, user_id: str, service: str, credentials: Dict[str, str], metadata: Dict[str, Any] = None) -> bool:
        """
        API認証情報を保存
        
        Args:
            user_id (str): ユーザーID
            service (str): サービス名（x_api, groq_ai等）
            credentials (Dict[str, str]): 認証情報
            metadata (Dict[str, Any]): メタデータ
            
        Returns:
            bool: 保存成功フラグ
        """
        try:
            data = self._load_user_apis(user_id)
            
            # 認証情報を暗号化
            encrypted_credentials = {}
            for key, value in credentials.items():
                encrypted_credentials[key] = self._encrypt_data(value)
            
            # サービス情報を構築
            service_data = {
                "credentials": encrypted_credentials,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # データに追加
            data["services"][service] = service_data
            self._save_user_apis(user_id, data)
            
            logger.info(f"API認証情報保存完了: user={user_id}, service={service}")
            return True
            
        except Exception as e:
            logger.error(f"API認証情報保存エラー: {e}")
            return False
    
    def get_api_credentials(self, user_id: str, service: str) -> Optional[Dict[str, str]]:
        """
        API認証情報を取得
        
        Args:
            user_id (str): ユーザーID
            service (str): サービス名
            
        Returns:
            Optional[Dict[str, str]]: 復号化された認証情報
        """
        try:
            data = self._load_user_apis(user_id)
            
            if service not in data["services"]:
                logger.warning(f"サービスが見つかりません: user={user_id}, service={service}")
                return None
            
            service_data = data["services"][service]
            encrypted_credentials = service_data["credentials"]
            
            # 認証情報を復号化
            decrypted_credentials = {}
            for key, encrypted_value in encrypted_credentials.items():
                decrypted_credentials[key] = self._decrypt_data(encrypted_value)
            
            logger.info(f"API認証情報取得完了: user={user_id}, service={service}")
            return decrypted_credentials
            
        except Exception as e:
            logger.error(f"API認証情報取得エラー: {e}")
            return None
    
    def update_api_credentials(self, user_id: str, service: str, credentials: Dict[str, str]) -> bool:
        """
        API認証情報を更新
        
        Args:
            user_id (str): ユーザーID
            service (str): サービス名
            credentials (Dict[str, str]): 新しい認証情報
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            data = self._load_user_apis(user_id)
            
            if service not in data["services"]:
                logger.warning(f"更新対象のサービスが見つかりません: user={user_id}, service={service}")
                return False
            
            # 既存のメタデータを保持
            existing_metadata = data["services"][service].get("metadata", {})
            existing_created_at = data["services"][service].get("created_at")
            
            # 認証情報を暗号化
            encrypted_credentials = {}
            for key, value in credentials.items():
                encrypted_credentials[key] = self._encrypt_data(value)
            
            # サービス情報を更新
            data["services"][service] = {
                "credentials": encrypted_credentials,
                "metadata": existing_metadata,
                "created_at": existing_created_at,
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_user_apis(user_id, data)
            
            logger.info(f"API認証情報更新完了: user={user_id}, service={service}")
            return True
            
        except Exception as e:
            logger.error(f"API認証情報更新エラー: {e}")
            return False
    
    def delete_api_credentials(self, user_id: str, service: str) -> bool:
        """
        API認証情報を削除
        
        Args:
            user_id (str): ユーザーID
            service (str): サービス名
            
        Returns:
            bool: 削除成功フラグ
        """
        try:
            data = self._load_user_apis(user_id)
            
            if service not in data["services"]:
                logger.warning(f"削除対象のサービスが見つかりません: user={user_id}, service={service}")
                return False
            
            del data["services"][service]
            self._save_user_apis(user_id, data)
            
            logger.info(f"API認証情報削除完了: user={user_id}, service={service}")
            return True
            
        except Exception as e:
            logger.error(f"API認証情報削除エラー: {e}")
            return False
    
    def list_user_services(self, user_id: str) -> Dict[str, Any]:
        """
        ユーザーの登録済みサービス一覧を取得
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            Dict[str, Any]: サービス一覧（認証情報は除外）
        """
        try:
            data = self._load_user_apis(user_id)
            services_info = {}
            
            for service, service_data in data["services"].items():
                services_info[service] = {
                    "metadata": service_data.get("metadata", {}),
                    "created_at": service_data.get("created_at"),
                    "updated_at": service_data.get("updated_at"),
                    "has_credentials": bool(service_data.get("credentials"))
                }
            
            return services_info
            
        except Exception as e:
            logger.error(f"サービス一覧取得エラー: {e}")
            return {}
    
    def validate_api_credentials(self, user_id: str, service: str) -> bool:
        """
        API認証情報の有効性をチェック
        
        Args:
            user_id (str): ユーザーID
            service (str): サービス名
            
        Returns:
            bool: 認証情報の有効性
        """
        credentials = self.get_api_credentials(user_id, service)
        
        if not credentials:
            return False
        
        # サービス別の検証ロジック
        if service == "x_api":
            required_keys = ["api_key", "api_secret", "access_token", "access_token_secret"]
            return all(key in credentials and credentials[key] for key in required_keys)
        
        elif service == "groq_ai":
            return "api_key" in credentials and credentials["api_key"]
        
        # その他のサービス
        return bool(credentials)


# =============================================================================
# サービス固有のヘルパー関数
# =============================================================================

def store_x_api_credentials(api_manager: APIManager, user_id: str, 
                           api_key: str, api_secret: str, 
                           access_token: str, access_token_secret: str,
                           bearer_token: str = None) -> bool:
    """
    X API認証情報を保存
    
    Args:
        api_manager (APIManager): APIマネージャー
        user_id (str): ユーザーID
        api_key (str): APIキー
        api_secret (str): APIシークレット
        access_token (str): アクセストークン
        access_token_secret (str): アクセストークンシークレット
        bearer_token (str): ベアラートークン（オプション）
        
    Returns:
        bool: 保存成功フラグ
    """
    credentials = {
        "api_key": api_key,
        "api_secret": api_secret,
        "access_token": access_token,
        "access_token_secret": access_token_secret
    }
    
    if bearer_token:
        credentials["bearer_token"] = bearer_token
    
    metadata = {
        "service_name": "X (Twitter) API",
        "api_version": "v2",
        "description": "X API v2 認証情報"
    }
    
    return api_manager.store_api_credentials(user_id, "x_api", credentials, metadata)

def store_groq_ai_credentials(api_manager: APIManager, user_id: str, api_key: str) -> bool:
    """
    Groq AI API認証情報を保存
    
    Args:
        api_manager (APIManager): APIマネージャー
        user_id (str): ユーザーID
        api_key (str): APIキー
        
    Returns:
        bool: 保存成功フラグ
    """
    credentials = {
        "api_key": api_key
    }
    
    metadata = {
        "service_name": "Groq AI",
        "description": "Groq AI API認証情報"
    }
    
    return api_manager.store_api_credentials(user_id, "groq_ai", credentials, metadata)


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    # 基本テスト
    manager = APIManager("./test_data")
    
    # テストユーザーID
    test_user_id = "test_user_123"
    
    # X API認証情報テスト
    success = store_x_api_credentials(
        manager, test_user_id,
        "test_api_key", "test_api_secret",
        "test_access_token", "test_access_token_secret",
        "test_bearer_token"
    )
    
    if success:
        print("X API認証情報保存成功")
        
        # 取得テスト
        credentials = manager.get_api_credentials(test_user_id, "x_api")
        if credentials:
            print(f"X API認証情報取得成功: {list(credentials.keys())}")
        
        # サービス一覧テスト
        services = manager.list_user_services(test_user_id)
        print(f"登録済みサービス: {list(services.keys())}")
        
        # 検証テスト
        is_valid = manager.validate_api_credentials(test_user_id, "x_api")
        print(f"X API認証情報有効性: {is_valid}")
    else:
        print("X API認証情報保存失敗")
    
    # Groq AI認証情報テスト
    success = store_groq_ai_credentials(manager, test_user_id, "test_groq_api_key")
    
    if success:
        print("Groq AI認証情報保存成功")
    else:
        print("Groq AI認証情報保存失敗")