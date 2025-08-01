"""
🧠 X自動反応ツール - AI投稿・ユーザー分析エンジン
ユーザーのエンゲージメント品質とポテンシャルを AI 分析
"""

import logging
import re
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class PostAnalyzer:
    """AI投稿・ユーザー分析クラス"""
    
    def __init__(self):
        """AI分析エンジン初期化"""
        self.spam_keywords = [
            "無料", "即金", "簡単", "副業", "在宅", "投資", "儲かる", "稼げる",
            "限定", "今だけ", "急いで", "フォロバ", "相互フォロー", "RT希望",
            "拡散希望", "いいね返し", "spam", "bot", "fake"
        ]
        
        self.quality_keywords = [
            "ありがとう", "素晴らしい", "勉強になる", "参考になる", "感謝",
            "学び", "成長", "挑戦", "努力", "継続", "目標", "達成",
            "技術", "開発", "プログラミング", "デザイン", "マーケティング"
        ]
        
        logger.info("🧠 AI分析エンジン初期化完了")
    
    async def analyze_user_engagement_quality(
        self, 
        user_data: Dict[str, Any], 
        recent_tweets: List[Dict[str, Any]], 
        original_tweet: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ユーザーのエンゲージメント品質を AI 分析
        
        Args:
            user_data: ユーザー基本情報
            recent_tweets: ユーザーの最近のツイート
            original_tweet: 元のツイート（反応されたツイート）
            
        Returns:
            AI分析結果
        """
        try:
            logger.debug(f"🔍 ユーザー分析開始: @{user_data.get('username', 'unknown')}")
            
            # 各種スコアを計算
            profile_score = self._analyze_profile_quality(user_data)
            activity_score = self._analyze_activity_quality(recent_tweets)
            engagement_score = self._analyze_engagement_authenticity(user_data, original_tweet)
            content_score = self._analyze_content_quality(recent_tweets)
            
            # 総合スコア計算（重み付け平均）
            weights = {
                "profile": 0.25,
                "activity": 0.20,
                "engagement": 0.30,
                "content": 0.25
            }
            
            final_score = (
                profile_score * weights["profile"] +
                activity_score * weights["activity"] +
                engagement_score * weights["engagement"] +
                content_score * weights["content"]
            )
            
            # スコアを0-1の範囲に正規化
            final_score = max(0, min(1, final_score))
            
            # 品質カテゴリを決定
            quality_category = self._determine_quality_category(final_score)
            
            # エンゲージメント推奨度を計算
            engagement_recommendation = self._calculate_engagement_recommendation(
                final_score, user_data, recent_tweets
            )
            
            analysis_result = {
                "engagement_score": round(final_score, 3),
                "quality_category": quality_category,
                "score_breakdown": {
                    "profile_score": round(profile_score, 3),
                    "activity_score": round(activity_score, 3),
                    "engagement_score": round(engagement_score, 3),
                    "content_score": round(content_score, 3)
                },
                "engagement_recommendation": engagement_recommendation,
                "analysis_details": {
                    "follower_ratio": self._calculate_follower_ratio(user_data),
                    "activity_level": self._assess_activity_level(recent_tweets),
                    "content_diversity": self._assess_content_diversity(recent_tweets),
                    "spam_indicators": self._detect_spam_indicators(user_data, recent_tweets)
                },
                "analyzed_at": datetime.now(timezone.utc)
            }
            
            logger.debug(f"✅ ユーザー分析完了: @{user_data.get('username')} スコア={final_score:.3f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ ユーザー分析エラー: {str(e)}")
            # デフォルトの低スコアを返す
            return {
                "engagement_score": 0.1,
                "quality_category": "very_low",
                "score_breakdown": {
                    "profile_score": 0.1,
                    "activity_score": 0.1,
                    "engagement_score": 0.1,
                    "content_score": 0.1
                },
                "engagement_recommendation": "avoid",
                "analysis_details": {"error": str(e)},
                "analyzed_at": datetime.now(timezone.utc)
            }
    
    def _analyze_profile_quality(self, user_data: Dict[str, Any]) -> float:
        """プロフィール品質を分析"""
        score = 0.5  # ベーススコア
        
        try:
            # フォロワー数分析
            followers = user_data["public_metrics"]["followers_count"]
            following = user_data["public_metrics"]["following_count"]
            
            # フォロワー数による加点
            if followers > 1000:
                score += 0.2
            elif followers > 100:
                score += 0.1
            elif followers < 10:
                score -= 0.2
            
            # フォロー比率分析
            if following > 0:
                ratio = followers / following
                if 0.5 <= ratio <= 2.0:
                    score += 0.1
                elif ratio < 0.1 or ratio > 10:
                    score -= 0.2
            
            # 認証バッジ
            if user_data.get("verified"):
                score += 0.2
            
            # プロフィール記述
            bio = user_data.get("description", "")
            if bio:
                score += 0.1
                # スパムキーワードチェック
                if any(keyword in bio.lower() for keyword in self.spam_keywords):
                    score -= 0.3
                # 品質キーワードチェック
                if any(keyword in bio.lower() for keyword in self.quality_keywords):
                    score += 0.1
            
        except Exception as e:
            logger.warning(f"⚠️ プロフィール分析エラー: {str(e)}")
        
        return max(0, min(1, score))
    
    def _analyze_activity_quality(self, recent_tweets: List[Dict[str, Any]]) -> float:
        """アクティビティ品質を分析"""
        score = 0.5  # ベーススコア
        
        try:
            if not recent_tweets:
                return 0.2  # ツイートがない場合は低スコア
            
            # ツイート数による評価
            tweet_count = len(recent_tweets)
            if 2 <= tweet_count <= 10:
                score += 0.2
            elif tweet_count > 15:
                score -= 0.1  # 過度な投稿は減点
            
            # エンゲージメント率分析
            total_likes = sum(tweet.get("public_metrics", {}).get("like_count", 0) for tweet in recent_tweets)
            total_retweets = sum(tweet.get("public_metrics", {}).get("retweet_count", 0) for tweet in recent_tweets)
            
            avg_engagement = (total_likes + total_retweets) / tweet_count if tweet_count > 0 else 0
            
            if avg_engagement > 50:
                score += 0.3
            elif avg_engagement > 10:
                score += 0.2
            elif avg_engagement > 1:
                score += 0.1
            
        except Exception as e:
            logger.warning(f"⚠️ アクティビティ分析エラー: {str(e)}")
        
        return max(0, min(1, score))
    
    def _analyze_engagement_authenticity(self, user_data: Dict[str, Any], original_tweet: Dict[str, Any]) -> float:
        """エンゲージメントの真正性を分析"""
        score = 0.6  # ベーススコア
        
        try:
            # エンゲージメントタイプによる評価
            engagement_type = user_data.get("engagement_type", "")
            
            if engagement_type == "like":
                score += 0.1  # いいねは一般的
            elif engagement_type == "retweet":
                score += 0.2  # リツイートはより価値が高い
            elif engagement_type == "reply":
                score += 0.3  # リプライは最も価値が高い
            
            # エンゲージメントタイミング分析
            engagement_time = user_data.get("engagement_time")
            if engagement_time:
                # 即座の反応は真正性が高い
                score += 0.1
            
            # ユーザーのフォロワー数とエンゲージメントの関係
            followers = user_data["public_metrics"]["followers_count"]
            if 100 <= followers <= 10000:
                score += 0.1  # 中規模ユーザーは価値が高い
            elif followers > 100000:
                score -= 0.1  # 大規模アカウントは影響力があるが個人的関係は薄い
            
        except Exception as e:
            logger.warning(f"⚠️ エンゲージメント真正性分析エラー: {str(e)}")
        
        return max(0, min(1, score))
    
    def _analyze_content_quality(self, recent_tweets: List[Dict[str, Any]]) -> float:
        """コンテンツ品質を分析"""
        score = 0.5  # ベーススコア
        
        try:
            if not recent_tweets:
                return 0.2
            
            quality_count = 0
            spam_count = 0
            
            for tweet in recent_tweets:
                text = tweet.get("text", "").lower()
                
                # 品質コンテンツの検出
                if any(keyword in text for keyword in self.quality_keywords):
                    quality_count += 1
                
                # スパムコンテンツの検出
                if any(keyword in text for keyword in self.spam_keywords):
                    spam_count += 1
                
                # URL過多チェック
                if text.count("http") > 2:
                    spam_count += 1
                
                # ハッシュタグ過多チェック
                if text.count("#") > 5:
                    spam_count += 1
                
                # 同じ内容の繰り返しチェック
                # (簡略化実装)
            
            # スコア調整
            if quality_count > 0:
                score += min(0.3, quality_count * 0.1)
            
            if spam_count > 0:
                score -= min(0.4, spam_count * 0.1)
            
            # 多様性ボーナス
            unique_words = set()
            for tweet in recent_tweets:
                words = tweet.get("text", "").split()
                unique_words.update(words)
            
            if len(unique_words) > 50:
                score += 0.1
            
        except Exception as e:
            logger.warning(f"⚠️ コンテンツ品質分析エラー: {str(e)}")
        
        return max(0, min(1, score))
    
    def _determine_quality_category(self, score: float) -> str:
        """スコアから品質カテゴリを決定"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        elif score >= 0.2:
            return "poor"
        else:
            return "very_poor"
    
    def _calculate_engagement_recommendation(
        self, 
        score: float, 
        user_data: Dict[str, Any], 
        recent_tweets: List[Dict[str, Any]]
    ) -> str:
        """エンゲージメント推奨度を計算"""
        if score >= 0.7:
            return "highly_recommended"
        elif score >= 0.5:
            return "recommended"
        elif score >= 0.3:
            return "conditional"
        else:
            return "avoid"
    
    def _calculate_follower_ratio(self, user_data: Dict[str, Any]) -> float:
        """フォロワー比率を計算"""
        try:
            followers = user_data["public_metrics"]["followers_count"]
            following = user_data["public_metrics"]["following_count"]
            return followers / following if following > 0 else float('inf')
        except:
            return 0
    
    def _assess_activity_level(self, recent_tweets: List[Dict[str, Any]]) -> str:
        """アクティビティレベルを評価"""
        tweet_count = len(recent_tweets)
        if tweet_count >= 10:
            return "very_active"
        elif tweet_count >= 5:
            return "active"
        elif tweet_count >= 2:
            return "moderate"
        elif tweet_count >= 1:
            return "low"
        else:
            return "inactive"
    
    def _assess_content_diversity(self, recent_tweets: List[Dict[str, Any]]) -> str:
        """コンテンツ多様性を評価"""
        if not recent_tweets:
            return "none"
        
        # 簡略化実装: 異なる単語数をカウント
        all_words = set()
        for tweet in recent_tweets:
            words = tweet.get("text", "").split()
            all_words.update(words)
        
        unique_ratio = len(all_words) / (len(recent_tweets) * 10) if recent_tweets else 0
        
        if unique_ratio >= 0.8:
            return "very_diverse"
        elif unique_ratio >= 0.6:
            return "diverse"
        elif unique_ratio >= 0.4:
            return "moderate"
        elif unique_ratio >= 0.2:
            return "limited"
        else:
            return "repetitive"
    
    def _detect_spam_indicators(self, user_data: Dict[str, Any], recent_tweets: List[Dict[str, Any]]) -> List[str]:
        """スパム指標を検出"""
        indicators = []
        
        try:
            # プロフィールスパムチェック
            bio = user_data.get("description", "").lower()
            if any(keyword in bio for keyword in self.spam_keywords):
                indicators.append("spam_keywords_in_bio")
            
            # フォロー比率異常
            followers = user_data["public_metrics"]["followers_count"]
            following = user_data["public_metrics"]["following_count"]
            
            if following > followers * 10 and followers < 100:
                indicators.append("suspicious_follow_ratio")
            
            # ツイートスパムチェック
            for tweet in recent_tweets:
                text = tweet.get("text", "").lower()
                if any(keyword in text for keyword in self.spam_keywords):
                    indicators.append("spam_keywords_in_tweets")
                    break
            
            # URL過多
            url_count = sum(tweet.get("text", "").count("http") for tweet in recent_tweets)
            if url_count > len(recent_tweets) * 2:
                indicators.append("excessive_urls")
            
        except Exception as e:
            logger.warning(f"⚠️ スパム検出エラー: {str(e)}")
        
        return indicators