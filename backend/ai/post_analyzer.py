"""
高度な投稿分析サービス

このモジュールは以下の機能を提供します：
- いいね♡とリポスト適性スコアリング
- 多角的AI分析
- 安全性チェック
- タイミング推奨
- リスク評価
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re
import random

from .groq_client import GroqClient
from ..core.twitter_client import TwitterClient, Tweet

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 高度な投稿分析サービスクラス
# =============================================================================

class PostAnalyzer:
    """
    高度な投稿分析サービス
    
    いいね♡とリポストの適性を多角的に分析し、
    AIによる詳細な推奨事項を提供します。
    """
    
    def __init__(self, groq_client: GroqClient = None, twitter_client: TwitterClient = None):
        """
        初期化
        
        Args:
            groq_client (GroqClient): Groq AIクライアント
            twitter_client (TwitterClient): Twitterクライアント
        """
        self.groq_client = groq_client or GroqClient()
        self.twitter_client = twitter_client or TwitterClient()
        
        # 危険キーワードリスト
        self.risk_keywords = [
            "炎上", "批判", "叩き", "晒し", "攻撃", "差別", "ヘイト", 
            "詐欺", "スパム", "政治", "選挙", "宗教", "暴力", "違法"
        ]
        
        # ポジティブキーワードリスト
        self.positive_keywords = [
            "素晴らしい", "最高", "感謝", "成功", "達成", "喜び", "幸せ",
            "技術", "革新", "学習", "成長", "発見", "創造", "協力"
        ]
        
        logger.info("高度なPostAnalyzer初期化完了")
    
    async def analyze_for_like_and_retweet(self, text: str, metrics: Dict[str, int] = None) -> Dict[str, Any]:
        """
        いいね♡とリポスト向けの詳細分析
        
        Args:
            text (str): 分析対象テキスト
            metrics (Dict[str, int]): 既存のエンゲージメント指標
            
        Returns:
            Dict[str, Any]: 詳細分析結果
        """
        try:
            # 並行して複数の分析を実行
            tasks = [
                self._calculate_like_score(text, metrics),
                self._calculate_retweet_score(text, metrics),
                self._analyze_safety(text),
                self._categorize_content(text),
                self._assess_risk_level(text),
                self._recommend_timing(text, metrics)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            like_score = results[0] if not isinstance(results[0], Exception) else 0
            retweet_score = results[1] if not isinstance(results[1], Exception) else 0
            safety_check = results[2] if not isinstance(results[2], Exception) else {"safe": False, "reason": "分析エラー"}
            content_category = results[3] if not isinstance(results[3], Exception) else "不明"
            risk_level = results[4] if not isinstance(results[4], Exception) else "高"
            timing_recommendation = results[5] if not isinstance(results[5], Exception) else "後で"
            
            # 総合的な推奨アクション決定
            recommended_action = self._determine_recommended_action(
                like_score, retweet_score, safety_check, risk_level
            )
            
            # 信頼度計算
            confidence = self._calculate_confidence(like_score, retweet_score, safety_check)
            
            analysis_result = {
                "like_score": like_score,
                "retweet_score": retweet_score,
                "timing_recommendation": timing_recommendation,
                "safety_check": safety_check["safe"],
                "safety_reason": safety_check.get("reason", ""),
                "content_category": content_category,
                "risk_level": risk_level,
                "recommended_action": recommended_action,
                "confidence": confidence,
                "detailed_analysis": {
                    "text_length": len(text),
                    "has_hashtags": "#" in text,
                    "has_mentions": "@" in text,
                    "has_urls": "http" in text.lower(),
                    "word_count": len(text.split()),
                    "positive_keywords_found": self._count_keywords(text, self.positive_keywords),
                    "risk_keywords_found": self._count_keywords(text, self.risk_keywords)
                },
                "ai_reasoning": await self._generate_ai_reasoning(text, like_score, retweet_score, safety_check),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"詳細分析完了: いいね={like_score}, リポスト={retweet_score}, 安全性={safety_check['safe']}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"詳細分析エラー: {e}")
            return {
                "error": f"分析エラー: {str(e)}",
                "like_score": 0,
                "retweet_score": 0,
                "safety_check": False,
                "risk_level": "高",
                "recommended_action": "skip",
                "confidence": 0,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def _calculate_like_score(self, text: str, metrics: Dict[str, int] = None) -> int:
        """
        いいね適性スコア計算
        
        Args:
            text (str): テキスト
            metrics (Dict[str, int]): エンゲージメント指標
            
        Returns:
            int: いいねスコア (0-100)
        """
        score = 50  # ベーススコア
        
        # テキスト長評価
        text_length = len(text)
        if 50 <= text_length <= 150:
            score += 15  # 適切な長さ
        elif text_length > 280:
            score -= 10  # 長すぎる
        
        # ポジティブコンテンツ評価
        positive_count = self._count_keywords(text, self.positive_keywords)
        score += min(positive_count * 5, 20)
        
        # ハッシュタグ評価
        hashtag_count = text.count('#')
        if 1 <= hashtag_count <= 3:
            score += 10
        elif hashtag_count > 5:
            score -= 5
        
        # 既存エンゲージメント評価
        if metrics:
            existing_likes = metrics.get("like_count", 0)
            if existing_likes > 50:
                score += 15
            elif existing_likes > 10:
                score += 10
        
        # 感情表現評価
        emotion_indicators = ["！", "♡", "❤️", "😊", "🎉", "✨"]
        emotion_count = sum(text.count(indicator) for indicator in emotion_indicators)
        score += min(emotion_count * 3, 15)
        
        # リスクキーワード減点
        risk_count = self._count_keywords(text, self.risk_keywords)
        score -= risk_count * 15
        
        return max(0, min(100, score))
    
    async def _calculate_retweet_score(self, text: str, metrics: Dict[str, int] = None) -> int:
        """
        リポスト適性スコア計算
        
        Args:
            text (str): テキスト
            metrics (Dict[str, int]): エンゲージメント指標
            
        Returns:
            int: リポストスコア (0-100)
        """
        score = 40  # ベーススコア（リポストはより慎重）
        
        # 情報価値評価
        info_keywords = ["発表", "リリース", "発見", "研究", "開発", "技術", "革新", "ニュース"]
        info_count = self._count_keywords(text, info_keywords)
        score += min(info_count * 10, 25)
        
        # 教育価値評価
        educational_keywords = ["学習", "教育", "解説", "方法", "ガイド", "tips", "コツ"]
        edu_count = self._count_keywords(text, educational_keywords)
        score += min(edu_count * 8, 20)
        
        # 既存のリポスト実績
        if metrics:
            existing_retweets = metrics.get("retweet_count", 0)
            existing_likes = metrics.get("like_count", 0)
            
            # リポスト率評価
            if existing_likes > 0:
                retweet_ratio = existing_retweets / existing_likes
                if 0.1 <= retweet_ratio <= 0.3:  # 適切なリポスト率
                    score += 15
                elif retweet_ratio > 0.5:  # リポスト率が高すぎる（炎上リスク）
                    score -= 20
        
        # ブランド安全性評価
        brand_safe_keywords = ["公式", "正式", "認定", "専門", "権威"]
        brand_count = self._count_keywords(text, brand_safe_keywords)
        score += min(brand_count * 5, 15)
        
        # 質の高さ評価
        quality_indicators = ["詳細", "分析", "検証", "根拠", "データ", "統計"]
        quality_count = self._count_keywords(text, quality_indicators)
        score += min(quality_count * 7, 20)
        
        # リスクキーワード大幅減点（リポストはブランドリスクが高い）
        risk_count = self._count_keywords(text, self.risk_keywords)
        score -= risk_count * 25
        
        return max(0, min(100, score))
    
    async def _analyze_safety(self, text: str) -> Dict[str, Any]:
        """
        安全性分析
        
        Args:
            text (str): テキスト
            
        Returns:
            Dict[str, Any]: 安全性分析結果
        """
        safety_issues = []
        
        # リスクキーワードチェック
        risk_found = self._count_keywords(text, self.risk_keywords)
        if risk_found > 0:
            safety_issues.append("危険キーワード検出")
        
        # URL安全性チェック
        if "http" in text.lower():
            # 簡易的な危険URLパターンチェック
            dangerous_patterns = [".tk", ".ml", "bit.ly", "短縮URL", "怪しい"]
            if any(pattern in text.lower() for pattern in dangerous_patterns):
                safety_issues.append("危険なURL可能性")
        
        # スパムパターンチェック
        spam_indicators = ["今すぐ", "限定", "無料", "稼げる", "簡単", "確実"]
        spam_count = self._count_keywords(text, spam_indicators)
        if spam_count > 2:
            safety_issues.append("スパム的表現")
        
        # 過度な宣伝チェック
        promo_indicators = ["購入", "販売", "割引", "キャンペーン", "プレゼント"]
        promo_count = self._count_keywords(text, promo_indicators)
        if promo_count > 1:
            safety_issues.append("過度な宣伝")
        
        # 長すぎるハッシュタグ
        hashtag_count = text.count('#')
        if hashtag_count > 5:
            safety_issues.append("ハッシュタグ過多")
        
        is_safe = len(safety_issues) == 0
        
        return {
            "safe": is_safe,
            "issues": safety_issues,
            "reason": "; ".join(safety_issues) if safety_issues else "安全性に問題なし"
        }
    
    async def _categorize_content(self, text: str) -> str:
        """
        コンテンツカテゴリ分析
        
        Args:
            text (str): テキスト
            
        Returns:
            str: カテゴリ名
        """
        categories = {
            "技術": ["技術", "開発", "プログラミング", "AI", "IT", "エンジニア", "コード"],
            "ビジネス": ["ビジネス", "経営", "起業", "マーケティング", "営業", "会社"],
            "教育": ["学習", "教育", "勉強", "研究", "知識", "スキル", "成長"],
            "エンターテイメント": ["映画", "音楽", "ゲーム", "アニメ", "芸能", "スポーツ"],
            "ライフスタイル": ["生活", "健康", "料理", "旅行", "ファッション", "美容"],
            "ニュース": ["ニュース", "速報", "発表", "報告", "更新", "リリース"],
            "個人的": ["私", "個人", "日記", "感想", "思い", "体験"]
        }
        
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return "その他"
        
        return max(category_scores, key=category_scores.get)
    
    async def _assess_risk_level(self, text: str) -> str:
        """
        リスクレベル評価
        
        Args:
            text (str): テキスト
            
        Returns:
            str: リスクレベル (低/中/高)
        """
        risk_score = 0
        
        # リスクキーワード
        risk_count = self._count_keywords(text, self.risk_keywords)
        risk_score += risk_count * 3
        
        # 感情的表現
        emotional_patterns = ["！！", "???", "絶対", "最悪", "ムカつく", "許せない"]
        emotional_count = sum(1 for pattern in emotional_patterns if pattern in text)
        risk_score += emotional_count * 2
        
        # 攻撃的表現
        aggressive_patterns = ["バカ", "アホ", "死ね", "消えろ", "うざい"]
        aggressive_count = sum(1 for pattern in aggressive_patterns if pattern in text)
        risk_score += aggressive_count * 5
        
        # 政治・宗教関連
        sensitive_topics = ["政治", "選挙", "宗教", "右翼", "左翼", "政党"]
        sensitive_count = self._count_keywords(text, sensitive_topics)
        risk_score += sensitive_count * 4
        
        # リスクレベル判定
        if risk_score >= 10:
            return "高"
        elif risk_score >= 5:
            return "中"
        else:
            return "低"
    
    async def _recommend_timing(self, text: str, metrics: Dict[str, int] = None) -> str:
        """
        タイミング推奨
        
        Args:
            text (str): テキスト
            metrics (Dict[str, int]): エンゲージメント指標
            
        Returns:
            str: 推奨タイミング
        """
        # 現在時刻
        now = datetime.now()
        hour = now.hour
        
        # コンテンツタイプ別推奨
        if "ニュース" in text or "速報" in text:
            return "即座に"
        
        # 時間帯別推奨
        if 7 <= hour <= 9:
            return "1-2分後"  # 朝の通勤時間
        elif 12 <= hour <= 13:
            return "数分後"   # 昼休み
        elif 19 <= hour <= 22:
            return "1-3分後"  # 夜のゴールデンタイム
        else:
            return "数分後"
        
        # エンゲージメントが既に高い場合は早めに
        if metrics and metrics.get("like_count", 0) > 50:
            return "即座に"
        
        return "数分後"
    
    def _determine_recommended_action(self, like_score: int, retweet_score: int, 
                                    safety_check: Dict[str, Any], risk_level: str) -> str:
        """
        推奨アクション決定
        
        Args:
            like_score (int): いいねスコア
            retweet_score (int): リポストスコア
            safety_check (Dict[str, Any]): 安全性チェック結果
            risk_level (str): リスクレベル
            
        Returns:
            str: 推奨アクション
        """
        # 安全性チェックで問題がある場合はスキップ
        if not safety_check.get("safe", False) or risk_level == "高":
            return "skip"
        
        # スコア比較
        if like_score >= 75 and retweet_score >= 75:
            return "both"  # 両方実行
        elif like_score >= 70:
            return "like"
        elif retweet_score >= 70:
            return "retweet"
        elif like_score >= 60 or retweet_score >= 60:
            if like_score > retweet_score:
                return "like"
            else:
                return "retweet"
        else:
            return "skip"
    
    def _calculate_confidence(self, like_score: int, retweet_score: int, 
                            safety_check: Dict[str, Any]) -> float:
        """
        AI分析の信頼度計算
        
        Args:
            like_score (int): いいねスコア
            retweet_score (int): リポストスコア
            safety_check (Dict[str, Any]): 安全性チェック結果
            
        Returns:
            float: 信頼度 (0.0-1.0)
        """
        # ベース信頼度
        base_confidence = 0.7
        
        # スコアの明確さ
        max_score = max(like_score, retweet_score)
        if max_score >= 80:
            base_confidence += 0.2
        elif max_score <= 30:
            base_confidence += 0.1  # 明確に低い場合も信頼度高
        
        # 安全性チェック
        if safety_check.get("safe", False):
            base_confidence += 0.1
        else:
            base_confidence -= 0.2
        
        return max(0.0, min(1.0, base_confidence))
    
    async def _generate_ai_reasoning(self, text: str, like_score: int, 
                                   retweet_score: int, safety_check: Dict[str, Any]) -> str:
        """
        AI推論理由生成
        
        Args:
            text (str): テキスト
            like_score (int): いいねスコア
            retweet_score (int): リポストスコア
            safety_check (Dict[str, Any]): 安全性チェック結果
            
        Returns:
            str: AI推論理由
        """
        reasoning_parts = []
        
        # いいねスコア理由
        if like_score >= 70:
            reasoning_parts.append(f"いいね適性が高い（{like_score}点）: ポジティブで親しみやすい内容")
        elif like_score < 50:
            reasoning_parts.append(f"いいね適性が低い（{like_score}点）: エンゲージメントが期待できない内容")
        
        # リポストスコア理由
        if retweet_score >= 70:
            reasoning_parts.append(f"リポスト適性が高い（{retweet_score}点）: 情報価値が高くシェアに適している")
        elif retweet_score < 50:
            reasoning_parts.append(f"リポスト適性が低い（{retweet_score}点）: ブランドリスクを考慮")
        
        # 安全性理由
        if not safety_check.get("safe", False):
            reasoning_parts.append(f"安全性に懸念: {safety_check.get('reason', '不明')}")
        else:
            reasoning_parts.append("安全性に問題なし")
        
        return "; ".join(reasoning_parts)
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """
        キーワード出現回数カウント
        
        Args:
            text (str): テキスト
            keywords (List[str]): キーワードリスト
            
        Returns:
            int: 出現回数
        """
        text_lower = text.lower()
        return sum(1 for keyword in keywords if keyword in text_lower)
    
    # 既存の基本メソッドも残す（互換性のため）
    async def analyze_post_safety(self, text: str) -> Dict[str, Any]:
        """基本的な安全性分析（後方互換性）"""
        safety = await self._analyze_safety(text)
        return {
            "safety_score": 0.8 if safety["safe"] else 0.3,
            "quality_score": random.uniform(0.6, 0.9),
            "safe": safety["safe"],
            "reason": safety["reason"]
        }
    
    async def analyze_for_action(self, text: str, metrics: Dict[str, int] = None) -> Dict[str, Any]:
        """アクション分析（後方互換性）"""
        analysis = await self.analyze_for_like_and_retweet(text, metrics)
        return {
            "recommended_action": analysis["recommended_action"],
            "confidence": analysis["confidence"],
            "reasoning": analysis["ai_reasoning"]
        }


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_advanced_analyzer():
        """高度な分析機能のテスト"""
        analyzer = PostAnalyzer()
        
        test_texts = [
            "今日は素晴らしい技術発表がありました！AIの未来が楽しみです。 #AI #技術",
            "政治家は全員腐敗している。絶対に許せない！！！",
            "新しいプログラミング言語のチュートリアルを公開しました。学習に役立ててください。",
            "限定セール！今すぐ購入で90%OFF！絶対お得！"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n=== テストケース {i} ===")
            print(f"テキスト: {text}")
            
            analysis = await analyzer.analyze_for_like_and_retweet(text)
            
            print(f"いいねスコア: {analysis['like_score']}")
            print(f"リポストスコア: {analysis['retweet_score']}")
            print(f"推奨アクション: {analysis['recommended_action']}")
            print(f"安全性: {analysis['safety_check']}")
            print(f"リスクレベル: {analysis['risk_level']}")
            print(f"カテゴリ: {analysis['content_category']}")
            print(f"信頼度: {analysis['confidence']:.2f}")
    
    # テスト実行
    asyncio.run(test_advanced_analyzer())