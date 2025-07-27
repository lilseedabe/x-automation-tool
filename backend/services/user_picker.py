"""
ユーザーピックアップサービス

このモジュールは以下の機能を提供します：
- ターゲットユーザーの発見
- フォロワー分析
- インフルエンサー検出
- ユーザー関連性分析
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from ..core.twitter_client import TwitterClient, User
from .blacklist_service import BlacklistService

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ユーザーピックアップサービスクラス
# =============================================================================

class UserPicker:
    """
    ユーザーピックアップサービス
    
    研究・分析目的でターゲットユーザーを発見・分析します。
    """
    
    def __init__(self, twitter_client: TwitterClient = None, blacklist_service: BlacklistService = None):
        """
        初期化
        
        Args:
            twitter_client (TwitterClient): Twitterクライアント
            blacklist_service (BlacklistService): ブラックリストサービス
        """
        self.twitter_client = twitter_client or TwitterClient()
        self.blacklist_service = blacklist_service or BlacklistService()
        
        # 分析パラメータ
        self.min_followers = 100
        self.max_followers = 100000
        self.min_engagement_rate = 0.01  # 1%
        self.activity_threshold_days = 30
        
        logger.info("UserPicker初期化完了")
    
    async def discover_users_by_keywords(self, keywords: List[str], max_users: int = 50,
                                       user_id: str = None) -> List[Dict[str, Any]]:
        """
        キーワードベースのユーザー発見
        
        Args:
            keywords (List[str]): 検索キーワード
            max_users (int): 最大取得ユーザー数
            user_id (str): フィルタリング用ユーザーID
            
        Returns:
            List[Dict[str, Any]]: 発見されたユーザーリスト
        """
        if not self.twitter_client.is_available():
            logger.error("Twitterクライアントが利用できません")
            return []
        
        try:
            discovered_users = []
            processed_users = set()
            
            for keyword in keywords:
                # キーワードでツイート検索
                tweets = await self.twitter_client.search_tweets(
                    f'"{keyword}" -is:retweet', 
                    max_results=min(100, max_users * 2)
                )
                
                for tweet in tweets:
                    if tweet.author_id and tweet.author_id not in processed_users:
                        # ユーザー情報取得
                        user = await self.twitter_client.get_user_by_id(tweet.author_id)
                        
                        if user:
                            # ブラックリストチェック
                            if user_id and self.blacklist_service.is_user_blacklisted(user_id, user.username):
                                continue
                            
                            # 基本フィルタリング
                            if self._is_valid_user(user):
                                user_analysis = await self._analyze_user(user)
                                user_analysis["discovery_keyword"] = keyword
                                user_analysis["sample_tweet"] = tweet.text[:100] + "..."
                                
                                discovered_users.append(user_analysis)
                                processed_users.add(tweet.author_id)
                                
                                if len(discovered_users) >= max_users:
                                    break
                
                # レート制限対策
                await asyncio.sleep(0.1)
                
                if len(discovered_users) >= max_users:
                    break
            
            # 関連性でソート
            discovered_users.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            logger.info(f"ユーザー発見完了: {len(discovered_users)}件")
            return discovered_users[:max_users]
            
        except Exception as e:
            logger.error(f"ユーザー発見エラー: {e}")
            return []
    
    async def find_influencers_in_topic(self, topic: str, min_followers: int = 1000,
                                      max_results: int = 20) -> List[Dict[str, Any]]:
        """
        トピック内のインフルエンサー発見
        
        Args:
            topic (str): トピック
            min_followers (int): 最小フォロワー数
            max_results (int): 最大結果数
            
        Returns:
            List[Dict[str, Any]]: インフルエンサーリスト
        """
        if not self.twitter_client.is_available():
            logger.error("Twitterクライアントが利用できません")
            return []
        
        try:
            influencers = []
            processed_users = set()
            
            # トピック関連のツイートを検索
            search_queries = [
                f'"{topic}" min_faves:100',
                f'"{topic}" min_retweets:50',
                f'#{topic.replace(" ", "")} min_faves:50'
            ]
            
            for query in search_queries:
                tweets = await self.twitter_client.search_tweets(
                    query, max_results=100
                )
                
                for tweet in tweets:
                    if tweet.author_id and tweet.author_id not in processed_users:
                        user = await self.twitter_client.get_user_by_id(tweet.author_id)
                        
                        if user and user.public_metrics.get("followers_count", 0) >= min_followers:
                            # インフルエンサー分析
                            influence_analysis = await self._analyze_influencer(user, tweet)
                            influence_analysis["topic"] = topic
                            
                            influencers.append(influence_analysis)
                            processed_users.add(tweet.author_id)
                            
                            if len(influencers) >= max_results:
                                break
                
                await asyncio.sleep(0.1)
                
                if len(influencers) >= max_results:
                    break
            
            # インフルエンス スコアでソート
            influencers.sort(key=lambda x: x.get("influence_score", 0), reverse=True)
            
            logger.info(f"インフルエンサー発見完了: {len(influencers)}件")
            return influencers[:max_results]
            
        except Exception as e:
            logger.error(f"インフルエンサー発見エラー: {e}")
            return []
    
    async def analyze_user_network(self, username: str, depth: int = 2) -> Dict[str, Any]:
        """
        ユーザーネットワーク分析
        
        Args:
            username (str): 分析対象ユーザー名
            depth (int): 分析深度
            
        Returns:
            Dict[str, Any]: ネットワーク分析結果
        """
        if not self.twitter_client.is_available():
            logger.error("Twitterクライアントが利用できません")
            return {"error": "Twitterクライアントが利用できません"}
        
        try:
            # 中心ユーザー取得
            center_user = await self.twitter_client.get_user_by_username(username)
            if not center_user:
                return {"error": f"ユーザーが見つかりません: {username}"}
            
            # ユーザーのツイート分析
            tweets = await self.twitter_client.get_user_tweets(center_user.id, max_results=50)
            
            # メンション・リプライ分析
            connected_users = self._extract_connected_users(tweets)
            
            # ネットワーク構築
            network = {
                "center_user": {
                    "id": center_user.id,
                    "username": center_user.username,
                    "name": center_user.name,
                    "followers": center_user.public_metrics.get("followers_count", 0),
                    "following": center_user.public_metrics.get("following_count", 0)
                },
                "connected_users": connected_users,
                "network_size": len(connected_users),
                "analysis_depth": depth,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # ネットワーク統計
            network["statistics"] = self._calculate_network_statistics(connected_users)
            
            logger.info(f"ユーザーネットワーク分析完了: {username}")
            return network
            
        except Exception as e:
            logger.error(f"ユーザーネットワーク分析エラー: {e}")
            return {"error": f"ネットワーク分析エラー: {str(e)}"}
    
    def _is_valid_user(self, user: User) -> bool:
        """
        ユーザーの有効性チェック
        
        Args:
            user (User): ユーザー情報
            
        Returns:
            bool: 有効性フラグ
        """
        metrics = user.public_metrics
        followers = metrics.get("followers_count", 0)
        following = metrics.get("following_count", 0)
        
        # 基本フィルタ
        if followers < self.min_followers or followers > self.max_followers:
            return False
        
        # スパムアカウント除外（フォロー/フォロワー比率チェック）
        if following > 0:
            follow_ratio = followers / following
            if follow_ratio < 0.1 or follow_ratio > 10:  # 極端な比率は除外
                return False
        
        # デフォルト画像チェック（簡易）
        if "default_profile_image" in user.profile_image_url:
            return False
        
        return True
    
    async def _analyze_user(self, user: User) -> Dict[str, Any]:
        """
        ユーザー分析
        
        Args:
            user (User): ユーザー情報
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        metrics = user.public_metrics
        followers = metrics.get("followers_count", 0)
        following = metrics.get("following_count", 0)
        tweets_count = metrics.get("tweet_count", 0)
        
        # エンゲージメント率推定（簡易）
        if tweets_count > 0:
            estimated_engagement_rate = min((followers * 0.02) / tweets_count, 0.1)
        else:
            estimated_engagement_rate = 0
        
        # 関連性スコア計算
        relevance_score = self._calculate_relevance_score(user)
        
        # アクティビティレベル推定
        activity_level = self._estimate_activity_level(user)
        
        return {
            "user_info": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "description": user.description,
                "verified": user.verified,
                "created_at": user.created_at,
                "profile_image_url": user.profile_image_url
            },
            "metrics": metrics,
            "analysis": {
                "estimated_engagement_rate": round(estimated_engagement_rate, 4),
                "follow_ratio": round(followers / max(following, 1), 2),
                "activity_level": activity_level,
                "relevance_score": relevance_score,
                "user_type": self._classify_user_type(user)
            },
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _analyze_influencer(self, user: User, sample_tweet) -> Dict[str, Any]:
        """
        インフルエンサー分析
        
        Args:
            user (User): ユーザー情報
            sample_tweet: サンプルツイート
            
        Returns:
            Dict[str, Any]: インフルエンサー分析結果
        """
        basic_analysis = await self._analyze_user(user)
        
        # インフルエンススコア計算
        followers = user.public_metrics.get("followers_count", 0)
        engagement = sample_tweet.public_metrics
        
        # サンプルツイートのエンゲージメント分析
        likes = engagement.get("like_count", 0)
        retweets = engagement.get("retweet_count", 0)
        replies = engagement.get("reply_count", 0)
        
        total_engagement = likes + retweets + replies
        engagement_rate = total_engagement / max(followers, 1)
        
        # インフルエンススコア（複合指標）
        influence_score = (
            (followers * 0.3) +
            (total_engagement * 10) +
            (engagement_rate * 1000) +
            (1 if user.verified else 0) * 500
        )
        
        basic_analysis["influence_analysis"] = {
            "influence_score": round(influence_score, 2),
            "engagement_rate": round(engagement_rate, 4),
            "sample_engagement": {
                "likes": likes,
                "retweets": retweets,
                "replies": replies,
                "total": total_engagement
            },
            "influencer_tier": self._classify_influencer_tier(followers, engagement_rate)
        }
        
        return basic_analysis
    
    def _extract_connected_users(self, tweets) -> List[Dict[str, Any]]:
        """
        ツイートから関連ユーザーを抽出
        
        Args:
            tweets: ツイートリスト
            
        Returns:
            List[Dict[str, Any]]: 関連ユーザーリスト
        """
        connected_users = {}
        
        for tweet in tweets:
            # メンション抽出
            entities = tweet.entities
            if entities and "mentions" in entities:
                for mention in entities["mentions"]:
                    username = mention.get("username")
                    if username:
                        if username not in connected_users:
                            connected_users[username] = {
                                "username": username,
                                "mention_count": 0,
                                "reply_count": 0,
                                "connection_strength": 0
                            }
                        connected_users[username]["mention_count"] += 1
            
            # リプライ抽出
            referenced_tweets = tweet.referenced_tweets
            if referenced_tweets:
                for ref in referenced_tweets:
                    if ref.get("type") == "replied_to":
                        # リプライ対象の分析（実際の実装では詳細取得が必要）
                        pass
        
        # 接続強度計算
        for user_data in connected_users.values():
            mentions = user_data["mention_count"]
            replies = user_data["reply_count"]
            user_data["connection_strength"] = mentions * 1 + replies * 2
        
        # 強度順にソート
        sorted_users = sorted(
            connected_users.values(),
            key=lambda x: x["connection_strength"],
            reverse=True
        )
        
        return sorted_users[:20]  # 上位20ユーザー
    
    def _calculate_network_statistics(self, connected_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ネットワーク統計計算
        
        Args:
            connected_users (List[Dict[str, Any]]): 関連ユーザーリスト
            
        Returns:
            Dict[str, Any]: ネットワーク統計
        """
        if not connected_users:
            return {"total_connections": 0}
        
        total_mentions = sum(user.get("mention_count", 0) for user in connected_users)
        total_replies = sum(user.get("reply_count", 0) for user in connected_users)
        
        strengths = [user.get("connection_strength", 0) for user in connected_users]
        avg_strength = sum(strengths) / len(strengths) if strengths else 0
        
        return {
            "total_connections": len(connected_users),
            "total_mentions": total_mentions,
            "total_replies": total_replies,
            "average_connection_strength": round(avg_strength, 2),
            "strongest_connection": max(strengths) if strengths else 0,
            "network_density": min(len(connected_users) / 100, 1.0)  # 正規化された密度
        }
    
    def _calculate_relevance_score(self, user: User) -> float:
        """
        関連性スコア計算
        
        Args:
            user (User): ユーザー情報
            
        Returns:
            float: 関連性スコア
        """
        score = 0.5  # ベーススコア
        
        # フォロワー数による調整
        followers = user.public_metrics.get("followers_count", 0)
        if 1000 <= followers <= 50000:
            score += 0.2  # 適度なフォロワー数
        elif followers > 50000:
            score += 0.1  # 大規模アカウント
        
        # 認証バッジ
        if user.verified:
            score += 0.2
        
        # プロフィール情報の充実度
        if user.description and len(user.description) > 20:
            score += 0.1
        
        # アカウント年数（簡易推定）
        if user.created_at:
            # 実際の実装では詳細な日付計算が必要
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_activity_level(self, user: User) -> str:
        """
        アクティビティレベル推定
        
        Args:
            user (User): ユーザー情報
            
        Returns:
            str: アクティビティレベル
        """
        tweets_count = user.public_metrics.get("tweet_count", 0)
        
        if tweets_count > 10000:
            return "very_high"
        elif tweets_count > 5000:
            return "high"
        elif tweets_count > 1000:
            return "medium"
        elif tweets_count > 100:
            return "low"
        else:
            return "very_low"
    
    def _classify_user_type(self, user: User) -> str:
        """
        ユーザータイプ分類
        
        Args:
            user (User): ユーザー情報
            
        Returns:
            str: ユーザータイプ
        """
        description = user.description.lower() if user.description else ""
        followers = user.public_metrics.get("followers_count", 0)
        
        if user.verified:
            return "verified"
        elif followers > 100000:
            return "macro_influencer"
        elif followers > 10000:
            return "micro_influencer"
        elif any(word in description for word in ["bot", "自動", "automatic"]):
            return "bot"
        elif any(word in description for word in ["企業", "company", "corp", "株式会社"]):
            return "corporate"
        elif any(word in description for word in ["個人", "personal", "趣味"]):
            return "personal"
        else:
            return "general"
    
    def _classify_influencer_tier(self, followers: int, engagement_rate: float) -> str:
        """
        インフルエンサー階層分類
        
        Args:
            followers (int): フォロワー数
            engagement_rate (float): エンゲージメント率
            
        Returns:
            str: インフルエンサー階層
        """
        if followers > 1000000:
            return "mega_influencer"
        elif followers > 100000:
            return "macro_influencer"
        elif followers > 10000:
            if engagement_rate > 0.05:  # 5%以上
                return "high_engagement_micro"
            else:
                return "micro_influencer"
        elif followers > 1000:
            return "nano_influencer"
        else:
            return "emerging"


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_user_picker():
        """UserPickerのテスト"""
        picker = UserPicker()
        
        if not picker.twitter_client.is_available():
            print("TwitterClientが利用できません（API認証情報を確認してください）")
            return
        
        print("=== キーワードベースユーザー発見テスト ===")
        users = await picker.discover_users_by_keywords(["AI", "機械学習"], max_users=5)
        print(f"発見ユーザー数: {len(users)}")
        
        for user in users[:3]:
            user_info = user.get("user_info", {})
            analysis = user.get("analysis", {})
            print(f"- @{user_info.get('username', 'N/A')} (関連性: {analysis.get('relevance_score', 0)})")
        
        print("\n=== インフルエンサー発見テスト ===")
        influencers = await picker.find_influencers_in_topic("Python", min_followers=5000, max_results=3)
        print(f"発見インフルエンサー数: {len(influencers)}")
        
        for influencer in influencers:
            user_info = influencer.get("user_info", {})
            influence = influencer.get("influence_analysis", {})
            print(f"- @{user_info.get('username', 'N/A')} (影響力: {influence.get('influence_score', 0)})")
    
    # テスト実行
    asyncio.run(test_user_picker())