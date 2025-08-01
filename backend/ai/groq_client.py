"""
Groq AI クライアント（運営側一括管理）

このモジュールは以下の機能を提供します：
- Groq AI APIとの統合
- テキスト分析・生成
- 感情分析・コンテンツ分析
- 運営側でAPIキーを一括管理
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
import json

# Groq関連
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq library not installed. Install with: pip install groq")

# ログ
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Groq AI統合クライアント
# =============================================================================

class GroqClient:
    """
    Groq AI統合クライアント（運営側管理）
    
    運営者が一括でGroq APIキーを管理し、
    全ユーザーが共通でAI分析機能を利用できます。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key (Optional[str]): Groq APIキー（省略時は環境変数から取得）
        """
        # 運営側で一括管理されるAPIキー
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        # デフォルトモデル
        self.default_model = "llama3-8b-8192"
        
        # クライアント初期化
        self.client = None
        self._initialize_client()
        
        logger.info("GroqClient初期化完了（運営側管理）")
    
    def _initialize_client(self):
        """Groqクライアント初期化"""
        if not GROQ_AVAILABLE:
            logger.warning("Groq library が利用できません")
            return
        
        if not self.api_key:
            logger.warning("Groq API キーが設定されていません（運営側で設定が必要）")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq AIクライアント初期化成功")
        except Exception as e:
            logger.error(f"Groq AIクライアント初期化エラー: {e}")
    
    def is_available(self) -> bool:
        """
        Groq AIサービスが利用可能かチェック
        
        Returns:
            bool: 利用可能フラグ
        """
        return self.client is not None and GROQ_AVAILABLE
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        感情分析
        
        Args:
            text (str): 分析対象テキスト
            
        Returns:
            Dict[str, Any]: 感情分析結果
        """
        if not self.is_available():
            return {
                "error": "Groq AIサービスが利用できません（運営側で設定が必要）",
                "sentiment": "neutral",
                "confidence": 0.5
            }
        
        try:
            prompt = f"""
以下のツイートテキストの感情を分析してください：

テキスト: "{text}"

以下の形式でJSON回答してください：
{{
  "sentiment": "positive/negative/neutral",
  "confidence": 0.0-1.0,
  "reasoning": "判定理由",
  "keywords": ["感情を表すキーワード"]
}}
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "あなたは日本語テキストの感情分析専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # JSON解析を試行
            try:
                result = json.loads(content)
                logger.info("感情分析完了")
                return result
            except json.JSONDecodeError:
                # JSON解析失敗時はテキストベースで返す
                return {
                    "sentiment": "neutral",
                    "confidence": 0.7,
                    "reasoning": content,
                    "keywords": []
                }
                
        except Exception as e:
            logger.error(f"感情分析エラー: {e}")
            return {
                "error": f"分析エラー: {str(e)}",
                "sentiment": "neutral",
                "confidence": 0.5
            }
    
    async def analyze_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        コンテンツ分析
        
        Args:
            text (str): 分析対象テキスト
            analysis_type (str): 分析タイプ (general, engagement, safety)
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if not self.is_available():
            return {
                "error": "Groq AIサービスが利用できません（運営側で設定が必要）",
                "analysis_type": analysis_type,
                "score": 50
            }
        
        try:
            if analysis_type == "engagement":
                prompt = f"""
以下のツイートのエンゲージメント潜在力を分析してください：

テキスト: "{text}"

以下の観点で評価し、JSON形式で回答してください：
{{
  "engagement_score": 0-100,
  "virality_potential": 0-100,
  "shareability": 0-100,
  "factors": ["エンゲージメントを高める要因"],
  "recommendations": ["改善提案"]
}}
"""
            elif analysis_type == "safety":
                prompt = f"""
以下のツイートの安全性を分析してください：

テキスト: "{text}"

以下の観点で評価し、JSON形式で回答してください：
{{
  "safety_score": 0-100,
  "risk_factors": ["リスク要因"],
  "brand_safety": 0-100,
  "content_quality": 0-100,
  "recommendations": ["安全性向上提案"]
}}
"""
            else:  # general
                prompt = f"""
以下のツイートを総合的に分析してください：

テキスト: "{text}"

以下の形式でJSON回答してください：
{{
  "overall_score": 0-100,
  "content_type": "カテゴリ",
  "quality_score": 0-100,
  "audience_appeal": 0-100,
  "insights": ["分析結果"]
}}
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "あなたは日本語ソーシャルメディアコンテンツの分析専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
                result["analysis_type"] = analysis_type
                logger.info(f"コンテンツ分析完了: {analysis_type}")
                return result
            except json.JSONDecodeError:
                return {
                    "analysis_type": analysis_type,
                    "score": 70,
                    "content": content,
                    "error": "JSON解析に失敗しましたが、分析は完了しました"
                }
                
        except Exception as e:
            logger.error(f"コンテンツ分析エラー: {e}")
            return {
                "error": f"分析エラー: {str(e)}",
                "analysis_type": analysis_type,
                "score": 50
            }
    
    async def generate_suggestions(self, text: str, suggestion_type: str = "improvement") -> Dict[str, Any]:
        """
        改善提案生成
        
        Args:
            text (str): 対象テキスト
            suggestion_type (str): 提案タイプ (improvement, hashtags, timing)
            
        Returns:
            Dict[str, Any]: 提案結果
        """
        if not self.is_available():
            return {
                "error": "Groq AIサービスが利用できません（運営側で設定が必要）",
                "suggestions": []
            }
        
        try:
            if suggestion_type == "hashtags":
                prompt = f"""
以下のツイートに最適なハッシュタグを提案してください：

テキスト: "{text}"

以下の形式でJSON回答してください：
{{
  "recommended_hashtags": ["#ハッシュタグ1", "#ハッシュタグ2"],
  "trending_hashtags": ["#トレンドハッシュタグ"],
  "niche_hashtags": ["#ニッチハッシュタグ"],
  "reasoning": "選定理由"
}}
"""
            elif suggestion_type == "timing":
                prompt = f"""
以下のツイートの最適な投稿タイミングを提案してください：

テキスト: "{text}"

以下の形式でJSON回答してください：
{{
  "optimal_times": ["時間帯"],
  "day_of_week": ["曜日"],
  "audience_activity": "オーディエンス活動パターン",
  "reasoning": "タイミング選定理由"
}}
"""
            else:  # improvement
                prompt = f"""
以下のツイートの改善提案をしてください：

テキスト: "{text}"

以下の形式でJSON回答してください：
{{
  "improvements": ["改善提案"],
  "strengths": ["現在の強み"],
  "weaknesses": ["改善点"],
  "alternative_versions": ["改善版テキスト例"]
}}
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "あなたはソーシャルメディアマーケティングの専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
                result["suggestion_type"] = suggestion_type
                logger.info(f"提案生成完了: {suggestion_type}")
                return result
            except json.JSONDecodeError:
                return {
                    "suggestion_type": suggestion_type,
                    "suggestions": [content],
                    "error": "JSON解析に失敗しましたが、提案は生成されました"
                }
                
        except Exception as e:
            logger.error(f"提案生成エラー: {e}")
            return {
                "error": f"提案生成エラー: {str(e)}",
                "suggestion_type": suggestion_type,
                "suggestions": []
            }
    
    async def analyze_post_content(self, content: str, analysis_type: str = "engagement_prediction", user_id: str = None) -> Dict[str, Any]:
        """
        投稿内容の包括的分析
        
        Args:
            content (str): 投稿内容
            analysis_type (str): 分析タイプ
            user_id (str): ユーザーID（ログ用）
            
        Returns:
            Dict[str, Any]: 包括的分析結果
        """
        if not self.is_available():
            logger.warning(f"Groq AI利用不可 - フォールバック分析を返します (user: {user_id})")
            return self._generate_fallback_analysis(content)
        
        try:
            prompt = f"""
以下の投稿内容を包括的に分析し、エンゲージメント予測を行ってください：

投稿内容: "{content}"

以下の形式でJSON回答してください：
{{
  "overall_score": 0-100の総合スコア,
  "engagement_prediction": {{
    "likes": 予想いいね数,
    "retweets": 予想リツイート数,
    "replies": 予想返信数
  }},
  "sentiment": {{
    "positive": 0.0-1.0のポジティブ度,
    "neutral": 0.0-1.0のニュートラル度,
    "negative": 0.0-1.0のネガティブ度
  }},
  "keywords": ["抽出されたキーワード"],
  "recommendations": ["最適化の推奨事項"],
  "risk_assessment": "low/medium/high"
}}

分析は日本語のソーシャルメディア投稿として行い、現実的な数値を予測してください。
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "あなたは日本語ソーシャルメディア投稿の分析専門家です。現実的で実用的な分析を提供してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content
            
            try:
                result = json.loads(content_response)
                logger.info(f"AI投稿分析完了 (user: {user_id})")
                return result
            except json.JSONDecodeError:
                logger.warning(f"AI分析JSON解析失敗 - フォールバック分析を返します (user: {user_id})")
                return self._generate_fallback_analysis(content)
                
        except Exception as e:
            logger.error(f"AI投稿分析エラー (user: {user_id}): {e}")
            return self._generate_fallback_analysis(content)
    
    def _generate_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """フォールバック分析生成"""
        content_length = len(content) if content else 0
        
        # 基本スコア計算
        base_score = 50
        if content_length > 100:
            base_score += 20
        if '#' in content:
            base_score += 10
        if content_length < 280:
            base_score += 10
        if '?' in content or '！' in content:
            base_score += 5
        
        # エンゲージメント予測
        likes_base = max(20, content_length * 1.5)
        retweets_base = max(10, content_length * 0.8)
        replies_base = max(5, content_length * 0.4)
        
        return {
            "overall_score": min(base_score, 95),
            "engagement_prediction": {
                "likes": int(likes_base),
                "retweets": int(retweets_base),
                "replies": int(replies_base)
            },
            "sentiment": {
                "positive": 0.6,
                "neutral": 0.3,
                "negative": 0.1
            },
            "keywords": self._extract_basic_keywords_fallback(content),
            "recommendations": self._generate_basic_recommendations_fallback(content),
            "risk_assessment": "low",
            "note": "AI分析が利用できないため、基本的な分析を表示しています"
        }
    
    def _extract_basic_keywords_fallback(self, content: str) -> List[str]:
        """フォールバック用キーワード抽出"""
        if not content:
            return ["投稿"]
        
        common_words = ["AI", "自動化", "テクノロジー", "効率化", "ビジネス", "マーケティング", "SNS", "Twitter"]
        found_words = [word for word in common_words if word.lower() in content.lower()]
        
        return found_words if found_words else ["一般"]
    
    def _generate_basic_recommendations_fallback(self, content: str) -> List[str]:
        """フォールバック用推奨事項生成"""
        recommendations = []
        
        if not content:
            return ["投稿内容を入力してください"]
        
        if len(content) < 50:
            recommendations.append("投稿をもう少し詳しく書くとエンゲージメントが向上します")
        
        if '#' not in content:
            recommendations.append("関連するハッシュタグを追加することをお勧めします")
        
        if len(content) > 280:
            recommendations.append("投稿が長すぎる可能性があります。簡潔にまとめることを検討してください")
        
        if '?' not in content and '！' not in content:
            recommendations.append("疑問符や感嘆符を使って感情を表現すると良いでしょう")
        
        recommendations.append("投稿時間を19-21時に設定すると良いでしょう")
        
        return recommendations
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        サービス状態取得
        
        Returns:
            Dict[str, Any]: サービス状態情報
        """
        return {
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "groq_library_installed": GROQ_AVAILABLE,
            "default_model": self.default_model,
            "management": "運営側一括管理",
            "user_setup_required": False
        }


# =============================================================================
# グローバルインスタンス（運営側管理）
# =============================================================================

# 運営者が一括でGroq APIキーを設定
_global_groq_client = None

def get_groq_client() -> GroqClient:
    """
    グローバルGroqクライアントを取得
    
    Returns:
        GroqClient: 運営側管理のGroqクライアント
    """
    global _global_groq_client
    
    if _global_groq_client is None:
        # 運営側で設定されたAPIキーを使用
        _global_groq_client = GroqClient()
    
    return _global_groq_client

def configure_groq_api_key(api_key: str):
    """
    運営者用：Groq APIキーの設定
    
    Args:
        api_key (str): Groq APIキー
    """
    global _global_groq_client
    
    # 環境変数に設定
    os.environ["GROQ_API_KEY"] = api_key
    
    # 新しいクライアントを作成
    _global_groq_client = GroqClient(api_key)
    
    logger.info("運営側Groq APIキーが更新されました")


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_groq_client():
        """GroqClientのテスト"""
        client = get_groq_client()
        
        print("=== Groq AIクライアントテスト（運営側管理）===")
        
        # サービス状態確認
        status = await client.get_service_status()
        print(f"サービス状態: {status}")
        
        if not client.is_available():
            print("Groq AIサービスが利用できません（運営側でAPIキー設定が必要）")
            return
        
        # テストテキスト
        test_text = "今日は素晴らしい技術発表会でした！AI技術の進歩に感動しています。 #AI #技術"
        
        print(f"\nテストテキスト: {test_text}")
        
        # 感情分析テスト
        print("\n--- 感情分析 ---")
        sentiment = await client.analyze_sentiment(test_text)
        print(f"感情分析結果: {sentiment}")
        
        # エンゲージメント分析テスト
        print("\n--- エンゲージメント分析 ---")
        engagement = await client.analyze_content(test_text, "engagement")
        print(f"エンゲージメント分析: {engagement}")
        
        # 安全性分析テスト
        print("\n--- 安全性分析 ---")
        safety = await client.analyze_content(test_text, "safety")
        print(f"安全性分析: {safety}")
    
    # テスト実行
    asyncio.run(test_groq_client())