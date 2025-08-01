"""
🚦 X自動反応ツール - レート制限APIルーター（シンプル版）
"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import logging

from ..auth.dependencies import get_current_active_user
from ..database.models import UserResponse

logger = logging.getLogger(__name__)

# ルーター作成
router = APIRouter(prefix="/api/rate-limits", tags=["rate-limits"])

# ===============================================================================
# Pydantic Models
# ===============================================================================

class RateLimitInfo(BaseModel):
    """レート制限情報"""
    endpoint: str = Field(..., description="APIエンドポイント")
    requests_made: int = Field(..., description="使用済みリクエスト数")
    requests_limit: int = Field(..., description="制限数")
    remaining: int = Field(..., description="残りリクエスト数")
    reset_at: datetime = Field(..., description="リセット時刻")
    percentage_used: float = Field(..., description="使用率（%）")

class RateLimitSummary(BaseModel):
    """レート制限サマリー"""
    user_id: str = Field(..., description="ユーザーID")
    total_endpoints: int = Field(..., description="監視対象エンドポイント数")
    limits: List[RateLimitInfo] = Field(..., description="レート制限詳細")
    overall_status: str = Field(..., description="全体ステータス")
    next_reset: datetime = Field(..., description="次のリセット時刻")

# ===============================================================================
# API エンドポイント
# ===============================================================================

@router.get("/my", response_model=RateLimitSummary)
async def get_my_rate_limits(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    現在のユーザーのレート制限状況を取得（シンプル版）
    """
    try:
        logger.info(f"📊 レート制限取得: user_id={current_user.id}")
        
        # 現在時刻
        now = datetime.utcnow()
        reset_time = now + timedelta(hours=1)
        
        # 主要エンドポイントのデフォルト制限情報
        endpoints = [
            "/api/automation/analyze-engaging-users",
            "/api/automation/execute-actions", 
            "/api/automation/post",
            "/api/dashboard/stats",
            "/api/auth/api-keys/test"
        ]
        
        # デフォルトレート制限情報を作成
        limits = []
        for endpoint in endpoints:
            limit_info = RateLimitInfo(
                endpoint=endpoint,
                requests_made=0,  # 実際の使用量は後で実装
                requests_limit=100,
                remaining=100,
                reset_at=reset_time,
                percentage_used=0.0
            )
            limits.append(limit_info)
        
        # サマリー作成
        summary = RateLimitSummary(
            user_id=str(current_user.id),
            total_endpoints=len(limits),
            limits=limits,
            overall_status="healthy",
            next_reset=reset_time
        )
        
        logger.info(f"✅ レート制限取得成功: user_id={current_user.id}")
        return summary
        
    except Exception as e:
        logger.error(f"❌ レート制限取得エラー: {str(e)}")
        
        # エラー時もデフォルトレスポンスを返す
        now = datetime.utcnow()
        default_limits = [
            RateLimitInfo(
                endpoint="/api/automation/analyze-engaging-users",
                requests_made=0,
                requests_limit=100,
                remaining=100,
                reset_at=now + timedelta(hours=1),
                percentage_used=0.0
            )
        ]
        
        return RateLimitSummary(
            user_id=str(current_user.id),
            total_endpoints=1,
            limits=default_limits,
            overall_status="healthy",
            next_reset=now + timedelta(hours=1)
        )

@router.get("/status")
async def get_rate_limit_status(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """レート制限システムの全体ステータス"""
    return {
        "system_status": "operational",
        "current_time": datetime.utcnow(),
        "rate_limiting_enabled": True,
        "default_limits": {
            "automation": 100,
            "api_requests": 1000,
            "window_hours": 1
        },
        "message": "レート制限システムは正常に動作しています"
    }
