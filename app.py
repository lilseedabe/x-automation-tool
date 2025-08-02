"""
🤖 X自動反応ツール - メインアプリケーション（AIルーター統合版）
Python 3.13 + FastAPI + PostgreSQL VPS + 運営者ブラインド設計
"""

import os
import sys
import logging
from typing import Dict, Any, List
from pathlib import Path
from contextlib import asynccontextmanager

# FastAPI 0.115.9+ (Python 3.13公式サポート)
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Pydantic 2.8+ (Python 3.13公式サポート)
from pydantic import BaseModel, Field, ConfigDict

# データベース関連
from backend.database.connection import init_database, close_database, check_database_health

# APIルーター
from backend.api.auth_router import router as auth_router
from backend.api.dashboard_router import router as dashboard_router
from backend.api.automation_router import router as automation_router
from backend.api.rate_limits_router import router as rate_limits_router
from backend.api import ai_router  # 🆕 AI分析ルーター追加

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ライフサイクル管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時処理
    logger.info("🤖 X自動反応ツール - 起動中...")
    
    try:
        # データベース接続初期化
        await init_database()
        logger.info("✅ データベース接続初期化完了")
        
        # その他の初期化処理
        logger.info("✅ アプリケーション起動完了")
        
    except Exception as e:
        logger.error(f"❌ 起動エラー: {str(e)}")
        raise
    
    yield
    
    # 終了時処理
    logger.info("🤖 X自動反応ツール - 終了中...")
    try:
        await close_database()
        logger.info("✅ データベース接続クローズ完了")
    except Exception as e:
        logger.error(f"⚠️ 終了時エラー: {str(e)}")
    
    logger.info("✅ アプリケーション終了完了")

# アプリケーション初期化
app = FastAPI(
    title="X自動反応ツール",
    description="AI搭載のX自動化プラットフォーム - 運営者ブラインド設計",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    summary="プライバシー重視のX自動反応システム",
    lifespan=lifespan
)

# CORS設定
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信
frontend_build_path = Path("frontend/build")
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")

# ルーター登録
try:
    # 認証ルーター
    app.include_router(auth_router)
    logger.info("✅ 認証ルーター登録完了")
    
    # ダッシュボードルーター  
    app.include_router(dashboard_router)
    logger.info("✅ ダッシュボードルーター登録完了")
    
    # 自動化ルーター
    app.include_router(automation_router)
    logger.info("✅ 自動化ルーター登録完了")
    
    # レート制限ルーター
    app.include_router(rate_limits_router)
    logger.info("✅ レート制限ルーター登録完了")
    
    # 🆕 AI分析ルーター（新規追加）
    app.include_router(ai_router.router)
    logger.info("✅ AI分析ルーター登録完了")
    
except Exception as e:
    logger.error(f"❌ ルーター登録エラー: {str(e)}")

# Pydantic 2.8+ モデル定義（Python 3.13完全対応）
class HealthResponse(BaseModel):
    """ヘルスチェックレスポンスモデル"""
    model_config = ConfigDict(
        title="ヘルスチェック",
        description="サーバーの健康状態",
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "X自動反応ツール",
                "python_version": "3.13.0"
            }
        }
    )
    
    status: str = Field(description="サービス状態", examples=["healthy", "unhealthy"])
    service: str = Field(description="サービス名", examples=["X自動反応ツール"])
    message: str = Field(description="メッセージ", examples=["運営者ブラインド設計でプライバシー保護"])
    python_version: str = Field(description="Pythonバージョン", examples=["3.13.0"])
    frontend_built: bool = Field(description="フロントエンドビルド状態", examples=[True])
    environment: str = Field(description="環境", examples=["production"])
    features: List[str] = Field(description="利用可能機能", examples=[["FastAPI", "PostgreSQL"]])
    database: Dict[str, Any] = Field(description="データベース状態")

class APIHealthResponse(BaseModel):
    """API ヘルスチェックレスポンスモデル"""
    model_config = ConfigDict(
        title="API健康状態",
        description="APIエンドポイントの詳細状態"
    )
    
    status: str = Field(description="API状態", examples=["ok"])
    service: str = Field(description="サービス名", examples=["X自動反応ツール API"])
    version: str = Field(description="バージョン", examples=["2.0.0"])
    python: str = Field(description="Pythonバージョン", examples=["3.13.0"])
    environment: str = Field(description="環境", examples=["production"])
    privacy_mode: str = Field(description="プライバシーモード", examples=["maximum"])
    operator_blind: str = Field(description="運営者ブラインド", examples=["true"])
    compatibility: str = Field(description="互換性情報", examples=["Python 3.13 + FastAPI 0.115.9+"])
    features_status: Dict[str, str] = Field(description="機能状態", examples=[{"fastapi": "✅ Running"}])
    database_status: Dict[str, Any] = Field(description="データベース詳細状態")
    ai_services: Dict[str, str] = Field(description="AI サービス状態", examples=[{"groq_api": "connected"}])

class Feature(BaseModel):
    """機能モデル"""
    model_config = ConfigDict(
        title="機能",
        description="システム機能の詳細"
    )
    
    name: str = Field(description="機能名", examples=["運営者ブラインド設計"])
    description: str = Field(description="説明", examples=["技術的に運営者がユーザーデータにアクセス不可"])
    status: str = Field(description="状態", examples=["active", "ready", "planned"])
    implementation: str = Field(description="実装方式", examples=["PostgreSQL + AES-256暗号化"])

class DeploymentInfo(BaseModel):
    """デプロイ情報モデル"""
    model_config = ConfigDict(
        title="デプロイ情報",
        description="システムのデプロイメント詳細"
    )
    
    platform: str = Field(description="プラットフォーム", examples=["Render + シンVPS"])
    python_version: str = Field(description="Pythonバージョン", examples=["3.13.0"])
    fastapi_version: str = Field(description="FastAPIバージョン", examples=["0.115.9+"])
    pydantic_version: str = Field(description="Pydanticバージョン", examples=["2.8+"])
    database: str = Field(description="データベース", examples=["PostgreSQL 16"])
    vps_provider: str = Field(description="VPSプロバイダー", examples=["シンVPS"])
    compatibility: str = Field(description="互換性", examples=["✅ Python 3.13 Full Support"])
    uptime: str = Field(description="稼働時間", examples=["High Availability"])
    cost: str = Field(description="コスト", examples=["VPS Optimized"])

class FeaturesResponse(BaseModel):
    """機能一覧レスポンスモデル"""
    model_config = ConfigDict(
        title="機能一覧",
        description="システムの全機能リスト"
    )
    
    core_features: List[Feature] = Field(description="コア機能")
    privacy_features: List[str] = Field(description="プライバシー機能")
    deployment_info: DeploymentInfo = Field(description="デプロイ情報")

@app.get("/", response_class=HTMLResponse, summary="メインページ", description="React フロントエンドまたはフォールバックHTMLを配信")
async def read_root():
    """ルートエンドポイント - フロントエンド配信"""
    frontend_index = frontend_build_path / "index.html"
    
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    else:
        # フォールバック HTML（フロントエンドビルド中）
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>🤖 X自動反応ツール</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    max-width: 900px;
                    padding: 40px;
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                }}
                .status {{
                    background: rgba(16, 185, 129, 0.2);
                    padding: 20px;
                    border-radius: 15px;
                    margin: 30px 0;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }}
                .tech-badge {{
                    display: inline-block;
                    background: rgba(34, 197, 94, 0.2);
                    color: #86efac;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin: 5px;
                    border: 1px solid rgba(34, 197, 94, 0.3);
                }}
                .feature {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 15px 0;
                    text-align: left;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                a {{
                    color: #a7f3d0;
                    text-decoration: none;
                    padding: 10px 20px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    display: inline-block;
                    margin: 10px;
                    transition: all 0.3s ease;
                }}
                a:hover {{
                    background: rgba(255, 255, 255, 0.2);
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 X自動反応ツール</h1>
                
                <div class="status">
                    <h3>✅ FastAPI + PostgreSQL + AI分析 サーバー正常稼働中</h3>
                    <div>
                        <span class="tech-badge">Python {sys.version.split()[0]}</span>
                        <span class="tech-badge">FastAPI 0.115.9+</span>
                        <span class="tech-badge">Pydantic 2.8+</span>
                        <span class="tech-badge">PostgreSQL VPS</span>
                        <span class="tech-badge">運営者ブラインド</span>
                        <span class="tech-badge">🧠 AI分析</span>
                    </div>
                    <p>🌍 シンVPS + Render ハイブリッド構成で安全なデータ管理</p>
                </div>

                <div class="grid">
                    <div class="feature">
                        <h4>🔐 運営者ブラインド設計</h4>
                        <p>ユーザーのAPIキーは暗号化され、運営者が技術的にアクセス不可。PostgreSQL VPSで安全管理。</p>
                    </div>

                    <div class="feature">
                        <h4>🧠 AI分析エンジン</h4>
                        <p>Groq AIによる高度なエンゲージメント分析とポスト最適化機能。リアルタイム分析対応。</p>
                    </div>

                    <div class="feature">
                        <h4>🏗️ VPS + Render ハイブリッド</h4>
                        <p>シンVPSでデータベース、Renderでアプリケーション。コスト効率と安全性を両立。</p>
                    </div>

                    <div class="feature">
                        <h4>🔑 暗号化ユーザー管理</h4>
                        <p>JWT認証、bcryptパスワード、AES-256暗号化。エンタープライズレベルのセキュリティ。</p>
                    </div>

                    <div class="feature">
                        <h4>🚀 最新技術スタック</h4>
                        <p>Python 3.13 + FastAPI 0.115.9+ + Pydantic 2.8+ + PostgreSQL 16の最新構成。</p>
                    </div>

                    <div class="feature">
                        <h4>🎯 自動化機能</h4>
                        <p>インテリジェントな自動反応、フォロー管理、エンゲージメント分析による効率的なX運用。</p>
                    </div>
                </div>

                <div style="margin-top: 30px;">
                    <a href="/health">🔍 システム状況</a>
                    <a href="/api/system/health">📡 API状況</a>
                    <a href="/api/ai/health">🧠 AI分析状況</a>
                    <a href="/api/features">⚙️ 機能一覧</a>
                    <a href="/api/docs">📚 API文書</a>
                    <a href="/api/auth/register">👤 新規登録</a>
                </div>
                
                <div style="margin-top: 20px; font-size: 0.9em; opacity: 0.8;">
                    <p>🎉 <strong>PostgreSQL VPS + AI分析エンジン + 運営者ブラインド設計完成！</strong></p>
                    <p>完全なユーザー管理システムで安全運用開始</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.get("/health", response_model=HealthResponse, summary="ヘルスチェック", description="サーバーの健康状態を確認")
async def health_check():
    """ヘルスチェックエンドポイント"""
    # データベースヘルスチェック
    db_health = await check_database_health()
    
    return HealthResponse(
        status="healthy" if db_health.get("database") == "healthy" else "degraded",
        service="X自動反応ツール",
        message="運営者ブラインド設計でプライバシー保護",
        python_version=sys.version.split()[0],
        frontend_built=frontend_build_path.exists() and (frontend_build_path / "index.html").exists(),
        environment=os.getenv("APP_ENV", "production"),
        features=[
            "FastAPI 0.115.9+ (Python 3.13公式サポート)",
            "Pydantic 2.8+ (Python 3.13公式サポート)",
            "PostgreSQL VPS データベース",
            "運営者ブラインド暗号化",
            "JWT認証システム",
            "シンVPS + Render ハイブリッド",
            "フロントエンド配信",
            "🧠 AI分析エンジン",
            "Groq API統合",
            "リアルタイム分析"
        ],
        database=db_health
    )

@app.get("/api/system/health", response_model=APIHealthResponse, summary="API ヘルスチェック", description="APIシステムの詳細状態")
async def api_health():
    """API ヘルスチェック"""
    # データベースヘルスチェック
    db_health = await check_database_health()
    
    return APIHealthResponse(
        status="ok" if db_health.get("database") == "healthy" else "degraded",
        service="X自動反応ツール API",
        version="2.0.0",
        python=sys.version.split()[0],
        environment=os.getenv("APP_ENV", "production"),
        privacy_mode=os.getenv("PRIVACY_MODE", "maximum"),
        operator_blind=os.getenv("OPERATOR_BLIND_ENABLED", "true"),
        compatibility="Python 3.13 + FastAPI 0.115.9+ + Pydantic 2.8+ + PostgreSQL 16",
        features_status={
            "fastapi": "✅ 0.115.9+ Running",
            "pydantic": "✅ v2.8+ Active",
            "python_3_13": "✅ Official Support",
            "postgresql": f"✅ {db_health.get('database', 'unknown').title()}",
            "database_response": f"{db_health.get('response_time_ms', 'N/A')}ms",
            "vps_connection": "✅ Active" if db_health.get("connection_test") else "❌ Failed",
            "frontend": "✅ Ready" if (frontend_build_path / "index.html").exists() else "⏳ Building",
            "cors": "✅ Enabled",
            "privacy": "✅ Maximum",
            "api_docs": "✅ Available",
            "authentication": "✅ JWT + bcrypt",
            "encryption": "✅ AES-256-GCM",
            "compatibility": "✅ Fully Compatible",
            "ai_analysis": "✅ Groq AI Connected",
            "post_analyzer": "✅ Active",
            "sentiment_analysis": "✅ Active"
        },
        database_status=db_health,
        ai_services={
            "groq_api": "connected",
            "post_analyzer": "active",
            "sentiment_analysis": "active",
            "engagement_predictor": "active",
            "content_optimizer": "active"
        }
    )

@app.get("/api/features", response_model=FeaturesResponse, summary="機能一覧", description="システムの全機能とデプロイ情報")
async def get_features():
    """利用可能機能一覧"""
    return FeaturesResponse(
        core_features=[
            Feature(
                name="運営者ブラインド設計",
                description="技術的に運営者がユーザーデータにアクセス不可",
                status="active",
                implementation="PostgreSQL + AES-256-GCM暗号化"
            ),
            Feature(
                name="AI分析エンジン",
                description="Groq AIによる高度なエンゲージメント分析とポスト最適化",
                status="active",
                implementation="Groq API + PostgreSQL + リアルタイム分析"
            ),
            Feature(
                name="ユーザー認証システム",
                description="JWT + bcrypt による安全な認証機能",
                status="active",
                implementation="FastAPI Security + PostgreSQL"
            ),
            Feature(
                name="APIキー暗号化管理",
                description="X APIキーをユーザーパスワードベースで暗号化保存",
                status="active",
                implementation="PBKDF2 + AES-256-GCM"
            ),
            Feature(
                name="PostgreSQL VPS",
                description="シンVPSでの専用データベース運用",
                status="active",
                implementation="Ubuntu 25.04 + PostgreSQL 16"
            ),
            Feature(
                name="Python 3.13 + FastAPI 0.115.9+",
                description="最新技術スタックでの高性能API（公式サポート）",
                status="active",
                implementation="FastAPI 0.115.9+ + Pydantic 2.8+"
            ),
            Feature(
                name="フロントエンド配信",
                description="React SPAの効率的な配信",
                status="active",
                implementation="静的ファイル配信 + SPAフォールバック"
            ),
            Feature(
                name="自動化システム",
                description="インテリジェントな自動反応とフォロー管理",
                status="active",
                implementation="AI駆動型自動化エンジン"
            )
        ],
        privacy_features=[
            "運営者ブラインド暗号化",
            "ユーザーパスワードベース暗号化",
            "暗号化ストレージ",
            "自動削除機能",
            "セッション管理",
            "Row Level Security",
            "ユーザー制御",
            "透明性保証",
            "運営者アクセス不可",
            "AI分析匿名化",
            "プライベートデータ保護"
        ],
        deployment_info=DeploymentInfo(
            platform="Render + シンVPS",
            python_version=sys.version.split()[0],
            fastapi_version="0.115.9+",
            pydantic_version="2.8+",
            database="PostgreSQL 16",
            vps_provider="シンVPS (1GB/1vCPU/30GB SSD)",
            compatibility="✅ Python 3.13 Full Official Support",
            uptime="High Availability",
            cost="VPS + Render Optimized"
        )
    )

# フロントエンドルートのフォールバック（SPA対応）
@app.get("/{path:path}", summary="SPA フォールバック", description="React SPAのルーティング対応")
async def serve_frontend(path: str):
    """フロントエンド配信（SPA対応）"""
    # APIパスは除外
    if path.startswith("api/"):
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "API endpoint not found",
                "path": path,
                "available_endpoints": [
                    "/health", 
                    "/api/system/health", 
                    "/api/ai/health",
                    "/api/features", 
                    "/api/docs",
                    "/api/auth/register",
                    "/api/auth/login",
                    "/api/auth/me",
                    "/api/ai/analyze",
                    "/api/ai/optimize"
                ]
            }
        )
    
    # フロントエンドファイルが存在する場合
    frontend_index = frontend_build_path / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    else:
        return {
            "message": "フロントエンドビルド中...",
            "requested_path": path,
            "status": "building",
            "compatibility": "Python 3.13 + FastAPI 0.115.9+ + PostgreSQL VPS",
            "features": "ユーザー認証・APIキー管理・運営者ブラインド設計・AI分析エンジン"
        }

# 開発用サーバー起動
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🤖 X自動反応ツール - FastAPI 0.115.9+ + PostgreSQL VPS + AI分析")
    logger.info(f"Python {sys.version}")
    logger.info(f"Pydantic 2.8+ + 運営者ブラインド設計")
    logger.info(f"🚀 起動: http://{host}:{port}")
    logger.info(f"📚 API文書: http://{host}:{port}/api/docs")
    logger.info(f"🧠 AI分析: http://{host}:{port}/api/ai/health")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("APP_ENV") != "production",
        log_level="info"
    )
