"""
⚡ X自動反応ツール - エンゲージメント自動化エグゼキューター
あなたのツイートに反応したユーザーを分析し、相互エンゲージメントを実行
"""

import logging
import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class EngagementAutomationExecutor:
    """エンゲージメント自動化実行クラス"""
    
    def __init__(self, twitter_client, ai_analyzer, user_id: int):
        """
        初期化
        
        Args:
            twitter_client: TwitterAPIClient インスタンス
            ai_analyzer: PostAnalyzer インスタンス
            user_id: 実行ユーザーID
        """
        self.twitter_client = twitter_client
        self.ai_analyzer = ai_analyzer
        self.user_id = user_id
    
    async def analyze_engaging_users(self, tweet_url: str) -> Dict[str, Any]:
        """
        指定されたツイートにエンゲージしたユーザーを分析
        
        Args:
            tweet_url: 分析対象のツイートURL
            
        Returns:
            分析結果辞書
        """
        try:
            logger.info(f"🔍 エンゲージユーザー分析開始: {tweet_url}")
            
            # ツイートIDを抽出
            tweet_id = self.twitter_client.extract_tweet_id_from_url(tweet_url)
            if not tweet_id:
                return {
                    "success": False,
                    "error": "無効なツイートURLです"
                }
            
            # ツイート情報を取得
            tweet_result = await self.twitter_client.get_tweet(tweet_id)
            if not tweet_result.get("success"):
                return {
                    "success": False,
                    "error": "ツイートの取得に失敗しました"
                }
            
            tweet_data = tweet_result["tweet"]
            
            # いいねしたユーザーを取得
            liking_users_result = await self.twitter_client.get_liking_users(tweet_id, max_results=100)
            liking_users = liking_users_result.get("users", []) if liking_users_result.get("success") else []
            
            # リツイートしたユーザーを取得
            retweeting_users_result = await self.twitter_client.get_retweeting_users(tweet_id, max_results=100)
            retweeting_users = retweeting_users_result.get("users", []) if retweeting_users_result.get("success") else []
            
            # 全エンゲージユーザーをまとめる
            all_engaging_users = []
            
            # 重複を避けるためのユーザーIDセット
            seen_user_ids = set()
            
            # いいねユーザーを追加
            for user in liking_users:
                if user["id"] not in seen_user_ids:
                    all_engaging_users.append(user)
                    seen_user_ids.add(user["id"])
            
            # リツイートユーザーを追加
            for user in retweeting_users:
                if user["id"] not in seen_user_ids:
                    all_engaging_users.append(user)
                    seen_user_ids.add(user["id"])
            
            # 各ユーザーを AI 分析
            analyzed_users = []
            for user in all_engaging_users:
                try:
                    # ユーザーの最新ツイートを取得（仮想実装）
                    recent_tweets = await self._get_user_recent_tweets(user["id"])
                    
                    # AI 分析実行
                    ai_analysis = await self.ai_analyzer.analyze_user_engagement_quality(
                        user_data=user,
                        recent_tweets=recent_tweets,
                        original_tweet=tweet_data
                    )
                    
                    # 推奨アクションを生成
                    recommended_actions = self._generate_recommended_actions(
                        user, recent_tweets, ai_analysis
                    )
                    
                    analyzed_user = {
                        "user_id": user["id"],
                        "username": user["username"],
                        "display_name": user["name"],
                        "follower_count": user["public_metrics"]["followers_count"],
                        "following_count": user["public_metrics"]["following_count"],
                        "profile_image_url": None,  # Twitter API v2では別途取得が必要
                        "bio": user.get("description", ""),
                        "verified": user.get("verified", False),
                        "engagement_type": user["engagement_type"],
                        "engagement_time": user["engagement_time"],
                        "ai_score": ai_analysis["engagement_score"],
                        "recent_tweets": recent_tweets,
                        "recommended_actions": recommended_actions
                    }
                    
                    analyzed_users.append(analyzed_user)
                    
                except Exception as e:
                    logger.warning(f"⚠️ ユーザー分析スキップ: {user['username']} - {str(e)}")
                    continue
            
            # 分析サマリーを生成
            analysis_summary = self._generate_analysis_summary(analyzed_users, tweet_data)
            
            result = {
                "success": True,
                "tweet_id": tweet_id,
                "tweet_author": tweet_data["author"]["username"] if tweet_data.get("author") else "unknown",
                "tweet_text": tweet_data["text"],
                "total_engagement_count": len(all_engaging_users),
                "engaging_users": analyzed_users,
                "analysis_summary": analysis_summary
            }
            
            logger.info(f"✅ エンゲージユーザー分析完了: {len(analyzed_users)}人分析")
            return result
            
        except Exception as e:
            logger.error(f"❌ エンゲージユーザー分析エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_selected_actions(self, selected_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        選択されたアクションを実行
        
        Args:
            selected_actions: 実行するアクション一覧
            
        Returns:
            実行結果辞書
        """
        try:
            logger.info(f"⚡ アクション実行開始: {len(selected_actions)}件")
            
            results = []
            executed_count = 0
            failed_count = 0
            
            for action in selected_actions:
                try:
                    action_type = action["action_type"]
                    target_username = action["target_username"]
                    target_tweet_id = action.get("target_tweet_id")
                    
                    # アクション実行
                    if action_type == "like":
                        result = await self.twitter_client.like_tweet(target_tweet_id)
                    elif action_type == "retweet":
                        result = await self.twitter_client.retweet(target_tweet_id)
                    elif action_type == "reply":
                        reply_text = action.get("reply_text", "素晴らしい投稿ですね！")
                        result = await self.twitter_client.reply_to_tweet(target_tweet_id, reply_text)
                    else:
                        result = {
                            "success": False,
                            "error": f"未対応のアクションタイプ: {action_type}"
                        }
                    
                    # 結果を記録
                    action_result = {
                        "action_type": action_type,
                        "target_username": target_username,
                        "target_tweet_id": target_tweet_id,
                        "success": result.get("success", False),
                        "content_preview": action.get("content_preview", "")
                    }
                    
                    if result.get("success"):
                        executed_count += 1
                        logger.info(f"✅ アクション成功: {action_type} -> @{target_username}")
                    else:
                        failed_count += 1
                        action_result["error"] = result.get("error", "不明なエラー")
                        logger.warning(f"❌ アクション失敗: {action_type} -> @{target_username} - {action_result['error']}")
                    
                    results.append(action_result)
                    
                    # レート制限を避けるため少し待機
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    failed_count += 1
                    action_result = {
                        "action_type": action.get("action_type", "unknown"),
                        "target_username": action.get("target_username", "unknown"),
                        "target_tweet_id": action.get("target_tweet_id"),
                        "success": False,
                        "error": str(e)
                    }
                    results.append(action_result)
                    logger.error(f"❌ アクション実行エラー: {str(e)}")
            
            # 実行サマリーを生成
            execution_summary = {
                "total_actions": len(selected_actions),
                "executed_count": executed_count,
                "failed_count": failed_count,
                "success_rate": (executed_count / len(selected_actions)) * 100 if selected_actions else 0,
                "execution_time": datetime.now(timezone.utc)
            }
            
            result = {
                "success": executed_count > 0,
                "executed_count": executed_count,
                "failed_count": failed_count,
                "results": results,
                "execution_summary": execution_summary
            }
            
            logger.info(f"✅ アクション実行完了: 成功={executed_count}, 失敗={failed_count}")
            return result
            
        except Exception as e:
            logger.error(f"❌ アクション実行エラー: {str(e)}")
            return {
                "success": False,
                "executed_count": 0,
                "failed_count": len(selected_actions),
                "results": [],
                "execution_summary": {"error": str(e)},
                "error": str(e)
            }
    
    async def _get_user_recent_tweets(self, user_id: str, max_tweets: int = 5) -> List[Dict[str, Any]]:
        """
        ユーザーの最新ツイートを取得
        
        Args:
            user_id: ユーザーID
            max_tweets: 取得する最大ツイート数
            
        Returns:
            最新ツイート一覧
        """
        try:
            # 実際の実装では Twitter API v2 の get_users_tweets を使用
            # ここでは簡略化したダミーデータを返す
            tweets = []
            for i in range(min(max_tweets, 3)):
                tweets.append({
                    "id": f"tweet_{user_id}_{i}",
                    "text": f"ユーザー {user_id} のサンプルツイート {i+1}",
                    "created_at": datetime.now(timezone.utc),
                    "public_metrics": {
                        "like_count": random.randint(0, 50),
                        "retweet_count": random.randint(0, 20),
                        "reply_count": random.randint(0, 10)
                    }
                })
            
            return tweets
            
        except Exception as e:
            logger.warning(f"⚠️ ユーザーツイート取得失敗: {user_id} - {str(e)}")
            return []
    
    def _generate_recommended_actions(
        self, 
        user: Dict[str, Any], 
        recent_tweets: List[Dict[str, Any]], 
        ai_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        推奨アクションを生成
        
        Args:
            user: ユーザー情報
            recent_tweets: 最新ツイート
            ai_analysis: AI分析結果
            
        Returns:
            推奨アクション一覧
        """
        actions = []
        
        # AI スコアに基づいて推奨アクションを決定
        score = ai_analysis.get("engagement_score", 0)
        
        if score >= 0.8:
            # 高品質ユーザー: 積極的エンゲージメント
            if recent_tweets:
                latest_tweet = recent_tweets[0]
                actions.extend([
                    f"いいね: {latest_tweet['text'][:50]}...",
                    f"リツイート: {latest_tweet['text'][:50]}..."
                ])
                
                # フォロワー数が適度なら返信も推奨
                if user["public_metrics"]["followers_count"] < 10000:
                    actions.append(f"返信: {latest_tweet['text'][:50]}...")
        
        elif score >= 0.6:
            # 中品質ユーザー: 選択的エンゲージメント
            if recent_tweets:
                latest_tweet = recent_tweets[0]
                actions.append(f"いいね: {latest_tweet['text'][:50]}...")
        
        elif score >= 0.4:
            # 低品質ユーザー: 慎重なエンゲージメント
            actions.append("観察のみ推奨")
        
        else:
            # 非常に低品質: エンゲージメント非推奨
            actions.append("エンゲージメント非推奨")
        
        return actions
    
    def _generate_analysis_summary(
        self, 
        analyzed_users: List[Dict[str, Any]], 
        tweet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析サマリーを生成
        
        Args:
            analyzed_users: 分析済みユーザー一覧
            tweet_data: 元ツイートデータ
            
        Returns:
            分析サマリー
        """
        if not analyzed_users:
            return {
                "total_users": 0,
                "average_score": 0,
                "quality_distribution": {},
                "recommended_engagement_count": 0
            }
        
        # AI スコアの統計
        scores = [user["ai_score"] for user in analyzed_users]
        average_score = sum(scores) / len(scores)
        
        # 品質分布
        high_quality = len([s for s in scores if s >= 0.8])
        medium_quality = len([s for s in scores if 0.6 <= s < 0.8])
        low_quality = len([s for s in scores if 0.4 <= s < 0.6])
        very_low_quality = len([s for s in scores if s < 0.4])
        
        # 推奨エンゲージメント数
        recommended_count = high_quality + (medium_quality // 2)
        
        return {
            "total_users": len(analyzed_users),
            "average_score": round(average_score, 2),
            "quality_distribution": {
                "high_quality": high_quality,
                "medium_quality": medium_quality,
                "low_quality": low_quality,
                "very_low_quality": very_low_quality
            },
            "recommended_engagement_count": recommended_count,
            "analysis_time": datetime.now(timezone.utc)
        }