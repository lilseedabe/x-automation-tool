"""
X自動反応アクション実行サービス

このモジュールは以下の機能を提供します：
- エンゲージユーザーの自動取得・分析
- いいね♡とリポストの自動実行
- Groq AI分析との連携
- 安全性チェック
- 人間らしいタイミング制御
- アクションキューの管理
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os

# ログ
import logging

# 内部モジュール
from backend.core.twitter_client import TwitterClient
from backend.ai.groq_client import GroqClient
from backend.ai.post_analyzer import PostAnalyzer
from backend.ai.timing_controller import TimingController
from backend.services.blacklist_service import BlacklistService

logger = logging.getLogger(__name__)

# =============================================================================
# エンゲージユーザー自動化エグゼキューター
# =============================================================================

class EngagementAutomationExecutor:
    """
    エンゲージユーザー自動化実行エンジン
    
    特定の投稿にエンゲージしたユーザーの最新投稿を分析し、
    適切なアクション（いいね♡・リポスト）を実行します。
    """
    
    def __init__(self, user_id: str, credentials: Dict[str, str] = None):
        """
        初期化
        
        Args:
            user_id (str): ユーザーID
            credentials (Dict[str, str]): X API認証情報
        """
        self.user_id = user_id
        
        # サービス初期化
        self.twitter_client = TwitterClient(credentials)
        self.groq_client = GroqClient()
        self.post_analyzer = PostAnalyzer(self.groq_client)
        self.timing_controller = TimingController()
        self.blacklist_service = BlacklistService(user_id)
        
        # 実行統計
        self.execution_stats = {
            "total_executed": 0,
            "likes_executed": 0,
            "retweets_executed": 0,
            "users_processed": 0,
            "tweets_analyzed": 0,
            "errors": 0,
            "last_execution": None,
            "daily_count": 0,
            "last_reset": datetime.now().date()
        }
        
        # 設定
        self.settings = self._load_user_settings()
        
        logger.info(f"EngagementAutomationExecutor初期化完了: user_id={user_id}")
    
    def _load_user_settings(self) -> Dict[str, Any]:
        """ユーザー設定を読み込み"""
        try:
            settings_path = f"data/users/{self.user_id}/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # デフォルト設定
                settings = {
                    "max_daily_actions": 30,
                    "max_users_per_session": 10,
                    "auto_like_enabled": True,
                    "auto_retweet_enabled": True,
                    "safety_mode": True,
                    "min_delay_minutes": 2,
                    "max_delay_minutes": 15,
                    "active_hours": {"start": 8, "end": 22},
                    "quality_threshold": 0.7,
                    "safety_threshold": 0.8,
                    "random_selection": True,
                    "min_engagement_score": 60
                }
                
            return settings
            
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return {
                "max_daily_actions": 30,
                "max_users_per_session": 10,
                "auto_like_enabled": True,
                "auto_retweet_enabled": True,
                "safety_mode": True,
                "min_delay_minutes": 2,
                "max_delay_minutes": 15,
                "active_hours": {"start": 8, "end": 22},
                "quality_threshold": 0.7,
                "safety_threshold": 0.8,
                "random_selection": True,
                "min_engagement_score": 60
            }
    
    def _reset_daily_stats(self):
        """日次統計のリセット"""
        today = datetime.now().date()
        if self.execution_stats["last_reset"] != today:
            self.execution_stats.update({
                "daily_count": 0,
                "last_reset": today
            })
            logger.info("日次統計をリセットしました")
    
    async def is_available(self) -> bool:
        """
        実行可能かチェック
        
        Returns:
            bool: 実行可能フラグ
        """
        # Twitter APIクライアントのチェック
        if not self.twitter_client.is_available():
            return False
        
        # 日次制限チェック
        self._reset_daily_stats()
        if self.execution_stats["daily_count"] >= self.settings["max_daily_actions"]:
            return False
        
        # 時間帯チェック
        current_hour = datetime.now().hour
        active_start = self.settings["active_hours"]["start"]
        active_end = self.settings["active_hours"]["end"]
        
        if not (active_start <= current_hour <= active_end):
            return False
        
        return True
    
    async def analyze_engaging_users(self, tweet_url: str) -> Dict[str, Any]:
        """
        エンゲージユーザーの分析
        
        Args:
            tweet_url (str): 対象ツイートのURL
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if not await self.is_available():
            return {"error": "現在実行できません（制限または時間外）"}
        
        try:
            # ツイートIDを抽出
            tweet_id = self._extract_tweet_id(tweet_url)
            if not tweet_id:
                return {"error": "無効なツイートURLです"}
            
            # エンゲージユーザーを取得
            engaging_users = await self.twitter_client.get_engaging_users(
                tweet_id, 
                max_users=self.settings.get("max_users_per_session", 10)
            )
            
            if not engaging_users:
                return {"error": "エンゲージユーザーが見つかりません"}
            
            # ブラックリストフィルタ
            filtered_users = []
            for user in engaging_users:
                if not await self.blacklist_service.is_blacklisted(user.id):
                    filtered_users.append(user)
            
            if not filtered_users:
                return {"error": "フィルタ後のユーザーが見つかりません"}
            
            # ランダム選択（設定による）
            if self.settings.get("random_selection", True):
                random.shuffle(filtered_users)
                max_analyze = min(len(filtered_users), self.settings.get("max_users_per_session", 10))
                filtered_users = filtered_users[:max_analyze]
            
            # 各ユーザーの最新投稿を分析
            analysis_results = []
            
            for user in filtered_users:
                try:
                    # ユーザーの最新ツイート取得
                    recent_tweets = await self.twitter_client.get_user_recent_tweets(user.id, max_results=3)
                    
                    if not recent_tweets:
                        continue
                    
                    # 最新ツイートを分析
                    latest_tweet = recent_tweets[0]
                    
                    # AI分析実行
                    analysis = await self.post_analyzer.analyze_for_like_and_retweet(
                        latest_tweet.text, 
                        latest_tweet.public_metrics
                    )
                    
                    # 結果を格納
                    user_analysis = {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "name": user.name,
                            "followers_count": user.public_metrics.get("followers_count", 0),
                            "verified": user.verified
                        },
                        "tweet": {
                            "id": latest_tweet.id,
                            "text": latest_tweet.text,
                            "created_at": latest_tweet.created_at,
                            "metrics": latest_tweet.public_metrics
                        },
                        "analysis": analysis,
                        "eligible_for_action": self._is_eligible_for_action(analysis)
                    }
                    
                    analysis_results.append(user_analysis)
                    
                    # レート制限を考慮した待機
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"ユーザー分析エラー (ID: {user.id}): {e}")
                    continue
            
            # 統計更新
            self.execution_stats["users_processed"] += len(filtered_users)
            self.execution_stats["tweets_analyzed"] += len(analysis_results)
            
            result = {
                "success": True,
                "tweet_id": tweet_id,
                "total_engaging_users": len(engaging_users),
                "filtered_users": len(filtered_users),
                "analyzed_users": len(analysis_results),
                "analysis_results": analysis_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"エンゲージユーザー分析完了: {len(analysis_results)}件")
            return result
            
        except Exception as e:
            logger.error(f"エンゲージユーザー分析エラー: {e}")
            return {"error": f"分析エラー: {str(e)}"}
    
    def _extract_tweet_id(self, tweet_url: str) -> Optional[str]:
        """
        ツイートURLからIDを抽出
        
        Args:
            tweet_url (str): ツイートURL
            
        Returns:
            Optional[str]: ツイートID
        """
        try:
            # URL形式: https://x.com/username/status/1234567890
            # または: https://twitter.com/username/status/1234567890
            if "/status/" in tweet_url:
                parts = tweet_url.split("/status/")
                if len(parts) >= 2:
                    tweet_id = parts[1].split("?")[0].split("/")[0]  # クエリパラメータやパスを除去
                    return tweet_id
            return None
        except Exception as e:
            logger.error(f"ツイートID抽出エラー: {e}")
            return None
    
    def _is_eligible_for_action(self, analysis: Dict[str, Any]) -> bool:
        """
        アクション実行対象かどうかを判定
        
        Args:
            analysis (Dict[str, Any]): AI分析結果
            
        Returns:
            bool: 実行対象の場合True
        """
        # エラーがある場合は除外
        if "error" in analysis:
            return False
        
        # 安全性チェック
        if not analysis.get("safety_check", False):
            return False
        
        # リスクレベルチェック
        if analysis.get("risk_level") == "高":
            return False
        
        # 最小エンゲージメントスコアチェック
        min_score = self.settings.get("min_engagement_score", 60)
        like_score = analysis.get("like_score", 0)
        retweet_score = analysis.get("retweet_score", 0)
        
        if max(like_score, retweet_score) < min_score:
            return False
        
        # 信頼度チェック
        if analysis.get("confidence", 0) < 0.6:
            return False
        
        return True
    
    async def execute_selected_actions(self, selected_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        選択されたユーザーに対してアクション実行
        
        Args:
            selected_analyses (List[Dict[str, Any]]): 選択された分析結果
            
        Returns:
            Dict[str, Any]: 実行結果
        """
        if not await self.is_available():
            return {"error": "現在実行できません（制限または時間外）"}
        
        results = []
        successful_actions = 0
        
        try:
            for user_analysis in selected_analyses:
                try:
                    user_info = user_analysis["user"]
                    tweet_info = user_analysis["tweet"]
                    analysis = user_analysis["analysis"]
                    
                    # 推奨アクションを取得
                    recommended_action = analysis.get("recommended_action", "skip")
                    
                    if recommended_action == "skip":
                        results.append({
                            "user_id": user_info["id"],
                            "username": user_info["username"],
                            "action": "skipped",
                            "reason": "AI推奨によりスキップ"
                        })
                        continue
                    
                    # アクション実行
                    if recommended_action == "like":
                        result = await self._execute_like_action(tweet_info["id"], user_info, analysis)
                    elif recommended_action == "retweet":
                        result = await self._execute_retweet_action(tweet_info["id"], user_info, analysis)
                    elif recommended_action == "both":
                        # いいねを優先実行
                        result = await self._execute_like_action(tweet_info["id"], user_info, analysis)
                    else:
                        result = {
                            "success": False,
                            "error": f"不明なアクション: {recommended_action}"
                        }
                    
                    if result.get("success"):
                        successful_actions += 1
                    
                    results.append({
                        "user_id": user_info["id"],
                        "username": user_info["username"],
                        "tweet_id": tweet_info["id"],
                        "action": recommended_action,
                        "result": result,
                        "ai_analysis": analysis
                    })
                    
                    # 人間らしい間隔で実行
                    await self._add_human_delay()
                    
                except Exception as e:
                    logger.error(f"個別アクション実行エラー: {e}")
                    results.append({
                        "user_id": user_analysis.get("user", {}).get("id", "unknown"),
                        "username": user_analysis.get("user", {}).get("username", "unknown"),
                        "action": "error",
                        "error": str(e)
                    })
            
            # 実行記録保存
            await self._save_execution_batch_record(results)
            
            return {
                "success": True,
                "total_attempted": len(selected_analyses),
                "successful_actions": successful_actions,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"バッチアクション実行エラー: {e}")
            return {"error": f"実行エラー: {str(e)}"}
    
    async def _execute_like_action(self, tweet_id: str, user_info: Dict[str, Any], 
                                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """いいねアクション実行"""
        if not self.settings.get("auto_like_enabled", True):
            return {"error": "いいね機能が無効です"}
        
        result = await self.twitter_client.like_tweet(tweet_id, safety_check=False)  # 既に分析済み
        
        if result.get("success"):
            self._update_execution_stats("like", True)
            
            # 実行記録保存
            await self._save_execution_record({
                "action": "like",
                "tweet_id": tweet_id,
                "target_user": user_info,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ai_analysis": analysis
            })
        
        return result
    
    async def _execute_retweet_action(self, tweet_id: str, user_info: Dict[str, Any], 
                                    analysis: Dict[str, Any]) -> Dict[str, Any]:
        """リポストアクション実行"""
        if not self.settings.get("auto_retweet_enabled", True):
            return {"error": "リポスト機能が無効です"}
        
        result = await self.twitter_client.retweet(tweet_id, safety_check=False)  # 既に分析済み
        
        if result.get("success"):
            self._update_execution_stats("retweet", True)
            
            # 実行記録保存
            await self._save_execution_record({
                "action": "retweet",
                "tweet_id": tweet_id,
                "target_user": user_info,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "ai_analysis": analysis
            })
        
        return result
    
    async def _add_human_delay(self):
        """人間らしい遅延を追加"""
        min_delay = self.settings.get("min_delay_minutes", 2) * 60
        max_delay = self.settings.get("max_delay_minutes", 15) * 60
        
        # ランダムな遅延時間を計算
        delay = random.uniform(min_delay, max_delay)
        
        logger.info(f"人間らしい遅延: {delay/60:.1f}分")
        await asyncio.sleep(delay)
    
    def _update_execution_stats(self, action_type: str, success: bool):
        """実行統計を更新"""
        self._reset_daily_stats()
        
        self.execution_stats["total_executed"] += 1
        self.execution_stats["daily_count"] += 1
        self.execution_stats["last_execution"] = datetime.now().isoformat()
        
        if success:
            if action_type == "like":
                self.execution_stats["likes_executed"] += 1
            elif action_type == "retweet":
                self.execution_stats["retweets_executed"] += 1
        else:
            self.execution_stats["errors"] += 1
    
    async def _save_execution_record(self, record: Dict[str, Any]):
        """実行記録を保存"""
        try:
            history_path = f"data/users/{self.user_id}/engagement_history.json"
            
            # 既存履歴読み込み
            history = []
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 新記録追加
            history.append(record)
            
            # 古い記録削除（最新200件まで保持）
            if len(history) > 200:
                history = history[-200:]
            
            # 保存
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"実行記録保存エラー: {e}")
    
    async def _save_execution_batch_record(self, batch_results: List[Dict[str, Any]]):
        """バッチ実行記録を保存"""
        try:
            batch_history_path = f"data/users/{self.user_id}/batch_history.json"
            
            # 既存履歴読み込み
            history = []
            if os.path.exists(batch_history_path):
                with open(batch_history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 新バッチ記録追加
            batch_record = {
                "timestamp": datetime.now().isoformat(),
                "total_actions": len(batch_results),
                "successful_actions": len([r for r in batch_results if r.get("result", {}).get("success")]),
                "results": batch_results
            }
            
            history.append(batch_record)
            
            # 古い記録削除（最新50バッチまで保持）
            if len(history) > 50:
                history = history[-50:]
            
            # 保存
            os.makedirs(os.path.dirname(batch_history_path), exist_ok=True)
            with open(batch_history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"バッチ記録保存エラー: {e}")
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """
        実行統計を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        self._reset_daily_stats()
        
        # Twitter API統計も取得
        twitter_stats = await self.twitter_client.get_automation_stats()
        
        return {
            "engagement_stats": self.execution_stats,
            "twitter_stats": twitter_stats,
            "settings": self.settings,
            "available": await self.is_available(),
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# 既存のActionExecutorクラス（互換性維持）
# =============================================================================

class ActionExecutor:
    """
    従来のActionExecutorクラス（後方互換性のため維持）
    """
    
    def __init__(self, user_id: str, credentials: Dict[str, str] = None):
        # EngagementAutomationExecutorに委譲
        self.engagement_executor = EngagementAutomationExecutor(user_id, credentials)
    
    async def execute_auto_like(self, tweet_id: str, force: bool = False) -> Dict[str, Any]:
        """従来のいいね実行メソッド"""
        return await self.engagement_executor.twitter_client.like_tweet(tweet_id, not force)
    
    async def execute_auto_retweet(self, tweet_id: str, force: bool = False) -> Dict[str, Any]:
        """従来のリポスト実行メソッド"""
        return await self.engagement_executor.twitter_client.retweet(tweet_id, not force)
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """従来の統計取得メソッド"""
        return await self.engagement_executor.get_execution_stats()


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_engagement_automation():
        """エンゲージメント自動化のテスト"""
        # テスト用ユーザーID
        test_user_id = "test_user"
        
        # EngagementAutomationExecutor初期化
        executor = EngagementAutomationExecutor(test_user_id)
        
        if not await executor.is_available():
            print("EngagementAutomationExecutorが利用できません")
            return
        
        print("=== エンゲージユーザー分析テスト ===")
        test_tweet_url = "https://x.com/test_user/status/1234567890"
        
        # エンゲージユーザー分析
        analysis_result = await executor.analyze_engaging_users(test_tweet_url)
        
        if analysis_result.get("success"):
            print(f"分析成功: {analysis_result['analyzed_users']}ユーザーを分析")
            
            # 実行対象を選択（テスト用に最初の2件）
            eligible_analyses = [
                result for result in analysis_result["analysis_results"]
                if result["eligible_for_action"]
            ][:2]
            
            if eligible_analyses:
                print(f"\n=== アクション実行テスト（{len(eligible_analyses)}件）===")
                execution_result = await executor.execute_selected_actions(eligible_analyses)
                
                if execution_result.get("success"):
                    print(f"実行完了: {execution_result['successful_actions']}件成功")
                else:
                    print(f"実行エラー: {execution_result.get('error')}")
        else:
            print(f"分析エラー: {analysis_result.get('error')}")
    
    # テスト実行
    asyncio.run(test_engagement_automation())