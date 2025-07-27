"""
X API レートリミッター

このモジュールは以下の機能を提供します：
- ユーザー単位のレート制限管理
- トークンバケット方式の実装
- リアルタイムの使用量追跡
- 429エラーハンドリング
- スケジューラ連携
"""

import asyncio
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
from enum import Enum

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# レート制限設定
# =============================================================================

class APIEndpoint(Enum):
    """API エンドポイント種別"""
    LIKE = "like"
    RETWEET = "retweet"
    GET_TWEETS = "get_tweets"
    GET_LIKING_USERS = "get_liking_users"
    GET_RETWEETERS = "get_retweeters"
    GET_USER = "get_user"
    SEARCH_TWEETS = "search_tweets"

@dataclass
class RateLimit:
    """レート制限設定"""
    requests_per_15min: int
    requests_per_24hour: int
    window_15min: int = 15 * 60  # 15分
    window_24hour: int = 24 * 60 * 60  # 24時間

# X API v2 レート制限設定
RATE_LIMITS = {
    APIEndpoint.LIKE: RateLimit(
        requests_per_15min=1,      # いいねは15分で1回のみ！
        requests_per_24hour=1000   # 24時間で1000回
    ),
    APIEndpoint.RETWEET: RateLimit(
        requests_per_15min=50,     # リツイートは15分で50回
        requests_per_24hour=1000   # 24時間で1000回（推定）
    ),
    APIEndpoint.GET_TWEETS: RateLimit(
        requests_per_15min=900,    # ツイート取得は15分で900回
        requests_per_24hour=900 * 96  # 24時間推定
    ),
    APIEndpoint.GET_LIKING_USERS: RateLimit(
        requests_per_15min=75,     # いいねユーザー取得は15分で75回
        requests_per_24hour=75 * 96  # 24時間推定
    ),
    APIEndpoint.GET_RETWEETERS: RateLimit(
        requests_per_15min=75,     # リツイーター取得は15分で75回
        requests_per_24hour=75 * 96  # 24時間推定
    ),
    APIEndpoint.GET_USER: RateLimit(
        requests_per_15min=900,    # ユーザー取得は15分で900回
        requests_per_24hour=900 * 96  # 24時間推定
    ),
    APIEndpoint.SEARCH_TWEETS: RateLimit(
        requests_per_15min=300,    # 検索は15分で300回
        requests_per_24hour=300 * 96  # 24時間推定
    )
}

# =============================================================================
# トークンバケット実装
# =============================================================================

@dataclass
class TokenBucket:
    """トークンバケット"""
    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens per second

    def consume(self, tokens: int = 1) -> bool:
        """
        トークンを消費
        
        Args:
            tokens (int): 消費するトークン数
            
        Returns:
            bool: 消費できた場合True
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """トークンを補充"""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            # 経過時間に応じてトークンを補充
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
    
    def get_available_tokens(self) -> int:
        """利用可能なトークン数を取得"""
        self._refill()
        return int(self.tokens)
    
    def time_until_token_available(self) -> float:
        """次のトークンが利用可能になるまでの秒数"""
        self._refill()
        
        if self.tokens >= 1:
            return 0
        
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate

# =============================================================================
# ユーザー単位レートリミッター
# =============================================================================

class UserRateLimiter:
    """
    ユーザー単位のレートリミッター
    
    各ユーザーのAPIトークンに対して独立したレート制限を管理
    """
    
    def __init__(self, user_id: str):
        """
        初期化
        
        Args:
            user_id (str): ユーザーID
        """
        self.user_id = user_id
        self.buckets_15min: Dict[APIEndpoint, TokenBucket] = {}
        self.buckets_24hour: Dict[APIEndpoint, TokenBucket] = {}
        self.request_history: Dict[APIEndpoint, List[float]] = {}
        
        # 各エンドポイント用のトークンバケットを初期化
        self._initialize_buckets()
        
        # 永続化パス
        self.state_file = f"data/users/{user_id}/rate_limit_state.json"
        
        # 既存状態を読み込み
        self._load_state()
        
        logger.info(f"UserRateLimiter初期化: user_id={user_id}")
    
    def _initialize_buckets(self):
        """トークンバケットを初期化"""
        now = time.time()
        
        for endpoint, limits in RATE_LIMITS.items():
            # 15分バケット
            self.buckets_15min[endpoint] = TokenBucket(
                capacity=limits.requests_per_15min,
                tokens=float(limits.requests_per_15min),
                last_refill=now,
                refill_rate=limits.requests_per_15min / limits.window_15min
            )
            
            # 24時間バケット
            self.buckets_24hour[endpoint] = TokenBucket(
                capacity=limits.requests_per_24hour,
                tokens=float(limits.requests_per_24hour),
                last_refill=now,
                refill_rate=limits.requests_per_24hour / limits.window_24hour
            )
            
            # リクエスト履歴
            self.request_history[endpoint] = []
    
    async def can_make_request(self, endpoint: APIEndpoint) -> Tuple[bool, Optional[str]]:
        """
        リクエスト可能かチェック
        
        Args:
            endpoint (APIEndpoint): APIエンドポイント
            
        Returns:
            Tuple[bool, Optional[str]]: (可能フラグ, エラーメッセージ)
        """
        if endpoint not in self.buckets_15min:
            return False, f"未対応のエンドポイント: {endpoint}"
        
        # 15分制限チェック
        bucket_15min = self.buckets_15min[endpoint]
        if not bucket_15min.consume(0):  # 消費せずにチェックのみ
            time_until_available = bucket_15min.time_until_token_available()
            return False, f"15分制限に達しています。{time_until_available/60:.1f}分後に再試行可能"
        
        # 24時間制限チェック
        bucket_24hour = self.buckets_24hour[endpoint]
        if not bucket_24hour.consume(0):  # 消費せずにチェックのみ
            time_until_available = bucket_24hour.time_until_token_available()
            return False, f"24時間制限に達しています。{time_until_available/3600:.1f}時間後に再試行可能"
        
        return True, None
    
    async def consume_request(self, endpoint: APIEndpoint) -> bool:
        """
        リクエストを消費（実際に実行する場合）
        
        Args:
            endpoint (APIEndpoint): APIエンドポイント
            
        Returns:
            bool: 消費できた場合True
        """
        if endpoint not in self.buckets_15min:
            return False
        
        # 両方のバケットからトークンを消費
        consumed_15min = self.buckets_15min[endpoint].consume(1)
        consumed_24hour = self.buckets_24hour[endpoint].consume(1)
        
        if consumed_15min and consumed_24hour:
            # リクエスト履歴に記録
            now = time.time()
            self.request_history[endpoint].append(now)
            
            # 古い履歴を削除（24時間以上前）
            cutoff = now - 24 * 60 * 60
            self.request_history[endpoint] = [
                req_time for req_time in self.request_history[endpoint]
                if req_time > cutoff
            ]
            
            # 状態を保存
            await self._save_state()
            
            logger.info(f"リクエスト消費: {endpoint.value}, user={self.user_id}")
            return True
        
        return False
    
    def get_usage_stats(self) -> Dict[str, Dict[str, any]]:
        """
        使用量統計を取得
        
        Returns:
            Dict[str, Dict[str, any]]: エンドポイント別使用量統計
        """
        stats = {}
        
        for endpoint in RATE_LIMITS.keys():
            bucket_15min = self.buckets_15min[endpoint]
            bucket_24hour = self.buckets_24hour[endpoint]
            limits = RATE_LIMITS[endpoint]
            
            # 15分制限の使用量
            used_15min = limits.requests_per_15min - bucket_15min.get_available_tokens()
            
            # 24時間制限の使用量
            used_24hour = limits.requests_per_24hour - bucket_24hour.get_available_tokens()
            
            # 次回利用可能時刻
            next_available_15min = bucket_15min.time_until_token_available()
            next_available_24hour = bucket_24hour.time_until_token_available()
            
            stats[endpoint.value] = {
                "15min_limit": limits.requests_per_15min,
                "15min_used": used_15min,
                "15min_remaining": bucket_15min.get_available_tokens(),
                "24hour_limit": limits.requests_per_24hour,
                "24hour_used": used_24hour,
                "24hour_remaining": bucket_24hour.get_available_tokens(),
                "next_available_seconds": max(next_available_15min, next_available_24hour),
                "can_make_request": bucket_15min.get_available_tokens() > 0 and bucket_24hour.get_available_tokens() > 0
            }
        
        return stats
    
    async def handle_429_error(self, endpoint: APIEndpoint, reset_time: Optional[int] = None):
        """
        429エラー（レート制限）を処理
        
        Args:
            endpoint (APIEndpoint): エラーが発生したエンドポイント
            reset_time (Optional[int]): リセット時刻（UNIX timestamp）
        """
        logger.warning(f"429エラー発生: {endpoint.value}, user={self.user_id}")
        
        # トークンを0にセット（強制的にレート制限状態に）
        if endpoint in self.buckets_15min:
            self.buckets_15min[endpoint].tokens = 0
        
        if reset_time:
            # リセット時刻が指定されている場合は、それに合わせて調整
            now = time.time()
            wait_time = reset_time - now
            
            if wait_time > 0:
                logger.info(f"レート制限リセット待機: {wait_time/60:.1f}分")
                # 実際の待機はスケジューラに任せる
        
        await self._save_state()
    
    async def _save_state(self):
        """状態を永続化"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            state = {
                "user_id": self.user_id,
                "timestamp": time.time(),
                "buckets_15min": {},
                "buckets_24hour": {},
                "request_history": {}
            }
            
            # トークンバケットの状態を保存
            for endpoint in RATE_LIMITS.keys():
                bucket_15min = self.buckets_15min[endpoint]
                bucket_24hour = self.buckets_24hour[endpoint]
                
                state["buckets_15min"][endpoint.value] = {
                    "capacity": bucket_15min.capacity,
                    "tokens": bucket_15min.tokens,
                    "last_refill": bucket_15min.last_refill,
                    "refill_rate": bucket_15min.refill_rate
                }
                
                state["buckets_24hour"][endpoint.value] = {
                    "capacity": bucket_24hour.capacity,
                    "tokens": bucket_24hour.tokens,
                    "last_refill": bucket_24hour.last_refill,
                    "refill_rate": bucket_24hour.refill_rate
                }
                
                state["request_history"][endpoint.value] = self.request_history[endpoint]
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"レート制限状態保存エラー: {e}")
    
    def _load_state(self):
        """保存された状態を読み込み"""
        try:
            if not os.path.exists(self.state_file):
                return
            
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 保存された状態を復元
            for endpoint_name, bucket_data in state.get("buckets_15min", {}).items():
                try:
                    endpoint = APIEndpoint(endpoint_name)
                    bucket = TokenBucket(**bucket_data)
                    self.buckets_15min[endpoint] = bucket
                except (ValueError, TypeError) as e:
                    logger.warning(f"15分バケット復元エラー {endpoint_name}: {e}")
            
            for endpoint_name, bucket_data in state.get("buckets_24hour", {}).items():
                try:
                    endpoint = APIEndpoint(endpoint_name)
                    bucket = TokenBucket(**bucket_data)
                    self.buckets_24hour[endpoint] = bucket
                except (ValueError, TypeError) as e:
                    logger.warning(f"24時間バケット復元エラー {endpoint_name}: {e}")
            
            for endpoint_name, history in state.get("request_history", {}).items():
                try:
                    endpoint = APIEndpoint(endpoint_name)
                    self.request_history[endpoint] = history
                except ValueError as e:
                    logger.warning(f"リクエスト履歴復元エラー {endpoint_name}: {e}")
            
            logger.info(f"レート制限状態復元完了: user={self.user_id}")
            
        except Exception as e:
            logger.error(f"レート制限状態読み込みエラー: {e}")


# =============================================================================
# レートリミッター管理クラス
# =============================================================================

class RateLimiterManager:
    """
    全ユーザーのレートリミッターを管理
    """
    
    def __init__(self):
        self.user_limiters: Dict[str, UserRateLimiter] = {}
        logger.info("RateLimiterManager初期化完了")
    
    def get_limiter(self, user_id: str) -> UserRateLimiter:
        """
        ユーザー用のレートリミッターを取得
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            UserRateLimiter: ユーザー専用レートリミッター
        """
        if user_id not in self.user_limiters:
            self.user_limiters[user_id] = UserRateLimiter(user_id)
        
        return self.user_limiters[user_id]
    
    def get_all_stats(self) -> Dict[str, Dict[str, any]]:
        """
        全ユーザーの使用量統計を取得
        
        Returns:
            Dict[str, Dict[str, any]]: ユーザー別統計
        """
        stats = {}
        for user_id, limiter in self.user_limiters.items():
            stats[user_id] = limiter.get_usage_stats()
        
        return stats


# グローバルインスタンス
rate_limiter_manager = RateLimiterManager()


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_rate_limiter():
        """レートリミッターのテスト"""
        # テスト用ユーザー
        test_user_id = "test_user"
        limiter = UserRateLimiter(test_user_id)
        
        print("=== レートリミッターテスト ===")
        
        # いいね制限テスト（15分で1回のみ）
        print("\n--- いいね制限テスト ---")
        for i in range(3):
            can_request, error = await limiter.can_make_request(APIEndpoint.LIKE)
            print(f"いいね {i+1}回目: {can_request}, エラー: {error}")
            
            if can_request:
                consumed = await limiter.consume_request(APIEndpoint.LIKE)
                print(f"  → 消費: {consumed}")
        
        # リツイート制限テスト（15分で50回）
        print("\n--- リツイート制限テスト ---")
        for i in range(3):
            can_request, error = await limiter.can_make_request(APIEndpoint.RETWEET)
            print(f"リツイート {i+1}回目: {can_request}, エラー: {error}")
            
            if can_request:
                consumed = await limiter.consume_request(APIEndpoint.RETWEET)
                print(f"  → 消費: {consumed}")
        
        # 使用量統計表示
        print("\n--- 使用量統計 ---")
        stats = limiter.get_usage_stats()
        for endpoint, stat in stats.items():
            print(f"{endpoint}:")
            print(f"  15分: {stat['15min_used']}/{stat['15min_limit']} (残り: {stat['15min_remaining']})")
            print(f"  24時間: {stat['24hour_used']}/{stat['24hour_limit']} (残り: {stat['24hour_remaining']})")
            print(f"  次回利用可能: {stat['next_available_seconds']:.1f}秒後")
    
    # テスト実行
    asyncio.run(test_rate_limiter())