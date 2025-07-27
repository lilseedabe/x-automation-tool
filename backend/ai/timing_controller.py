"""
AIタイミング制御モジュール

このモジュールは以下の機能を提供します：
- 最適な投稿タイミングの分析・予測
- スケジュール管理
- タイミング最適化アルゴリズム
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# タイミング制御クラス
# =============================================================================

class TimingController:
    """
    AIタイミング制御
    
    投稿の最適なタイミングを分析・制御します。
    """
    
    def __init__(self):
        """初期化"""
        # デフォルトの最適時間帯（日本時間）
        self.optimal_hours = {
            "weekday": [7, 8, 12, 19, 20, 21],  # 平日
            "weekend": [9, 10, 14, 15, 20, 21]  # 週末
        }
        
        # エンゲージメント重み
        self.engagement_weights = {
            "morning": 1.2,    # 朝（6-10時）
            "lunch": 1.5,      # 昼（11-14時）
            "evening": 1.8,    # 夕方（17-20時）
            "night": 1.3,      # 夜（20-23時）
            "late_night": 0.8  # 深夜（23-6時）
        }
        
        logger.info("TimingController初期化完了")
    
    async def analyze_optimal_timing(self, content: str, target_audience: str = "general") -> Dict[str, Any]:
        """
        最適投稿タイミング分析
        
        Args:
            content (str): 投稿内容
            target_audience (str): ターゲットオーディエンス
            
        Returns:
            Dict[str, Any]: タイミング分析結果
        """
        try:
            # コンテンツ分析
            content_analysis = self._analyze_content_type(content)
            
            # オーディエンス分析
            audience_preferences = self._get_audience_preferences(target_audience)
            
            # 時間帯別スコア計算
            timing_scores = self._calculate_timing_scores(content_analysis, audience_preferences)
            
            # 最適時間帯を推奨
            recommendations = self._generate_timing_recommendations(timing_scores)
            
            result = {
                "content_type": content_analysis["type"],
                "target_audience": target_audience,
                "timing_scores": timing_scores,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info("最適投稿タイミング分析完了")
            return result
            
        except Exception as e:
            logger.error(f"タイミング分析エラー: {e}")
            return {"error": f"タイミング分析エラー: {str(e)}"}
    
    def _analyze_content_type(self, content: str) -> Dict[str, Any]:
        """
        コンテンツタイプ分析
        
        Args:
            content (str): 投稿内容
            
        Returns:
            Dict[str, Any]: コンテンツ分析結果
        """
        # 簡易的なコンテンツ分類
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["ニュース", "速報", "発表", "リリース"]):
            content_type = "news"
        elif any(word in content_lower for word in ["質問", "?", "？", "教えて", "どう思う"]):
            content_type = "question"
        elif any(word in content_lower for word in ["おはよう", "こんにちは", "こんばんは"]):
            content_type = "greeting"
        elif any(word in content_lower for word in ["宣伝", "セール", "キャンペーン", "割引"]):
            content_type = "promotional"
        elif any(word in content_lower for word in ["感謝", "ありがとう", "お疲れ様"]):
            content_type = "appreciation"
        else:
            content_type = "general"
        
        return {
            "type": content_type,
            "length": len(content),
            "has_hashtags": "#" in content,
            "has_mentions": "@" in content,
            "has_urls": "http" in content_lower
        }
    
    def _get_audience_preferences(self, target_audience: str) -> Dict[str, Any]:
        """
        ターゲットオーディエンスの傾向取得
        
        Args:
            target_audience (str): ターゲットオーディエンス
            
        Returns:
            Dict[str, Any]: オーディエンス傾向
        """
        audience_patterns = {
            "general": {
                "active_hours": [7, 8, 12, 19, 20, 21],
                "peak_days": ["tuesday", "wednesday", "thursday"],
                "engagement_pattern": "standard"
            },
            "business": {
                "active_hours": [9, 10, 11, 14, 15, 16],
                "peak_days": ["tuesday", "wednesday", "thursday"],
                "engagement_pattern": "business_hours"
            },
            "students": {
                "active_hours": [7, 12, 18, 19, 20, 21, 22],
                "peak_days": ["monday", "tuesday", "wednesday", "thursday", "sunday"],
                "engagement_pattern": "student_schedule"
            },
            "tech": {
                "active_hours": [9, 10, 14, 15, 20, 21],
                "peak_days": ["tuesday", "wednesday", "thursday"],
                "engagement_pattern": "tech_community"
            },
            "entertainment": {
                "active_hours": [19, 20, 21, 22],
                "peak_days": ["friday", "saturday", "sunday"],
                "engagement_pattern": "leisure_time"
            }
        }
        
        return audience_patterns.get(target_audience, audience_patterns["general"])
    
    def _calculate_timing_scores(self, content_analysis: Dict[str, Any], 
                                audience_preferences: Dict[str, Any]) -> Dict[str, float]:
        """
        時間帯別スコア計算
        
        Args:
            content_analysis (Dict[str, Any]): コンテンツ分析結果
            audience_preferences (Dict[str, Any]): オーディエンス傾向
            
        Returns:
            Dict[str, float]: 時間帯別スコア
        """
        scores = {}
        content_type = content_analysis["type"]
        active_hours = audience_preferences["active_hours"]
        
        # 24時間すべてのスコアを計算
        for hour in range(24):
            base_score = 0.5  # ベーススコア
            
            # アクティブ時間帯ボーナス
            if hour in active_hours:
                base_score += 0.3
            
            # コンテンツタイプ別調整
            if content_type == "news" and 6 <= hour <= 9:
                base_score += 0.2  # 朝のニュースボーナス
            elif content_type == "question" and 12 <= hour <= 14:
                base_score += 0.2  # 昼の質問ボーナス
            elif content_type == "greeting":
                if hour in [7, 8, 9]:  # おはよう
                    base_score += 0.3
                elif hour in [12, 13]:  # こんにちは
                    base_score += 0.2
                elif hour in [18, 19, 20]:  # こんばんは
                    base_score += 0.2
            elif content_type == "promotional" and 10 <= hour <= 16:
                base_score += 0.15  # 営業時間ボーナス
            
            # 時間帯別重み適用
            time_period = self._get_time_period(hour)
            weight = self.engagement_weights.get(time_period, 1.0)
            final_score = min(base_score * weight, 1.0)
            
            scores[f"{hour:02d}:00"] = round(final_score, 3)
        
        return scores
    
    def _get_time_period(self, hour: int) -> str:
        """
        時間帯分類取得
        
        Args:
            hour (int): 時間（0-23）
            
        Returns:
            str: 時間帯分類
        """
        if 6 <= hour <= 10:
            return "morning"
        elif 11 <= hour <= 14:
            return "lunch"
        elif 17 <= hour <= 20:
            return "evening"
        elif 20 <= hour <= 23:
            return "night"
        else:
            return "late_night"
    
    def _generate_timing_recommendations(self, timing_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        タイミング推奨事項生成
        
        Args:
            timing_scores (Dict[str, float]): 時間帯別スコア
            
        Returns:
            Dict[str, Any]: 推奨事項
        """
        # スコア順にソート
        sorted_times = sorted(timing_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 上位3つの時間帯を推奨
        top_times = sorted_times[:3]
        
        # 今日の推奨時間
        now = datetime.now()
        today_recommendations = []
        
        for time_str, score in top_times:
            hour = int(time_str.split(":")[0])
            target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # 過去の時間の場合は明日に設定
            if target_time <= now:
                target_time += timedelta(days=1)
            
            today_recommendations.append({
                "time": target_time.strftime("%Y-%m-%d %H:%M"),
                "score": score,
                "relative_time": self._get_relative_time(target_time, now)
            })
        
        # 曜日別推奨
        weekday_scores = self._calculate_weekday_scores()
        
        return {
            "best_times_today": today_recommendations,
            "optimal_hours": [time for time, score in top_times],
            "peak_score": top_times[0][1] if top_times else 0,
            "weekday_recommendations": weekday_scores,
            "general_advice": self._generate_general_advice(timing_scores)
        }
    
    def _get_relative_time(self, target_time: datetime, now: datetime) -> str:
        """
        相対時間表示取得
        
        Args:
            target_time (datetime): 対象時間
            now (datetime): 現在時間
            
        Returns:
            str: 相対時間表示
        """
        diff = target_time - now
        hours = diff.total_seconds() / 3600
        
        if hours < 1:
            return "1時間以内"
        elif hours < 24:
            return f"約{int(hours)}時間後"
        else:
            days = int(hours / 24)
            remaining_hours = int(hours % 24)
            return f"{days}日{remaining_hours}時間後"
    
    def _calculate_weekday_scores(self) -> Dict[str, float]:
        """
        曜日別スコア計算
        
        Returns:
            Dict[str, float]: 曜日別スコア
        """
        # 簡易的な曜日別エンゲージメント傾向
        weekday_patterns = {
            "monday": 0.8,
            "tuesday": 0.95,
            "wednesday": 1.0,
            "thursday": 0.95,
            "friday": 0.85,
            "saturday": 0.7,
            "sunday": 0.75
        }
        
        return weekday_patterns
    
    def _generate_general_advice(self, timing_scores: Dict[str, float]) -> List[str]:
        """
        一般的なアドバイス生成
        
        Args:
            timing_scores (Dict[str, float]): 時間帯別スコア
            
        Returns:
            List[str]: アドバイスリスト
        """
        advice = []
        
        # 最高スコア時間帯を特定
        max_score = max(timing_scores.values())
        peak_times = [time for time, score in timing_scores.items() if score == max_score]
        
        if any("07:00" <= time <= "09:00" for time in peak_times):
            advice.append("朝の時間帯（7-9時）が最も効果的です")
        
        if any("12:00" <= time <= "14:00" for time in peak_times):
            advice.append("昼休み時間帯（12-14時）にエンゲージメントが高まります")
        
        if any("19:00" <= time <= "21:00" for time in peak_times):
            advice.append("夕方から夜（19-21時）が投稿に適しています")
        
        # 避けるべき時間帯
        min_score = min(timing_scores.values())
        if min_score < 0.3:
            low_times = [time for time, score in timing_scores.items() if score == min_score]
            advice.append(f"深夜・早朝の時間帯は避けることをお勧めします")
        
        advice.append("平日の火曜日〜木曜日が一般的に最もエンゲージメントが高いです")
        advice.append("週末は娯楽系コンテンツの反応が良い傾向にあります")
        
        return advice
    
    async def schedule_optimal_posting(self, content: str, target_audience: str = "general",
                                     days_ahead: int = 7) -> Dict[str, Any]:
        """
        最適投稿スケジュール生成
        
        Args:
            content (str): 投稿内容
            target_audience (str): ターゲットオーディエンス
            days_ahead (int): 先の日数
            
        Returns:
            Dict[str, Any]: スケジュール結果
        """
        try:
            # タイミング分析
            timing_analysis = await self.analyze_optimal_timing(content, target_audience)
            
            if "error" in timing_analysis:
                return timing_analysis
            
            # 今後の最適スケジュール生成
            schedule = []
            now = datetime.now()
            
            for day in range(days_ahead):
                target_date = now + timedelta(days=day)
                weekday = target_date.strftime("%A").lower()
                
                # 曜日別スコア取得
                weekday_scores = timing_analysis["recommendations"]["weekday_recommendations"]
                day_multiplier = weekday_scores.get(weekday, 0.8)
                
                # その日の最適時間を計算
                daily_recommendations = []
                timing_scores = timing_analysis["timing_scores"]
                
                # 上位3つの時間帯を推奨
                sorted_times = sorted(timing_scores.items(), key=lambda x: x[1], reverse=True)
                
                for time_str, base_score in sorted_times[:3]:
                    hour = int(time_str.split(":")[0])
                    scheduled_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # 過去の時間をスキップ
                    if scheduled_time <= now:
                        continue
                    
                    adjusted_score = base_score * day_multiplier
                    
                    daily_recommendations.append({
                        "datetime": scheduled_time.strftime("%Y-%m-%d %H:%M"),
                        "score": round(adjusted_score, 3),
                        "weekday": weekday,
                        "time_period": self._get_time_period(hour)
                    })
                
                if daily_recommendations:
                    schedule.extend(daily_recommendations[:2])  # 1日最大2回
            
            # スコア順にソート
            schedule.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "content": content,
                "target_audience": target_audience,
                "schedule_period": f"{days_ahead}日間",
                "recommended_schedule": schedule[:10],  # 上位10個
                "analysis_summary": timing_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"最適投稿スケジュール生成エラー: {e}")
            return {"error": f"スケジュール生成エラー: {str(e)}"}


# =============================================================================
# ユーティリティ関数
# =============================================================================

def get_next_optimal_time(content_type: str = "general", hours_ahead: int = 24) -> datetime:
    """
    次の最適投稿時間を取得
    
    Args:
        content_type (str): コンテンツタイプ
        hours_ahead (int): 先の時間数
        
    Returns:
        datetime: 次の最適時間
    """
    controller = TimingController()
    now = datetime.now()
    
    # 簡易的な最適時間計算
    optimal_hours = controller.optimal_hours["weekday"]
    
    for hour in optimal_hours:
        target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if target_time > now:
            return target_time
    
    # 当日に最適時間がない場合は翌日の最初の最適時間
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_timing_controller():
        """TimingControllerのテスト"""
        controller = TimingController()
        
        # テストコンテンツ
        test_content = "新しいAI技術について質問があります。皆さんはどう思いますか？ #AI #技術"
        
        print("=== 最適投稿タイミング分析テスト ===")
        timing_analysis = await controller.analyze_optimal_timing(test_content, "tech")
        print(f"分析結果: {timing_analysis}")
        
        print("\n=== 最適投稿スケジュール生成テスト ===")
        schedule = await controller.schedule_optimal_posting(test_content, "tech", 3)
        
        if "error" not in schedule:
            print("✓ スケジュール生成成功")
            print(f"推奨スケジュール数: {len(schedule['recommended_schedule'])}")
            
            for item in schedule['recommended_schedule'][:3]:
                print(f"- {item['datetime']} (スコア: {item['score']})")
        else:
            print("✗ スケジュール生成失敗")
            print(f"エラー: {schedule['error']}")
    
    # テスト実行
    asyncio.run(test_timing_controller())