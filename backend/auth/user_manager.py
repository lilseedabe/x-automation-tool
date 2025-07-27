"""
ユーザー管理モジュール

このモジュールは以下の機能を提供します：
- ユーザー認証（JWT）
- ユーザー登録・管理
- パスワード暗号化
- セッション管理
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

# 暗号化・認証関連
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

# ログ
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# データモデル
# =============================================================================

class User(BaseModel):
    """ユーザーモデル"""
    user_id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    settings: Dict[str, Any] = {}

class UserCreate(BaseModel):
    """ユーザー作成モデル"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """ログインモデル"""
    username: str
    password: str

class Token(BaseModel):
    """トークンモデル"""
    access_token: str
    token_type: str
    expires_in: int

# =============================================================================
# ユーザー管理クラス
# =============================================================================

class UserManager:
    """
    ユーザー管理クラス
    
    ユーザーの認証、登録、管理を行います。
    """
    
    def __init__(self, data_path: str = "./data"):
        """
        初期化
        
        Args:
            data_path (str): データファイルの保存パス
        """
        self.data_path = Path(data_path)
        self.users_file = self.data_path / "users.json"
        
        # パスワード暗号化設定
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT設定
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", 1440))
        
        # データディレクトリ作成
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # ユーザーデータの初期化
        self._initialize_users_file()
        
        logger.info("UserManager初期化完了")
    
    def _initialize_users_file(self):
        """ユーザーファイルの初期化"""
        if not self.users_file.exists():
            initial_data = {
                "users": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
            logger.info("ユーザーファイルを初期化しました")
    
    def _load_users(self) -> Dict[str, Any]:
        """ユーザーデータの読み込み"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"ユーザーデータの読み込みエラー: {e}")
            return {"users": {}, "metadata": {}}
    
    def _save_users(self, data: Dict[str, Any]):
        """ユーザーデータの保存"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"ユーザーデータの保存エラー: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """パスワードのハッシュ化"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワードの検証"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def _generate_user_id(self) -> str:
        """一意のユーザーIDを生成"""
        return secrets.token_urlsafe(16)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """JWTアクセストークンの生成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWTトークンの検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"トークン検証失敗: {e}")
            return None
    
    def register_user(self, user_data: UserCreate) -> Optional[User]:
        """
        新規ユーザー登録
        
        Args:
            user_data (UserCreate): ユーザー作成データ
            
        Returns:
            Optional[User]: 作成されたユーザー情報
        """
        try:
            data = self._load_users()
            
            # ユーザー名・メールの重複チェック
            for user_info in data["users"].values():
                if user_info["username"] == user_data.username:
                    logger.warning(f"ユーザー名が重複: {user_data.username}")
                    return None
                if user_info["email"] == user_data.email:
                    logger.warning(f"メールアドレスが重複: {user_data.email}")
                    return None
            
            # 新規ユーザー作成
            user_id = self._generate_user_id()
            hashed_password = self._hash_password(user_data.password)
            
            user_info = {
                "user_id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "password_hash": hashed_password,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "settings": {}
            }
            
            # ユーザーデータに追加
            data["users"][user_id] = user_info
            self._save_users(data)
            
            # ユーザー専用ディレクトリ作成
            user_dir = self.data_path / "users" / f"user_{user_id}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # ユーザー情報を返す（パスワードハッシュは除外）
            user_dict = user_info.copy()
            del user_dict["password_hash"]
            user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
            
            logger.info(f"新規ユーザー登録完了: {user_data.username}")
            return User(**user_dict)
            
        except Exception as e:
            logger.error(f"ユーザー登録エラー: {e}")
            return None
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        ユーザー認証
        
        Args:
            login_data (UserLogin): ログインデータ
            
        Returns:
            Optional[User]: 認証されたユーザー情報
        """
        try:
            data = self._load_users()
            
            # ユーザー検索
            user_info = None
            for user_data in data["users"].values():
                if user_data["username"] == login_data.username:
                    user_info = user_data
                    break
            
            if not user_info:
                logger.warning(f"ユーザーが見つかりません: {login_data.username}")
                return None
            
            # パスワード検証
            if not self._verify_password(login_data.password, user_info["password_hash"]):
                logger.warning(f"パスワードが間違っています: {login_data.username}")
                return None
            
            # アクティブユーザーチェック
            if not user_info["is_active"]:
                logger.warning(f"非アクティブユーザー: {login_data.username}")
                return None
            
            # 最終ログイン時刻更新
            user_info["last_login"] = datetime.now().isoformat()
            self._save_users(data)
            
            # ユーザー情報を返す（パスワードハッシュは除外）
            user_dict = user_info.copy()
            del user_dict["password_hash"]
            user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
            if user_dict["last_login"]:
                user_dict["last_login"] = datetime.fromisoformat(user_dict["last_login"])
            
            logger.info(f"ユーザー認証成功: {login_data.username}")
            return User(**user_dict)
            
        except Exception as e:
            logger.error(f"ユーザー認証エラー: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        ユーザーIDでユーザー情報を取得
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            Optional[User]: ユーザー情報
        """
        try:
            data = self._load_users()
            
            if user_id not in data["users"]:
                return None
            
            user_info = data["users"][user_id]
            user_dict = user_info.copy()
            del user_dict["password_hash"]
            user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
            if user_dict["last_login"]:
                user_dict["last_login"] = datetime.fromisoformat(user_dict["last_login"])
            
            return User(**user_dict)
            
        except Exception as e:
            logger.error(f"ユーザー取得エラー: {e}")
            return None
    
    def update_user_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        ユーザー設定更新
        
        Args:
            user_id (str): ユーザーID
            settings (Dict[str, Any]): 更新する設定
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            data = self._load_users()
            
            if user_id not in data["users"]:
                logger.warning(f"ユーザーが見つかりません: {user_id}")
                return False
            
            data["users"][user_id]["settings"].update(settings)
            self._save_users(data)
            
            logger.info(f"ユーザー設定更新完了: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザー設定更新エラー: {e}")
            return False
    
    def list_users(self) -> List[User]:
        """
        全ユーザー一覧取得
        
        Returns:
            List[User]: ユーザー一覧
        """
        try:
            data = self._load_users()
            users = []
            
            for user_info in data["users"].values():
                user_dict = user_info.copy()
                del user_dict["password_hash"]
                user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
                if user_dict["last_login"]:
                    user_dict["last_login"] = datetime.fromisoformat(user_dict["last_login"])
                
                users.append(User(**user_dict))
            
            return users
            
        except Exception as e:
            logger.error(f"ユーザー一覧取得エラー: {e}")
            return []


# =============================================================================
# ユーティリティ関数
# =============================================================================

def get_current_user_from_token(token: str, user_manager: UserManager) -> Optional[User]:
    """
    トークンから現在のユーザーを取得
    
    Args:
        token (str): JWTトークン
        user_manager (UserManager): ユーザーマネージャー
        
    Returns:
        Optional[User]: 現在のユーザー
    """
    payload = user_manager.verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return user_manager.get_user_by_id(user_id)


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    # 基本テスト
    manager = UserManager("./test_data")
    
    # テストユーザー作成
    test_user_data = UserCreate(
        username="test_user",
        email="test@example.com",
        password="test_password",
        full_name="テストユーザー"
    )
    
    user = manager.register_user(test_user_data)
    if user:
        print(f"ユーザー作成成功: {user.username}")
        
        # ログインテスト
        login_data = UserLogin(username="test_user", password="test_password")
        auth_user = manager.authenticate_user(login_data)
        
        if auth_user:
            print(f"認証成功: {auth_user.username}")
            
            # トークン生成テスト
            token = manager.create_access_token({"sub": auth_user.user_id})
            print(f"トークン生成: {token[:50]}...")
            
            # トークン検証テスト
            payload = manager.verify_token(token)
            if payload:
                print(f"トークン検証成功: {payload['sub']}")
        else:
            print("認証失敗")
    else:
        print("ユーザー作成失敗")