"""
🐦 X自動反応ツール - Twitter APIクライアント
X API v2を使用したツイート操作とエンゲージメント分析
"""

import logging
import tweepy
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TwitterAPIClient:
    """Twitter API v2クライアント"""
    
    def __init__(self, api_keys: Dict[str, str]):
        """
        Twitter APIクライアント初期化
        
        Args:
            api_keys: APIキー辞書
        """
        self.api_keys = api_keys
        self._client = None
        self._api = None
        self._init_client()
    
    def _init_client(self):
        """Twitter API v2クライアント初期化"""
        try:
            # Twitter API v2クライアント
            self._client = tweepy.Client(
                bearer_token=self.api_keys.get("bearer_token"),
                consumer_key=self.api_keys["api_key"],
                consumer_secret=self.api_keys["api_secret"],
                access_token=self.api_keys["access_token"],
                access_token_secret=self.api_keys["access_token_secret"],
                wait_on_rate_limit=True
            )
            
            # Twitter API v1.1（一部機能用）
            auth = tweepy.OAuthHandler(
                self.api_keys["api_key"],
                self.api_keys["api_secret"]
            )
            auth.set_access_token(
                self.api_keys["access_token"],
                self.api_keys["access_token_secret"]
            )
            self._api = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("✅ Twitter APIクライアント初期化完了")
            
        except Exception as e:
            logger.error(f"❌ Twitter APIクライアント初期化エラー: {str(e)}")
            raise
    
    async def create_tweet(self, text: str) -> Dict[str, Any]:
        """ツイート投稿"""
        try:
            response = self._client.create_tweet(text=text)
            
            if response.data:
                return {
                    "success": True,
                    "tweet_id": response.data["id"],
                    "text": text
                }
            else:
                return {
                    "success": False,
                    "error": "ツイート投稿に失敗しました"
                }
                
        except Exception as e:
            logger.error(f"❌ ツイート投稿エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """ツイートにいいね"""
        try:
            response = self._client.like(tweet_id)
            
            if response.data:
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "liked": response.data["liked"]
                }
            else:
                return {
                    "success": False,
                    "error": "いいねに失敗しました"
                }
                
        except Exception as e:
            logger.error(f"❌ いいねエラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """リツイート"""
        try:
            response = self._client.retweet(tweet_id)
            
            if response.data:
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "retweeted": response.data["retweeted"]
                }
            else:
                return {
                    "success": False,
                    "error": "リツイートに失敗しました"
                }
                
        except Exception as e:
            logger.error(f"❌ リツイートエラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reply_to_tweet(self, tweet_id: str, text: str) -> Dict[str, Any]:
        """ツイートにリプライ"""
        try:
            response = self._client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            
            if response.data:
                return {
                    "success": True,
                    "tweet_id": response.data["id"],
                    "reply_to": tweet_id,
                    "text": text
                }
            else:
                return {
                    "success": False,
                    "error": "リプライに失敗しました"
                }
                
        except Exception as e:
            logger.error(f"❌ リプライエラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """ツイート詳細取得"""
        try:
            response = self._client.get_tweet(
                tweet_id,
                expansions=["author_id"],
                tweet_fields=["created_at", "public_metrics", "context_annotations"],
                user_fields=["username", "name", "public_metrics"]
            )
            
            if response.data:
                tweet = response.data
                author = response.includes["users"][0] if response.includes and "users" in response.includes else None
                
                return {
                    "success": True,
                    "tweet": {
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "public_metrics": tweet.public_metrics,
                        "author": {
                            "id": author.id if author else None,
                            "username": author.username if author else None,
                            "name": author.name if author else None,
                            "public_metrics": author.public_metrics if author else None
                        } if author else None
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "ツイートが見つかりません"
                }
                
        except Exception as e:
            logger.error(f"❌ ツイート取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_liking_users(self, tweet_id: str, max_results: int = 100) -> Dict[str, Any]:
        """ツイートにいいねしたユーザー一覧取得"""
        try:
            response = self._client.get_liking_users(
                tweet_id,
                max_results=min(max_results, 100),
                user_fields=["username", "name", "public_metrics", "description", "verified"]
            )
            
            if response.data:
                users = []
                for user in response.data:
                    users.append({
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "description": user.description,
                        "verified": user.verified,
                        "public_metrics": user.public_metrics,
                        "engagement_type": "like",
                        "engagement_time": datetime.now(timezone.utc)
                    })
                
                return {
                    "success": True,
                    "users": users,
                    "count": len(users)
                }
            else:
                return {
                    "success": True,
                    "users": [],
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"❌ いいねユーザー取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_retweeting_users(self, tweet_id: str, max_results: int = 100) -> Dict[str, Any]:
        """リツイートしたユーザー一覧取得"""
        try:
            response = self._client.get_retweeted_by(
                tweet_id,
                max_results=min(max_results, 100),
                user_fields=["username", "name", "public_metrics", "description", "verified"]
            )
            
            if response.data:
                users = []
                for user in response.data:
                    users.append({
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "description": user.description,
                        "verified": user.verified,
                        "public_metrics": user.public_metrics,
                        "engagement_type": "retweet",
                        "engagement_time": datetime.now(timezone.utc)
                    })
                
                return {
                    "success": True,
                    "users": users,
                    "count": len(users)
                }
            else:
                return {
                    "success": True,
                    "users": [],
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"❌ リツイートユーザー取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_tweets(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """ユーザーの最新ツイート取得"""
        try:
            response = self._client.get_users_tweets(
                user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "context_annotations"],
                exclude=["retweets", "replies"]  # リツイートとリプライを除外
            )
            
            if response.data:
                tweets = []
                for tweet in response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "public_metrics": tweet.public_metrics,
                        "context_annotations": getattr(tweet, 'context_annotations', [])
                    })
                
                return {
                    "success": True,
                    "tweets": tweets,
                    "count": len(tweets)
                }
            else:
                return {
                    "success": True,
                    "tweets": [],
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"❌ ユーザーツイート取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """ユーザー名からユーザー情報を取得"""
        try:
            response = self._client.get_user(
                username=username,
                user_fields=["username", "name", "public_metrics", "description", "verified", "created_at"]
            )
            
            if response.data:
                user = response.data
                return {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "description": user.description,
                        "verified": user.verified,
                        "public_metrics": user.public_metrics,
                        "created_at": user.created_at
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません"
                }
                
        except Exception as e:
            logger.error(f"❌ ユーザー取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_tweets(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """ツイート検索"""
        try:
            response = self._client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "author_id"],
                user_fields=["username", "name", "public_metrics"],
                expansions=["author_id"]
            )
            
            if response.data:
                tweets = []
                users_dict = {}
                
                # ユーザー情報をマッピング
                if response.includes and "users" in response.includes:
                    for user in response.includes["users"]:
                        users_dict[user.id] = user
                
                for tweet in response.data:
                    author = users_dict.get(tweet.author_id)
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "public_metrics": tweet.public_metrics,
                        "author": {
                            "id": author.id if author else tweet.author_id,
                            "username": author.username if author else None,
                            "name": author.name if author else None,
                            "public_metrics": author.public_metrics if author else None
                        } if author else {"id": tweet.author_id}
                    })
                
                return {
                    "success": True,
                    "tweets": tweets,
                    "count": len(tweets)
                }
            else:
                return {
                    "success": True,
                    "tweets": [],
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"❌ ツイート検索エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_tweet_id_from_url(self, tweet_url: str) -> Optional[str]:
        """ツイートURLからIDを抽出"""
        try:
            # https://twitter.com/username/status/1234567890
            # https://x.com/username/status/1234567890
            if "/status/" in tweet_url:
                tweet_id = tweet_url.split("/status/")[-1].split("?")[0].split("/")[0]
                # 数字のみかチェック
                if tweet_id.isdigit():
                    return tweet_id
            return None
        except Exception as e:
            logger.error(f"❌ ツイートID抽出エラー: {str(e)}")
            return None
    
    async def verify_credentials(self) -> Dict[str, Any]:
        """APIキーの認証状態を確認"""
        try:
            me = self._client.get_me(
                user_fields=["username", "name", "public_metrics", "verified"]
            )
            
            if me.data:
                user = me.data
                return {
                    "success": True,
                    "authenticated": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "verified": user.verified,
                        "public_metrics": user.public_metrics
                    }
                }
            else:
                return {
                    "success": False,
                    "authenticated": False,
                    "error": "認証情報の取得に失敗しました"
                }
                
        except Exception as e:
            logger.error(f"❌ 認証確認エラー: {str(e)}")
            return {
                "success": False,
                "authenticated": False,
                "error": str(e)
            }
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """レート制限状況を取得"""
        try:
            # Twitter API v1.1を使用してレート制限情報を取得
            rate_limit_status = self._api.rate_limit_status()
            
            return {
                "success": True,
                "rate_limits": rate_limit_status
            }
            
        except Exception as e:
            logger.error(f"❌ レート制限状況取得エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }