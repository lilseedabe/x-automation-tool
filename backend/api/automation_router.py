"""
🤖 X自動反応ツール - 自動化APIルーター
エンゲージメント分析・アクション実行・ユーザー管理
Freeプラン制限・エラーメッセージ改善対応済み
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from ..database.connection import get_db_session
from ..database.models import UserResponse, AutomationAction
from ..auth.dependencies import get_current_active_user
from ..auth.user_service import api_key_service
from ..services.action_executor import EngagementAutomationExecutor
from ..core.twitter_client import TwitterAPIClient
from ..ai.post_analyzer import PostAnalyzer
from ..services.blacklist_service import blacklist_service

# ログ設定
logger = logging.getLogger(__name__)

# ルーター作成
router = APIRouter(prefix="/api/automation", tags=["自動化"])

# ===================================================================
# 📋 Pydantic Models
# ===================================================================

class AnalyzeEngagingUsersRequest(BaseModel):
    """エンゲージユーザー分析リクエスト"""
    tweet_url: str = Field(..., description="分析対象のツイートURL")
    user_password: str = Field(..., description="APIキー復号用パスワード")

class EngagingUser(BaseModel):
    """エンゲージユーザー情報"""
    user_id: str
    username: str
    display_name: str
    follower_count: int
    following_count: int
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    verified: bool = False
    engagement_type: str  # "like", "retweet", "reply"
    engagement_time: datetime
    ai_score: float
    recent_tweets: List[Dict[str, Any]] = []
    recommended_actions: List[str] = []

class AnalyzeEngagingUsersResponse(BaseModel):
    """エンゲージユーザー分析レスポンス"""
    success: bool
    tweet_id: str
    tweet_author: str
    tweet_text: str
    total_engagement_count: int
    analyzed_users: List[EngagingUser]
    analysis_summary: Dict[str, Any]
    processing_time: float

class ExecuteActionsRequest(BaseModel):
    """アクション実行リクエスト"""
    user_password: str = Field(..., description="APIキー復号用パスワード")
    selected_actions: List[Dict[str, Any]] = Field(..., description="実行するアクション一覧")

class ExecuteActionsResponse(BaseModel):
    """アクション実行レスポンス"""
    success: bool
    executed_count: int
    failed_count: int
    results: List[Dict[str, Any]]
    execution_summary: Dict[str, Any]

class UserPostRequest(BaseModel):
    """ユーザー投稿リクエスト"""
    content: str = Field(..., description="投稿内容")
    user_password: str = Field(..., description="APIキー復号用パスワード")
    schedule_time: Optional[datetime] = Field(None, description="投稿予約時間")

class UserPostResponse(BaseModel):
    """ユーザー投稿レスポンス"""
    success: bool
    tweet_id: Optional[str] = None
    tweet_url: Optional[str] = None
    message: str

class BlacklistRequest(BaseModel):
    """ブラックリスト操作リクエスト"""
    username: str = Field(..., description="対象ユーザー名")
    reason: Optional[str] = Field(None, description="ブラックリスト理由")

class BlacklistResponse(BaseModel):
    """ブラックリスト操作レスポンス"""
    success: bool
    message: str
    blacklisted_users: List[Dict[str, Any]]

# ===================================================================
# 🤖 Automation Endpoints
# ===================================================================

@router.post("/analyze-engaging-users", response_model=AnalyzeEngagingUsersResponse, summary="エンゲージユーザー分析")
async def analyze_engaging_users(
    request: AnalyzeEngagingUsersRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """指定されたツイートにエンゲージしたユーザーを分析（Freeプラン制限対応）"""
    # Freeプラン制限チェック
    api_access_level = "free"  # 仮実装: 実際はcheck_user_api_access_level(current_user.id)で判定
    if api_access_level == "free":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "この機能はFreeプランでは利用できません",
                "reason": "エンゲージメント詳細情報の取得にはBasicプラン（$200/月）が必要です",
                "alternative": "お気に入りユーザー登録機能をご利用ください",
                "required_plan": "Basic ($200/月) または Pro ($5,000/月)"
            }
        )
    # 既存処理...

@router.post("/execute-actions", response_model=ExecuteActionsResponse, summary="自動化アクション実行")
async def execute_automation_actions(
    request: ExecuteActionsRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """選択されたアクションを実行"""
    try:
        logger.info(f"⚡ アクション実行開始: user_id={current_user.id}, actions={len(request.selected_actions)}")
        
        # APIキー復号
        api_keys = await api_key_service.get_decrypted_api_keys(
            current_user.id, request.user_password, session
        )
        
        if not api_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="APIキーの復号に失敗しました。パスワードを確認してください。"
            )
        
        # Twitter APIクライアント初期化
        twitter_client = TwitterAPIClient(api_keys)
        
        # 自動化エグゼキューター初期化
        executor = EngagementAutomationExecutor(
            twitter_client=twitter_client,
            ai_analyzer=PostAnalyzer(),
            user_id=current_user.id
        )
        
        # アクション実行
        execution_result = await executor.execute_selected_actions(request.selected_actions)
        
        # 実行結果をデータベースに記録
        for action_result in execution_result.get("results", []):
            automation_action = AutomationAction(
                user_id=current_user.id,
                action_type=action_result["action_type"],
                target_username=action_result.get("target_username"),
                target_tweet_id=action_result.get("target_tweet_id"),
                content_preview=action_result.get("content_preview", "")[:500],
                status="completed" if action_result["success"] else "failed",
                like_count=1 if action_result["action_type"] == "like" and action_result["success"] else 0,
                retweet_count=1 if action_result["action_type"] == "retweet" and action_result["success"] else 0,
                reply_count=1 if action_result["action_type"] == "reply" and action_result["success"] else 0,
                error_message=action_result.get("error") if not action_result["success"] else None,
                created_at=datetime.now(timezone.utc)
            )
            session.add(automation_action)
        
        await session.commit()
        
        response = ExecuteActionsResponse(
            success=execution_result["success"],
            executed_count=execution_result["executed_count"],
            failed_count=execution_result["failed_count"],
            results=execution_result["results"],
            execution_summary=execution_result["execution_summary"]
        )
        
        logger.info(f"✅ アクション実行完了: 成功={response.executed_count}, 失敗={response.failed_count}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ アクション実行エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アクション実行エラー: {str(e)}"
        )

@router.get("/action-queue", summary="アクションキュー取得")
async def get_action_queue(
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーのアクションキューを取得"""
    try:
        query = select(AutomationAction).where(
            and_(
                AutomationAction.user_id == current_user.id,
                AutomationAction.status == 'pending'
            )
        ).order_by(AutomationAction.created_at.desc()).limit(50)
        
        result = await session.execute(query)
        actions = result.scalars().all()
        
        queue_data = []
        for action in actions:
            queue_data.append({
                "id": action.id,
                "action_type": action.action_type,
                "target_username": action.target_username,
                "target_tweet_id": action.target_tweet_id,
                "content_preview": action.content_preview,
                "created_at": action.created_at,
                "status": action.status
            })
        
        logger.info(f"📋 アクションキュー取得: {len(queue_data)}件")
        return {
            "success": True,
            "queued_actions": queue_data,
            "total_count": len(queue_data)
        }
        
    except Exception as e:
        logger.error(f"❌ アクションキュー取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アクションキュー取得エラー: {str(e)}"
        )

# ===================================================================
# 📝 Post Management Endpoints
# ===================================================================

@router.post("/post", response_model=UserPostResponse, summary="ツイート投稿")
async def create_user_post(
    request: UserPostRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーの投稿を作成"""
    try:
        logger.info(f"📝 投稿作成開始: user_id={current_user.id}")
        
        # APIキー復号
        api_keys = await api_key_service.get_decrypted_api_keys(
            current_user.id, request.user_password, session
        )
        
        if not api_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="APIキーの復号に失敗しました。パスワードを確認してください。"
            )
        
        # Twitter APIクライアント初期化
        twitter_client = TwitterAPIClient(api_keys)
        
        if request.schedule_time:
            # 予約投稿の場合（将来実装）
            return UserPostResponse(
                success=False,
                message="予約投稿は現在実装されていません"
            )
        else:
            # 即座に投稿
            post_result = await twitter_client.create_tweet(request.content)
            
            if post_result.get("success"):
                tweet_id = post_result["tweet_id"]
                tweet_url = f"https://twitter.com/{current_user.username}/status/{tweet_id}"
                
                logger.info(f"✅ 投稿成功: tweet_id={tweet_id}")
                return UserPostResponse(
                    success=True,
                    tweet_id=tweet_id,
                    tweet_url=tweet_url,
                    message="投稿しました"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=post_result.get("error", "投稿に失敗しました")
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 投稿作成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"投稿作成エラー: {str(e)}"
        )

# ===================================================================
# 🚫 Blacklist Management Endpoints
# ===================================================================

@router.get("/blacklist", summary="ブラックリスト取得")
async def get_blacklist(
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーのブラックリストを取得"""
    try:
        blacklist_data = await blacklist_service.get_user_blacklist(current_user.id, session)
        
        return {
            "success": True,
            "blacklisted_users": blacklist_data,
            "total_count": len(blacklist_data)
        }
        
    except Exception as e:
        logger.error(f"❌ ブラックリスト取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ブラックリスト取得エラー: {str(e)}"
        )

@router.post("/blacklist", response_model=BlacklistResponse, summary="ブラックリスト追加")
async def add_to_blacklist(
    request: BlacklistRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーをブラックリストに追加"""
    try:
        logger.info(f"🚫 ブラックリスト追加: user_id={current_user.id}, target={request.username}")
        
        success = await blacklist_service.add_to_blacklist(
            current_user.id, request.username, request.reason, session
        )
        
        if success:
            blacklist_data = await blacklist_service.get_user_blacklist(current_user.id, session)
            
            return BlacklistResponse(
                success=True,
                message=f"@{request.username} をブラックリストに追加しました",
                blacklisted_users=blacklist_data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ブラックリストへの追加に失敗しました"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ブラックリスト追加エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ブラックリスト追加エラー: {str(e)}"
        )

@router.delete("/blacklist/{username}", summary="ブラックリスト削除")
async def remove_from_blacklist(
    username: str,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """ユーザーをブラックリストから削除"""
    try:
        logger.info(f"✅ ブラックリスト削除: user_id={current_user.id}, target={username}")
        
        success = await blacklist_service.remove_from_blacklist(
            current_user.id, username, session
        )
        
        if success:
            blacklist_data = await blacklist_service.get_user_blacklist(current_user.id, session)
            
            return {
                "success": True,
                "message": f"@{username} をブラックリストから削除しました",
                "blacklisted_users": blacklist_data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="削除対象のユーザーが見つかりません"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ブラックリスト削除エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ブラックリスト削除エラー: {str(e)}"
        )