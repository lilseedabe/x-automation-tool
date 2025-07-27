"""
X (Twitter) API統合クライアント（レートリミッター対応）

このモジュールは以下の機能を提供します：
- X API v2との通信
- ツイート取得・投稿
- ユーザー情報取得
- いいね・リポスト自動化
- エンゲージユーザー取得機能
- 厳密なレート制限管理
- エラーハンドリング
"""

import os
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import time
import random

# X API関連
import tweepy
import httpx

# 内部モジュール
from .rate_limiter import UserRateLimiter, APIEndpoint, rate_limiter_manager

# ログ
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# データモデル
# =============================================================================

class Tweet:
    """ツイートモデル"""
    
    def __init__(self, tweet_data: Dict[str, Any]):
        self.id = tweet_data.get("id")
        self.text = tweet_data.get("text", "")
        self.author_id = tweet_data.get("author_id")
        self.created_at = tweet_data.get("created_at")
        self.public_metrics = tweet_data.get("public_metrics", {})
        self.context_annotations = tweet_data.get("context_annotations", [])
        self.entities = tweet_data.get("entities", {})
        self.referenced_tweets = tweet_data.get("referenced_tweets", [])
        self.raw_data = tweet_data

class User:
    """ユーザーモデル"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data.get("id")
        self.username = user_data.get("username", "")
        self.name = user_data.get("name", "")
        self.description = user_data.get("description", "")
        self.public_metrics = user_data.get("public_metrics", {})
        self.verified = user_data.get("verified", False)
        self.created_at = user_data.get("created_at")
        self.profile_image_url = user_data.get("profile_image_url", "")
        self.raw_data = user_data

# =============================================================================
# レート制限対応TwitterClient
# =============================================================================

class TwitterClient:
    """
    レート制限対応 X (Twitter) API統合クライアント
    
    X API v2を使用してツイートやユーザー情報を取得・操作します。
    ユーザー単位でのレート制限を厳密に管理します。
    """
    
    def __init__(self, user_id: str, credentials: Dict[str, str] = None):
        """
        初期化
        
        Args:
            user_id (str): ユーザーID（レート制限管理用）
            credentials (Dict[str, str]): API認証情報
        """
        self.user_id = user_id
        
        # 認証情報の設定
        if credentials:
            self.api_key = credentials.get("api_key")
            self.api_secret = credentials.get("api_secret")
            self.access_token = credentials.get("access_token")
            self.access_token_secret = credentials.get("access_token_secret")
            self.bearer_token = credentials.get("bearer_token")
        else:
            self.api_key = os.getenv("X_API_KEY")
            self.api_secret = os.getenv("X_API_SECRET")
            self.access_token = os.getenv("X_ACCESS_TOKEN")
            self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
            self.bearer_token = os.getenv("X_BEARER_TOKEN")
        
        # クライアントの初期化
        self.api_v1 = None
        self.api_v2 = None
        self.client = None
        
        self._initialize_clients()
        
        # レートリミッター取得
        self.rate_limiter = rate_limiter_manager.get_limiter(user_id)
        
        # 自動化統計
        self.automation_stats = {
            "likes_today": 0,
            "retweets_today": 0,
            "last_reset": datetime.now().date()
        }
        
        logger.info(f"TwitterClient初期化完了: user_id={user_id}")
    
    def _initialize_clients(self):
        """APIクライアントの初期化"""
        try:
            if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                # OAuth 1.0a 認証（API v1.1用）
                auth = tweepy.OAuth1UserHandler(
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_token_secret
                )
                self.api_v1 = tweepy.API(auth, wait_on_rate_limit=False)  # 自前でレート制限管理
                
                # API v2クライアント
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=False  # 自前でレート制限管理
                )
                
                logger.info("X APIクライアント初期化成功")
            else:
                logger.warning("X API認証情報が不完全です")
                
        except Exception as e:
            logger.error(f"X APIクライアント初期化エラー: {e}")
    
    def _reset_daily_stats(self):
        """日次統計のリセット"""
        today = datetime.now().date()
        if self.automation_stats["last_reset"] != today:
            self.automation_stats.update({
                "likes_today": 0,
                "retweets_today": 0,
                "last_reset": today
            })
            logger.info("日次統計をリセットしました")
    
    def _add_human_delay(self, min_seconds: int = 2, max_seconds: int = 8):
        """人間らしい遅延を追加"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.info(f"人間らしい遅延: {delay:.1f}秒")
        time.sleep(delay)
    
    def is_available(self) -> bool:
        """
        X APIクライアントが利用可能かチェック
        
        Returns:
            bool: 利用可能フラグ
        """
        return self.client is not None
    
    async def verify_credentials(self) -> Dict[str, Any]:
        """
        認証情報の検証
        
        Returns:
            Dict[str, Any]: 検証結果
        """
        if not self.is_available():
            return {"error": "X APIクライアントが利用できません"}
        
        try:
            # レート制限チェック
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.GET_USER)
            if not can_request:
                return {"error": f"レート制限: {error_msg}"}
            
            # リクエスト実行
            me = self.client.get_me()
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.GET_USER)
            
            if me.data:
                return {
                    "success": True,
                    "user": {
                        "id": me.data.id,
                        "username": me.data.username,
                        "name": me.data.name
                    },
                    "message": "認証成功"
                }
            else:
                return {"error": "認証情報の検証に失敗しました"}
                
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.GET_USER, reset_time)
            return {"error": "レート制限に達しました。しばらく待ってから再試行してください"}
        except Exception as e:
            logger.error(f"認証情報検証エラー: {e}")
            return {"error": f"認証エラー: {str(e)}"}
    
    # =============================================================================
    # エンゲージユーザー取得機能（レート制限対応）
    # =============================================================================
    
    async def get_tweet_liking_users(self, tweet_id: str, max_results: int = 100) -> List[User]:
        """
        ツイートにいいねしたユーザーを取得（レート制限対応）
        
        Args:
            tweet_id (str): ツイートID
            max_results (int): 最大取得数
            
        Returns:
            List[User]: いいねしたユーザーのリスト
        """
        if not self.is_available():
            logger.error("X APIクライアントが利用できません")
            return []
        
        try:
            # レート制限チェック
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.GET_LIKING_USERS)
            if not can_request:
                logger.warning(f"いいねユーザー取得レート制限: {error_msg}")
                return []
            
            # API v2を使用してライキングユーザーを取得
            response = self.client.get_liking_users(
                id=tweet_id,
                max_results=min(max_results, 100),
                user_fields=['id', 'username', 'name', 'description', 'public_metrics', 'verified']
            )
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.GET_LIKING_USERS)
            
            users = []
            if response.data:
                for user_data in response.data:
                    users.append(User(user_data.data))
            
            logger.info(f"いいねユーザー取得完了: {len(users)}件")
            return users
            
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.GET_LIKING_USERS, reset_time)
            logger.warning("いいねユーザー取得レート制限に達しました")
            return []
        except tweepy.Forbidden:
            logger.warning("いいねユーザー取得権限がありません")
            return []
        except Exception as e:
            logger.error(f"いいねユーザー取得エラー: {e}")
            return []
    
    async def get_tweet_retweeting_users(self, tweet_id: str, max_results: int = 100) -> List[User]:
        """
        ツイートをリツイートしたユーザーを取得（レート制限対応）
        
        Args:
            tweet_id (str): ツイートID
            max_results (int): 最大取得数
            
        Returns:
            List[User]: リツイートしたユーザーのリスト
        """
        if not self.is_available():
            logger.error("X APIクライアントが利用できません")
            return []
        
        try:
            # レート制限チェック
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.GET_RETWEETERS)
            if not can_request:
                logger.warning(f"リツイートユーザー取得レート制限: {error_msg}")
                return []
            
            # API v2を使用してリツイートユーザーを取得
            response = self.client.get_retweeters(
                id=tweet_id,
                max_results=min(max_results, 100),
                user_fields=['id', 'username', 'name', 'description', 'public_metrics', 'verified']
            )
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.GET_RETWEETERS)
            
            users = []
            if response.data:
                for user_data in response.data:
                    users.append(User(user_data.data))
            
            logger.info(f"リツイートユーザー取得完了: {len(users)}件")
            return users
            
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.GET_RETWEETERS, reset_time)
            logger.warning("リツイートユーザー取得レート制限に達しました")
            return []
        except tweepy.Forbidden:
            logger.warning("リツイートユーザー取得権限がありません")
            return []
        except Exception as e:
            logger.error(f"リツイートユーザー取得エラー: {e}")
            return []
    
    async def get_engaging_users(self, tweet_id: str, max_users: int = 50) -> List[User]:
        """
        ツイートにエンゲージしたユーザーを取得（いいね + リツイート）
        
        Args:
            tweet_id (str): ツイートID
            max_users (int): 最大取得数
            
        Returns:
            List[User]: エンゲージしたユーザーのリスト（重複除去済み）
        """
        try:
            # いいねユーザーとリツイートユーザーを並行取得
            # ただし、レート制限を考慮して段階的に取得
            
            # まずいいねユーザーを取得
            liking_users = await self.get_tweet_liking_users(tweet_id, max_users)
            
            # レート制限を避けるため少し待機
            await asyncio.sleep(1)
            
            # 次にリツイートユーザーを取得
            retweeting_users = await self.get_tweet_retweeting_users(tweet_id, max_users // 2)
            
            # ユーザーIDで重複除去
            all_users = {}
            
            # いいねユーザーを追加
            for user in liking_users:
                all_users[user.id] = user
            
            # リツイートユーザーを追加（重複は上書きされない）
            for user in retweeting_users:
                if user.id not in all_users:
                    all_users[user.id] = user
            
            unique_users = list(all_users.values())
            
            # 最大数で制限
            if len(unique_users) > max_users:
                unique_users = unique_users[:max_users]
            
            logger.info(f"エンゲージユーザー取得完了: {len(unique_users)}件")
            return unique_users
            
        except Exception as e:
            logger.error(f"エンゲージユーザー取得エラー: {e}")
            return []
    
    async def get_user_recent_tweets(self, user_id: str, max_results: int = 10) -> List[Tweet]:
        """
        ユーザーの最新ツイートを取得（レート制限対応）
        
        Args:
            user_id (str): ユーザーID
            max_results (int): 最大取得数
            
        Returns:
            List[Tweet]: 最新ツイートリスト
        """
        if not self.is_available():
            logger.error("X APIクライアントが利用できません")
            return []
        
        try:
            # レート制限チェック
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.GET_TWEETS)
            if not can_request:
                logger.warning(f"ユーザーツイート取得レート制限: {error_msg}")
                return []
            
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                exclude=['retweets', 'replies'],  # リツイートと返信を除外
                tweet_fields=[
                    'id', 'text', 'author_id', 'created_at', 'public_metrics',
                    'context_annotations', 'entities'
                ]
            )
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.GET_TWEETS)
            
            tweets = []
            if response.data:
                for tweet_data in response.data:
                    tweets.append(Tweet(tweet_data.data))
            
            logger.info(f"ユーザー最新ツイート取得完了: {len(tweets)}件")
            return tweets
            
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.GET_TWEETS, reset_time)
            logger.warning("ユーザーツイート取得レート制限に達しました")
            return []
        except Exception as e:
            logger.error(f"ユーザー最新ツイート取得エラー: {e}")
            return []
    
    # =============================================================================
    # いいね♡自動化機能（レート制限対応）
    # =============================================================================
    
    async def like_tweet(self, tweet_id: str, safety_check: bool = True) -> Dict[str, Any]:
        """
        ツイートにいいね♡をする（レート制限対応）
        
        Args:
            tweet_id (str): ツイートID
            safety_check (bool): 安全性チェック実行フラグ
            
        Returns:
            Dict[str, Any]: 実行結果
        """
        if not self.is_available():
            return {"error": "X APIクライアントが利用できません"}
        
        self._reset_daily_stats()
        
        try:
            # レート制限チェック（重要！）
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.LIKE)
            if not can_request:
                return {"error": f"いいねレート制限: {error_msg}"}
            
            # 安全性チェック
            if safety_check:
                tweet = await self.get_tweet_by_id(tweet_id)
                if not tweet:
                    return {"error": "ツイートが見つかりません"}
                
                # 不適切なコンテンツチェック
                if self._is_unsafe_content(tweet.text):
                    return {"error": "安全性チェックで除外されました"}
            
            # 人間らしい遅延
            self._add_human_delay(2, 6)
            
            # いいね実行
            response = self.client.like(tweet_id)
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.LIKE)
            
            if response.data and response.data.get("liked"):
                # 統計更新
                self.automation_stats["likes_today"] += 1
                
                logger.info(f"いいね実行成功: {tweet_id}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "action": "like",
                    "message": "いいねを実行しました",
                    "rate_limit_info": self.rate_limiter.get_usage_stats().get("like", {})
                }
            else:
                return {"error": "いいねの実行に失敗しました"}
                
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.LIKE, reset_time)
            return {"error": "いいねレート制限に達しました。15分後に再試行してください"}
        except tweepy.Forbidden:
            logger.warning("いいね権限がありません")
            return {"error": "このツイートにいいねする権限がありません"}
        except Exception as e:
            logger.error(f"いいね実行エラー: {e}")
            return {"error": f"いいね実行エラー: {str(e)}"}
    
    # =============================================================================
    # リポスト自動化機能（レート制限対応）
    # =============================================================================
    
    async def retweet(self, tweet_id: str, safety_check: bool = True) -> Dict[str, Any]:
        """
        ツイートをリポスト（リツイート）する（レート制限対応）
        
        Args:
            tweet_id (str): ツイートID
            safety_check (bool): 安全性チェック実行フラグ
            
        Returns:
            Dict[str, Any]: 実行結果
        """
        if not self.is_available():
            return {"error": "X APIクライアントが利用できません"}
        
        self._reset_daily_stats()
        
        try:
            # レート制限チェック（重要！）
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.RETWEET)
            if not can_request:
                return {"error": f"リポストレート制限: {error_msg}"}
            
            # 安全性チェック
            if safety_check:
                tweet = await self.get_tweet_by_id(tweet_id)
                if not tweet:
                    return {"error": "ツイートが見つかりません"}
                
                # 不適切なコンテンツチェック
                if self._is_unsafe_content(tweet.text):
                    return {"error": "安全性チェックで除外されました"}
                
                # 品質チェック
                if not self._is_quality_content(tweet):
                    return {"error": "品質チェックで除外されました"}
            
            # 人間らしい遅延（リポストはより慎重に）
            self._add_human_delay(5, 12)
            
            # リポスト実行
            response = self.client.retweet(tweet_id)
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.RETWEET)
            
            if response.data and response.data.get("retweeted"):
                # 統計更新
                self.automation_stats["retweets_today"] += 1
                
                logger.info(f"リポスト実行成功: {tweet_id}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "action": "retweet",
                    "message": "リポストを実行しました",
                    "rate_limit_info": self.rate_limiter.get_usage_stats().get("retweet", {})
                }
            else:
                return {"error": "リポストの実行に失敗しました"}
                
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.RETWEET, reset_time)
            return {"error": "リポストレート制限に達しました。しばらく待ってから再試行してください"}
        except tweepy.Forbidden:
            logger.warning("リポスト権限がありません")
            return {"error": "このツイートをリポストする権限がありません"}
        except Exception as e:
            logger.error(f"リポスト実行エラー: {e}")
            return {"error": f"リポスト実行エラー: {str(e)}"}
    
    # =============================================================================
    # レート制限統計
    # =============================================================================
    
    async def get_rate_limit_stats(self) -> Dict[str, Any]:
        """
        レート制限使用状況を取得
        
        Returns:
            Dict[str, Any]: レート制限統計
        """
        return {
            "user_id": self.user_id,
            "rate_limits": self.rate_limiter.get_usage_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_automation_stats(self) -> Dict[str, Any]:
        """自動化統計情報を取得（レート制限情報付き）"""
        self._reset_daily_stats()
        
        rate_stats = await self.get_rate_limit_stats()
        
        return {
            "today": {
                "likes": self.automation_stats["likes_today"],
                "retweets": self.automation_stats["retweets_today"],
                "date": self.automation_stats["last_reset"].isoformat()
            },
            "rate_limits": rate_stats["rate_limits"],
            "safety": {
                "safety_checks_enabled": True,
                "human_like_delays": True,
                "rate_limit_protection": True
            }
        }
    
    # =============================================================================
    # 安全性・品質チェック（既存）
    # =============================================================================
    
    def _is_unsafe_content(self, text: str) -> bool:
        """不適切なコンテンツをチェック"""
        unsafe_keywords = [
            "炎上", "批判", "叩き", "晒し", "攻撃", "差別",
            "ヘイト", "詐欺", "スパム", "宣伝", "広告",
            "政治", "選挙", "投票", "宗教"
        ]
        
        text_lower = text.lower()
        
        for keyword in unsafe_keywords:
            if keyword in text_lower:
                logger.info(f"不適切キーワード検出: {keyword}")
                return True
        
        if len(text) > 200:
            return True
        
        if text.count("http") > 2:
            return True
        
        return False
    
    def _is_quality_content(self, tweet: Tweet) -> bool:
        """コンテンツの品質をチェック"""
        metrics = tweet.public_metrics
        
        like_count = metrics.get("like_count", 0)
        retweet_count = metrics.get("retweet_count", 0)
        reply_count = metrics.get("reply_count", 0)
        
        total_engagement = like_count + retweet_count + reply_count
        
        if total_engagement < 3:
            return False
        
        if like_count > 0 and (retweet_count / like_count) > 3:
            return False
        
        return True
    
    # =============================================================================
    # 既存の基本機能（レート制限対応）
    # =============================================================================
    
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[Tweet]:
        """ツイートIDでツイートを取得（レート制限対応）"""
        if not self.is_available():
            logger.error("X APIクライアントが利用できません")
            return None
        
        try:
            # レート制限チェック
            can_request, error_msg = await self.rate_limiter.can_make_request(APIEndpoint.GET_TWEETS)
            if not can_request:
                logger.warning(f"ツイート取得レート制限: {error_msg}")
                return None
            
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=[
                    "id", "text", "author_id", "created_at", "public_metrics",
                    "context_annotations", "entities", "referenced_tweets"
                ],
                expansions=["author_id"]
            )
            
            # レート制限消費
            await self.rate_limiter.consume_request(APIEndpoint.GET_TWEETS)
            
            if response.data:
                return Tweet(response.data.data)
            else:
                logger.warning(f"ツイートが見つかりません: {tweet_id}")
                return None
                
        except tweepy.TooManyRequests as e:
            # 429エラーハンドリング
            reset_time = getattr(e.response, 'headers', {}).get('x-rate-limit-reset')
            await self.rate_limiter.handle_429_error(APIEndpoint.GET_TWEETS, reset_time)
            logger.warning("ツイート取得レート制限に達しました")
            return None
        except Exception as e:
            logger.error(f"ツイート取得エラー: {e}")
            return None


# =============================================================================
# ファクトリー関数
# =============================================================================

def create_twitter_client(user_id: str, credentials: Dict[str, str] = None) -> TwitterClient:
    """
    TwitterClientを作成
    
    Args:
        user_id (str): ユーザーID
        credentials (Dict[str, str]): API認証情報
        
    Returns:
        TwitterClient: レート制限対応TwitterClient
    """
    return TwitterClient(user_id, credentials)


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_rate_limited_client():
        """レート制限対応TwitterClientのテスト"""
        client = create_twitter_client("test_user")
        
        if not client.is_available():
            print("TwitterClientが利用できません（API認証情報を確認してください）")
            return
        
        print("=== レート制限対応TwitterClientテスト ===")
        
        # レート制限統計確認
        stats = await client.get_rate_limit_stats()
        print(f"レート制限統計: {stats}")
        
        # いいね制限テスト（15分で1回のみ）
        print("\n=== いいね制限テスト ===")
        for i in range(3):
            result = await client.like_tweet("test_tweet_123")
            print(f"いいね {i+1}回目: {result}")
    
    # テスト実行
    asyncio.run(test_rate_limited_client())