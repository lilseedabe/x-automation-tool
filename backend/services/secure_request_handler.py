"""
セキュアリクエストハンドラー

ユーザーのAPIキーを一時的に受け取り、処理後は即座に削除
サーバーには一切保存しない、プライバシー重視の設計
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
import json
import logging
from contextlib import asynccontextmanager

from backend.core.twitter_client import TwitterClient
from backend.ai.post_analyzer import PostAnalyzer
from backend.core.rate_limiter import UserRateLimiter

logger = logging.getLogger(__name__)

class SecureRequestHandler:
    """
    セキュアリクエストハンドラー
    
    ユーザーのAPIキーを一時的にメモリで保持し、
    処理完了後は即座に削除してプライバシーを保護
    """
    
    def __init__(self):
        """初期化"""
        # アクティブなセッション管理（メモリ内のみ）
        self.active_sessions = {}
        
        logger.info("SecureRequestHandler初期化完了（メモリベース・非永続化）")
    
    @asynccontextmanager
    async def secure_session(self, session_id: str, api_keys: Dict[str, str]):
        """
        セキュアセッション管理
        
        Args:
            session_id (str): セッションID
            api_keys (Dict[str, str]): APIキー（一時的）
            
        Yields:
            TwitterClient: 一時的に作成されたクライアント
        """
        twitter_client = None
        
        try:
            # セッション開始ログ
            logger.info(f"セキュアセッション開始: {session_id}")
            
            # APIキーの検証
            if not self._validate_api_keys(api_keys):
                raise ValueError("無効なAPIキーです")
            
            # TwitterClientを一時的に作成
            twitter_client = TwitterClient(session_id, api_keys)
            
            # アクティブセッションに追加（メモリ内のみ）
            self.active_sessions[session_id] = {
                'start_time': time.time(),
                'client': twitter_client,
                'status': 'active'
            }
            
            yield twitter_client
            
        except Exception as e:
            logger.error(f"セキュアセッションエラー: {e}")
            raise
            
        finally:
            # セッション終了処理
            try:
                # メモリからAPIキーを完全削除
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                # TwitterClientのAPIキーも削除
                if twitter_client:
                    del twitter_client
                
                # Pythonガベージコレクションを強制実行
                import gc
                gc.collect()
                
                logger.info(f"セキュアセッション終了・データ削除完了: {session_id}")
                
            except Exception as cleanup_error:
                logger.error(f"セッションクリーンアップエラー: {cleanup_error}")
    
    async def handle_engagement_analysis(self, session_id: str, api_keys: Dict[str, str], 
                                       tweet_url: str) -> Dict[str, Any]:
        """
        エンゲージメント分析リクエストをセキュアに処理
        
        Args:
            session_id (str): セッションID
            api_keys (Dict[str, str]): APIキー（一時的）
            tweet_url (str): 分析対象ツイートURL
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        async with self.secure_session(session_id, api_keys) as twitter_client:
            try:
                # ツイートIDを抽出
                tweet_id = self._extract_tweet_id(tweet_url)
                if not tweet_id:
                    return {"error": "無効なツイートURLです"}
                
                # エンゲージユーザーを取得
                engaging_users = await twitter_client.get_engaging_users(tweet_id, max_users=20)
                
                if not engaging_users:
                    return {"error": "エンゲージユーザーが見つかりません"}
                
                # AI分析を実行
                post_analyzer = PostAnalyzer()
                analysis_results = []
                
                for user in engaging_users[:10]:  # 最大10人まで
                    try:
                        # ユーザーの最新ツイート取得
                        recent_tweets = await twitter_client.get_user_recent_tweets(user.id, max_results=1)
                        
                        if recent_tweets:
                            latest_tweet = recent_tweets[0]
                            
                            # AI分析実行
                            analysis = await post_analyzer.analyze_for_like_and_retweet(
                                latest_tweet.text, 
                                latest_tweet.public_metrics
                            )
                            
                            analysis_results.append({
                                "user": {
                                    "id": user.id,
                                    "username": user.username,
                                    "name": user.name,
                                    "followers_count": user.public_metrics.get("followers_count", 0)
                                },
                                "tweet": {
                                    "id": latest_tweet.id,
                                    "text": latest_tweet.text,
                                    "created_at": latest_tweet.created_at,
                                    "metrics": latest_tweet.public_metrics
                                },
                                "analysis": analysis
                            })
                            
                        # レート制限を考慮した待機
                        await asyncio.sleep(0.5)
                        
                    except Exception as user_error:
                        logger.warning(f"ユーザー分析エラー {user.id}: {user_error}")
                        continue
                
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "total_engaging_users": len(engaging_users),
                    "analyzed_users": len(analysis_results),
                    "analysis_results": analysis_results,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"エンゲージメント分析エラー: {e}")
                return {"error": f"分析エラー: {str(e)}"}
    
    async def handle_action_execution(self, session_id: str, api_keys: Dict[str, str],
                                    actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        アクション実行リクエストをセキュアに処理
        
        Args:
            session_id (str): セッションID
            api_keys (Dict[str, str]): APIキー（一時的）
            actions (List[Dict[str, Any]]): 実行するアクションリスト
            
        Returns:
            Dict[str, Any]: 実行結果
        """
        async with self.secure_session(session_id, api_keys) as twitter_client:
            try:
                results = []
                successful_actions = 0
                
                for action in actions:
                    try:
                        action_type = action.get("action_type")
                        tweet_id = action.get("tweet_id")
                        
                        if not tweet_id or not action_type:
                            results.append({
                                "action": action,
                                "success": False,
                                "error": "無効なアクション情報"
                            })
                            continue
                        
                        # アクション実行
                        if action_type == "like":
                            result = await twitter_client.like_tweet(tweet_id, safety_check=True)
                        elif action_type == "retweet":
                            result = await twitter_client.retweet(tweet_id, safety_check=True)
                        else:
                            result = {"error": f"未対応のアクション: {action_type}"}
                        
                        if result.get("success"):
                            successful_actions += 1
                        
                        results.append({
                            "action": action,
                            "result": result
                        })
                        
                        # 人間らしい遅延
                        await asyncio.sleep(2)
                        
                    except Exception as action_error:
                        logger.error(f"個別アクションエラー: {action_error}")
                        results.append({
                            "action": action,
                            "success": False,
                            "error": str(action_error)
                        })
                
                return {
                    "success": True,
                    "total_attempted": len(actions),
                    "successful_actions": successful_actions,
                    "results": results,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"アクション実行エラー: {e}")
                return {"error": f"実行エラー: {str(e)}"}
    
    async def handle_api_test(self, session_id: str, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """
        API接続テストをセキュアに処理
        
        Args:
            session_id (str): セッションID
            api_keys (Dict[str, str]): APIキー（一時的）
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        async with self.secure_session(session_id, api_keys) as twitter_client:
            try:
                # 認証情報検証
                verification_result = await twitter_client.verify_credentials()
                
                if verification_result.get("success"):
                    return {
                        "success": True,
                        "message": "X API接続テスト成功",
                        "user_info": verification_result.get("user"),
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "success": False,
                        "error": verification_result.get("error", "接続テスト失敗")
                    }
                    
            except Exception as e:
                logger.error(f"API接続テストエラー: {e}")
                return {
                    "success": False,
                    "error": f"接続テストエラー: {str(e)}"
                }
    
    def _validate_api_keys(self, api_keys: Dict[str, str]) -> bool:
        """
        APIキーの基本検証
        
        Args:
            api_keys (Dict[str, str]): APIキー
            
        Returns:
            bool: 有効フラグ
        """
        required_keys = ["api_key", "api_secret", "access_token", "access_token_secret"]
        
        for key in required_keys:
            if not api_keys.get(key) or len(api_keys[key].strip()) < 10:
                logger.warning(f"無効なAPIキー: {key}")
                return False
        
        return True
    
    def _extract_tweet_id(self, tweet_url: str) -> Optional[str]:
        """
        ツイートURLからIDを抽出
        
        Args:
            tweet_url (str): ツイートURL
            
        Returns:
            Optional[str]: ツイートID
        """
        try:
            if "/status/" in tweet_url:
                parts = tweet_url.split("/status/")
                if len(parts) >= 2:
                    tweet_id = parts[1].split("?")[0].split("/")[0]
                    return tweet_id
            return None
        except Exception as e:
            logger.error(f"ツイートID抽出エラー: {e}")
            return None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        セッション統計を取得
        
        Returns:
            Dict[str, Any]: セッション統計
        """
        active_count = len(self.active_sessions)
        
        return {
            "active_sessions": active_count,
            "memory_only_storage": True,
            "persistent_storage": False,
            "privacy_level": "maximum",
            "data_retention": "session_only"
        }


# グローバルインスタンス
secure_handler = SecureRequestHandler()

# エクスポート用関数
async def handle_secure_request(request_type: str, session_id: str, 
                               api_keys: Dict[str, str], **kwargs) -> Dict[str, Any]:
    """
    セキュアリクエストのメインハンドラー
    
    Args:
        request_type (str): リクエストタイプ
        session_id (str): セッションID
        api_keys (Dict[str, str]): APIキー（一時的）
        **kwargs: 追加パラメータ
        
    Returns:
        Dict[str, Any]: 処理結果
    """
    try:
        if request_type == "engagement_analysis":
            return await secure_handler.handle_engagement_analysis(
                session_id, api_keys, kwargs.get("tweet_url")
            )
        elif request_type == "action_execution":
            return await secure_handler.handle_action_execution(
                session_id, api_keys, kwargs.get("actions", [])
            )
        elif request_type == "api_test":
            return await secure_handler.handle_api_test(session_id, api_keys)
        else:
            return {"error": f"未対応のリクエストタイプ: {request_type}"}
            
    except Exception as e:
        logger.error(f"セキュアリクエスト処理エラー: {e}")
        return {"error": f"リクエスト処理エラー: {str(e)}"}


if __name__ == "__main__":
    import asyncio
    
    async def test_secure_handler():
        """セキュアハンドラーのテスト"""
        print("=== セキュアリクエストハンドラーテスト ===")
        
        # セッション統計確認
        stats = secure_handler.get_session_stats()
        print(f"セッション統計: {stats}")
        
        # テスト用APIキー（ダミー）
        test_api_keys = {
            "api_key": "test_api_key_12345",
            "api_secret": "test_api_secret_67890",
            "access_token": "test_access_token_12345",
            "access_token_secret": "test_access_token_secret_67890"
        }
        
        # API接続テスト
        test_result = await handle_secure_request(
            "api_test", 
            "test_session_123", 
            test_api_keys
        )
        print(f"API接続テスト結果: {test_result}")
    
    # テスト実行
    asyncio.run(test_secure_handler())