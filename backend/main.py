"""
🤖 X自動反応ツール - メインアプリケーション（シンVPS統一版 + 認証機能）

シンVPS + 運営者ブラインド・ストレージに統一
ローカルファイル保存は廃止
ユーザー認証機能を追加
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# FastAPI関連
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# データベース関連
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# 認証関連
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt

# 内部モジュール
from backend.config.storage_config import get_storage_config, is_shin_vps_mode
from backend.infrastructure.operator_blind_storage import (
    operator_blind_storage,
    store_user_data_operator_blind,
    get_user_data_operator_blind,
    delete_user_data_operator_blind,
    get_operator_blind_design_info
)
from backend.ai.groq_client import get_groq_client
from backend.core.rate_limiter import rate_limiter_manager
from backend.services.secure_request_handler import handle_secure_request

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# データベース設定
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite フォールバック（開発環境用）
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./x_automation.db"
    logger.warning("PostgreSQL URL not found, using SQLite fallback")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =============================================================================
# データベースモデル
# =============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

# =============================================================================
# Pydanticモデル
# =============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# =============================================================================
# セキュリティ設定
# =============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24時間

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# =============================================================================
# FastAPIアプリケーション初期化
# =============================================================================

app = FastAPI(
    title="X自動反応ツール（シンVPS統一版 + 認証機能）",
    description="運営者ブラインド・プライバシー保護設計 + ユーザー認証",
    version="2.1.0"
)

# CORS設定
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（フロントエンド）
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# =============================================================================
# データベース依存関数
# =============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# 認証ユーティリティ関数
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

# =============================================================================
# 起動時初期化
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時初期化"""
    logger.info("🚀 X自動反応ツール起動開始（シンVPS統一版 + 認証機能）")
    
    # データベーステーブル作成
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ データベーステーブル初期化完了")
    except Exception as e:
        logger.error(f"❌ データベース初期化エラー: {e}")
    
    # 統一設定確認
    config = get_storage_config()
    logger.info(f"ストレージモード: {config.get_active_storage_mode()}")
    logger.info(f"シンVPSモード: {is_shin_vps_mode()}")
    
    # シンVPS初期化
    if is_shin_vps_mode():
        try:
            await operator_blind_storage.create_tables()
            logger.info("✅ シンVPS運営者ブラインド・ストレージ初期化完了")
        except Exception as e:
            logger.error(f"❌ シンVPS初期化エラー: {e}")
    
    # Groq AI初期化確認
    groq_client = get_groq_client()
    if groq_client.is_available():
        logger.info("✅ Groq AI利用可能（運営者一括管理）")
    else:
        logger.warning("⚠️ Groq AI利用不可（APIキー未設定）")
    
    logger.info("✅ アプリケーション起動完了")

# =============================================================================
# 認証エンドポイント
# =============================================================================

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    
    # 既存ユーザーチェック
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="このメールアドレスは既に登録されています"
        )
    
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="このユーザー名は既に使用されています"
        )
    
    # パスワードバリデーション
    if len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="パスワードは6文字以上で入力してください"
        )
    
    # パスワードハッシュ化
    hashed_password = get_password_hash(user.password)
    
    # ユーザー作成
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        last_login=datetime.utcnow()
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # アクセストークン生成
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            last_login=db_user.last_login
        )
        
        logger.info(f"新規ユーザー登録: {user.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="ユーザー登録に失敗しました"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="アカウントが無効化されています"
        )
    
    # 最終ログイン時刻を更新
    user.last_login = datetime.utcnow()
    db.commit()
    
    # アクセストークン生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    logger.info(f"ユーザーログイン: {user.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報取得"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@app.post("/api/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """ユーザーログアウト"""
    logger.info(f"ユーザーログアウト: {current_user.email}")
    return {"message": "ログアウトしました"}

# =============================================================================
# システム情報API
# =============================================================================

@app.get("/api/system/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "database": "connected",
        "authentication": "enabled"
    }

@app.get("/api/system/info")
async def get_system_info():
    """システム情報取得"""
    config = get_storage_config()
    
    return {
        "app_name": "X自動反応ツール",
        "version": "2.1.0",
        "storage_mode": config.get_active_storage_mode().value,
        "privacy_design": "運営者ブラインド",
        "server_location": "日本（シンVPS）",
        "operator_access": "技術的に不可能",
        "groq_ai_available": get_groq_client().is_available(),
        "authentication": "JWT認証",
        "deprecated_features": [
            "ローカルファイル保存（data/users/）",
            "Render PostgreSQL",
            "複数ストレージ併用"
        ]
    }

@app.get("/api/system/migration-status")
async def get_migration_status():
    """移行ステータス取得"""
    config = get_storage_config()
    
    return {
        "migration_completed": True,
        "active_storage": "シンVPS運営者ブラインド",
        "deprecated_removed": True,
        "user_data_location": "シンVPS（暗号化）",
        "operator_access": False,
        "authentication_added": True,
        "migration_plan": config.get_storage_migration_plan()
    }

# =============================================================================
# 運営者ブラインド・ストレージAPI（認証付き）
# =============================================================================

@app.post("/api/storage/blind/store")
async def store_user_data_blind(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """ユーザーデータをブラインド保存（認証付き）"""
    try:
        user_id = str(current_user.id)
        api_keys = data.get("api_keys")
        user_password = data.get("user_password")
        
        if not all([api_keys, user_password]):
            raise HTTPException(status_code=400, detail="必須パラメータが不足しています")
        
        result = await store_user_data_operator_blind(user_id, api_keys, user_password)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "データがシンVPSに安全保存されました",
                "storage_info": result,
                "operator_access": "技術的に不可能"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"ブラインド保存エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storage/blind/retrieve")
async def retrieve_user_data_blind(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """ユーザーデータをブラインド取得（認証付き）"""
    try:
        user_id = str(current_user.id)
        user_password = data.get("user_password")
        
        if not user_password:
            raise HTTPException(status_code=400, detail="認証情報が不足しています")
        
        result = await get_user_data_operator_blind(user_id, user_password)
        
        if result.get("success"):
            return {
                "success": True,
                "api_keys": result["api_keys"],
                "metadata": result.get("metadata", {}),
                "last_accessed": result.get("last_accessed")
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"ブラインド取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/storage/blind/delete")
async def delete_user_data_blind(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """ユーザーデータをブラインド削除（認証付き）"""
    try:
        user_id = str(current_user.id)
        user_password = data.get("user_password")
        
        if not user_password:
            raise HTTPException(status_code=400, detail="認証情報が不足しています")
        
        result = await delete_user_data_operator_blind(user_id, user_password)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "データが完全に削除されました",
                "details": result
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"ブラインド削除エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# セキュアリクエスト処理API（認証付き）
# =============================================================================

@app.post("/api/automation/analyze")
async def analyze_engagement_users(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """エンゲージユーザー分析（セキュア・認証付き）"""
    try:
        session_id = f"session_{current_user.id}_{datetime.now().timestamp()}"
        api_keys = data.get("api_keys")
        tweet_url = data.get("tweet_url")
        
        if not all([api_keys, tweet_url]):
            raise HTTPException(status_code=400, detail="必須パラメータが不足しています")
        
        result = await handle_secure_request(
            "engagement_analysis",
            session_id,
            api_keys,
            tweet_url=tweet_url
        )
        
        return result
        
    except Exception as e:
        logger.error(f"エンゲージメント分析エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/execute")
async def execute_automation_actions(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """自動化アクション実行（セキュア・認証付き）"""
    try:
        session_id = f"session_{current_user.id}_{datetime.now().timestamp()}"
        api_keys = data.get("api_keys")
        actions = data.get("actions", [])
        
        if not all([api_keys, actions]):
            raise HTTPException(status_code=400, detail="必須パラメータが不足しています")
        
        result = await handle_secure_request(
            "action_execution",
            session_id,
            api_keys,
            actions=actions
        )
        
        return result
        
    except Exception as e:
        logger.error(f"アクション実行エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/test")
async def test_api_connection(data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """API接続テスト（セキュア・認証付き）"""
    try:
        session_id = f"session_{current_user.id}_{datetime.now().timestamp()}"
        api_keys = data.get("api_keys")
        
        if not api_keys:
            raise HTTPException(status_code=400, detail="APIキーが不足しています")
        
        result = await handle_secure_request(
            "api_test",
            session_id,
            api_keys
        )
        
        return result
        
    except Exception as e:
        logger.error(f"API接続テストエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# レート制限統計API（認証付き）
# =============================================================================

@app.get("/api/rate-limits/me")
async def get_my_rate_limits(current_user: User = Depends(get_current_user)):
    """現在のユーザーのレート制限統計取得"""
    try:
        user_id = str(current_user.id)
        limiter = rate_limiter_manager.get_limiter(user_id)
        stats = limiter.get_usage_stats()
        
        return {
            "user_id": user_id,
            "username": current_user.username,
            "rate_limits": stats,
            "privacy_note": "運営者はAPIキーを見ることができません"
        }
        
    except Exception as e:
        logger.error(f"レート制限統計エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# 運営者統計API（個人情報なし）
# =============================================================================

@app.get("/api/admin/stats")
async def get_operator_stats():
    """運営者用統計（個人情報なし）"""
    try:
        # 運営者ブラインド統計のみ
        stats = await operator_blind_storage.operator_maintenance_stats()
        
        # ユーザー統計（個人情報なし）
        with SessionLocal() as db:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
        
        return {
            "system_stats": stats,
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "note": "個人情報は含まれていません"
            },
            "design_info": get_operator_blind_design_info(),
            "privacy_guarantee": "運営者はユーザーデータにアクセスできません",
            "authentication": "JWT認証システム",
            "note": "この統計には個人情報は一切含まれていません"
        }
        
    except Exception as e:
        logger.error(f"運営者統計エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# 廃止されたエンドポイント
# =============================================================================

@app.get("/api/deprecated/{path:path}")
async def deprecated_endpoint(path: str):
    """廃止されたエンドポイント"""
    return {
        "error": "このエンドポイントは廃止されました",
        "deprecated_path": f"/{path}",
        "migration_info": {
            "reason": "シンVPS + 運営者ブラインド設計に統一、認証機能追加",
            "new_endpoints": [
                "/api/auth/*",
                "/api/storage/blind/*",
                "/api/automation/*",
                "/api/system/*"
            ],
            "deprecated_features": [
                "ローカルファイル保存（data/users/）",
                "Render PostgreSQL",
                "複数ストレージ併用",
                "認証なしアクセス"
            ]
        }
    }

# =============================================================================
# フロントエンド配信
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """フロントエンド配信"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return HTMLResponse("""
        <h1>X自動反応ツール（シンVPS統一版 + 認証機能）</h1>
        <p>フロントエンドをビルドしてください: <code>cd frontend && npm run build</code></p>
        <p>データ管理: シンVPS + 運営者ブラインド設計</p>
        <p>認証: JWT認証システム</p>
        <p>API文書: <a href="/docs">/docs</a></p>
        """)

@app.get("/{path:path}")
async def serve_frontend_routes(path: str):
    """フロントエンドルート配信"""
    # API パスは除外
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return HTMLResponse(f"<h1>Path: /{path}</h1><p>フロントエンドをビルドしてください</p>")

# =============================================================================
# アプリケーション実行
# =============================================================================

if __name__ == "__main__":
    print("🚀 X自動反応ツール起動中（シンVPS統一版 + 認証機能）...")
    print("📍 データ管理: シンVPS + 運営者ブラインド設計")
    print("🔒 プライバシー: 運営者は一切データにアクセス不可")
    print("🌍 サーバー所在地: 日本（シンクラウド）")
    print("🔐 認証: JWT認証システム")
    print("💰 運営コスト: 月額770円〜")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
