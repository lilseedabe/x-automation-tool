"""
🤖 X自動反応ツール - メインアプリケーション（シンVPS統一版）

シンVPS + 運営者ブラインド・ストレージに統一
ローカルファイル保存は廃止
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, Any

# FastAPI
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

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

# FastAPIアプリケーション初期化
app = FastAPI(
    title="X自動反応ツール（シンVPS統一版）",
    description="運営者ブラインド・プライバシー保護設計",
    version="2.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（フロントエンド）
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# =============================================================================
# 起動時初期化
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時初期化"""
    logger.info("🚀 X自動反応ツール起動開始（シンVPS統一版）")
    
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
# システム情報API
# =============================================================================

@app.get("/api/system/info")
async def get_system_info():
    """システム情報取得"""
    config = get_storage_config()
    
    return {
        "app_name": "X自動反応ツール",
        "version": "2.0.0",
        "storage_mode": config.get_active_storage_mode().value,
        "privacy_design": "運営者ブラインド",
        "server_location": "日本（シンVPS）",
        "operator_access": "技術的に不可能",
        "groq_ai_available": get_groq_client().is_available(),
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
        "migration_plan": config.get_storage_migration_plan()
    }

# =============================================================================
# 運営者ブラインド・ストレージAPI
# =============================================================================

@app.post("/api/storage/blind/store")
async def store_user_data_blind(data: Dict[str, Any]):
    """ユーザーデータをブラインド保存"""
    try:
        user_id = data.get("user_id")
        api_keys = data.get("api_keys")
        user_password = data.get("user_password")
        
        if not all([user_id, api_keys, user_password]):
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
async def retrieve_user_data_blind(data: Dict[str, Any]):
    """ユーザーデータをブラインド取得"""
    try:
        user_id = data.get("user_id")
        user_password = data.get("user_password")
        
        if not all([user_id, user_password]):
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
async def delete_user_data_blind(data: Dict[str, Any]):
    """ユーザーデータをブラインド削除"""
    try:
        user_id = data.get("user_id")
        user_password = data.get("user_password")
        
        if not all([user_id, user_password]):
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
# セキュアリクエスト処理API
# =============================================================================

@app.post("/api/automation/analyze")
async def analyze_engagement_users(data: Dict[str, Any]):
    """エンゲージユーザー分析（セキュア）"""
    try:
        session_id = data.get("session_id", f"session_{datetime.now().timestamp()}")
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
async def execute_automation_actions(data: Dict[str, Any]):
    """自動化アクション実行（セキュア）"""
    try:
        session_id = data.get("session_id", f"session_{datetime.now().timestamp()}")
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
async def test_api_connection(data: Dict[str, Any]):
    """API接続テスト（セキュア）"""
    try:
        session_id = data.get("session_id", f"session_{datetime.now().timestamp()}")
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
# レート制限統計API
# =============================================================================

@app.get("/api/rate-limits/{user_id}")
async def get_user_rate_limits(user_id: str):
    """ユーザーのレート制限統計取得"""
    try:
        limiter = rate_limiter_manager.get_limiter(user_id)
        stats = limiter.get_usage_stats()
        
        return {
            "user_id": user_id,
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
        
        return {
            "system_stats": stats,
            "design_info": get_operator_blind_design_info(),
            "privacy_guarantee": "運営者はユーザーデータにアクセスできません",
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
            "reason": "シンVPS + 運営者ブラインド設計に統一",
            "new_endpoints": [
                "/api/storage/blind/*",
                "/api/automation/*",
                "/api/system/*"
            ],
            "deprecated_features": [
                "ローカルファイル保存（data/users/）",
                "Render PostgreSQL",
                "複数ストレージ併用"
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
        <h1>X自動反応ツール（シンVPS統一版）</h1>
        <p>フロントエンドをビルドしてください: <code>cd frontend && npm run build</code></p>
        <p>データ管理: シンVPS + 運営者ブラインド設計</p>
        """)

@app.get("/{path:path}")
async def serve_frontend_routes(path: str):
    """フロントエンドルート配信"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return HTMLResponse(f"<h1>Path: /{path}</h1><p>フロントエンドをビルドしてください</p>")

# =============================================================================
# アプリケーション実行
# =============================================================================

if __name__ == "__main__":
    print("🚀 X自動反応ツール起動中（シンVPS統一版）...")
    print("📍 データ管理: シンVPS + 運営者ブラインド設計")
    print("🔒 プライバシー: 運営者は一切データにアクセス不可")
    print("🌍 サーバー所在地: 日本（シンクラウド）")
    print("💰 運営コスト: 月額770円〜")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )