"""
柔軟なデータ保持期間管理（シンVPS対応）

ユーザーが選択可能な保持期間設定
継続利用とプライバシー保護のバランス
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

from backend.infrastructure.operator_blind_storage import operator_blind_storage

logger = logging.getLogger(__name__)

class RetentionMode(Enum):
    """データ保持モード"""
    ULTRA_PRIVATE = "ultra_private"      # 24時間（最高プライバシー）
    BALANCED = "balanced"                # 7日間（バランス型）
    CONVENIENT = "convenient"            # 30日間（利便性重視）
    CONTINUOUS = "continuous"            # 無期限（継続利用）

class FlexibleRetentionManager:
    """
    柔軟なデータ保持期間管理
    
    ユーザーのニーズに応じて保持期間を選択可能
    プライバシーと利便性のバランスを調整
    """
    
    def __init__(self):
        """初期化"""
        self.retention_configs = {
            RetentionMode.ULTRA_PRIVATE: {
                "hours": 24,
                "name": "ウルトラプライベート",
                "description": "24時間で自動削除（最高プライバシー）",
                "use_case": "一時的な利用・テスト目的",
                "privacy_level": "最高",
                "convenience": "低",
                "recommended_for": ["プライバシー重視", "一時利用", "テスト"]
            },
            RetentionMode.BALANCED: {
                "hours": 168,  # 7日
                "name": "バランス型",
                "description": "7日間保持（週単位利用）",
                "use_case": "週単位での利用パターン",
                "privacy_level": "高",
                "convenience": "中",
                "recommended_for": ["週単位利用", "バランス重視", "定期利用"]
            },
            RetentionMode.CONVENIENT: {
                "hours": 720,  # 30日
                "name": "利便性重視",
                "description": "30日間保持（月単位利用）",
                "use_case": "月単位での継続利用",
                "privacy_level": "中",
                "convenience": "高",
                "recommended_for": ["月単位利用", "ビジネス用途", "継続利用"]
            },
            RetentionMode.CONTINUOUS: {
                "hours": 0,  # 無期限
                "name": "継続利用",
                "description": "手動削除まで保持（最高利便性）",
                "use_case": "長期継続利用・ビジネス運用",
                "privacy_level": "中",
                "convenience": "最高",
                "recommended_for": ["長期利用", "ビジネス", "自動化メイン"]
            }
        }
        
        logger.info("FlexibleRetentionManager初期化完了")
    
    def get_retention_options(self) -> Dict[str, Any]:
        """
        保持期間選択肢を取得
        
        Returns:
            Dict[str, Any]: 保持期間オプション
        """
        options = {}
        
        for mode, config in self.retention_configs.items():
            options[mode.value] = {
                "name": config["name"],
                "description": config["description"],
                "hours": config["hours"],
                "days": config["hours"] // 24 if config["hours"] > 0 else "無期限",
                "privacy_level": config["privacy_level"],
                "convenience": config["convenience"],
                "use_case": config["use_case"],
                "recommended_for": config["recommended_for"],
                "auto_reentry_required": config["hours"] > 0  # 自動削除される場合はtrue
            }
        
        return options
    
    def get_retention_recommendation(self, user_profile: Dict[str, Any]) -> RetentionMode:
        """
        ユーザープロフィールに基づく推奨保持期間
        
        Args:
            user_profile (Dict[str, Any]): ユーザープロフィール
            
        Returns:
            RetentionMode: 推奨保持期間
        """
        # 利用パターン分析
        usage_frequency = user_profile.get("usage_frequency", "occasional")  # daily, weekly, monthly, occasional
        privacy_priority = user_profile.get("privacy_priority", "medium")    # high, medium, low
        business_use = user_profile.get("business_use", False)
        automation_main = user_profile.get("automation_main", False)
        
        # 推奨ロジック
        if privacy_priority == "high" and usage_frequency == "occasional":
            return RetentionMode.ULTRA_PRIVATE
        elif business_use or automation_main:
            return RetentionMode.CONTINUOUS
        elif usage_frequency == "daily":
            return RetentionMode.CONVENIENT
        elif usage_frequency == "weekly":
            return RetentionMode.BALANCED
        else:
            return RetentionMode.BALANCED  # デフォルト
    
    def calculate_next_deletion(self, retention_mode: RetentionMode, 
                              last_accessed: datetime) -> Optional[datetime]:
        """
        次回削除予定時刻を計算
        
        Args:
            retention_mode (RetentionMode): 保持モード
            last_accessed (datetime): 最終アクセス時刻
            
        Returns:
            Optional[datetime]: 削除予定時刻（無期限の場合はNone）
        """
        config = self.retention_configs[retention_mode]
        
        if config["hours"] == 0:  # 無期限
            return None
        
        return last_accessed + timedelta(hours=config["hours"])
    
    def get_deletion_warning_times(self, deletion_time: datetime) -> List[datetime]:
        """
        削除警告通知タイミングを計算
        
        Args:
            deletion_time (datetime): 削除予定時刻
            
        Returns:
            List[datetime]: 警告通知タイミング
        """
        warnings = []
        now = datetime.utcnow()
        
        # 削除24時間前
        warning_24h = deletion_time - timedelta(hours=24)
        if warning_24h > now:
            warnings.append(warning_24h)
        
        # 削除6時間前
        warning_6h = deletion_time - timedelta(hours=6)
        if warning_6h > now:
            warnings.append(warning_6h)
        
        # 削除1時間前
        warning_1h = deletion_time - timedelta(hours=1)
        if warning_1h > now:
            warnings.append(warning_1h)
        
        return warnings
    
    async def extend_retention_period(self, user_id: str, new_mode: RetentionMode) -> Dict[str, Any]:
        """
        保持期間の延長・変更
        
        Args:
            user_id (str): ユーザーID
            new_mode (RetentionMode): 新しい保持モード
            
        Returns:
            Dict[str, Any]: 変更結果
        """
        try:
            # 運営者ブラインド設計のため、直接データベース操作
            # （実際の実装では、ユーザーがパスワードで認証後に変更）
            
            config = self.retention_configs[new_mode]
            
            return {
                "success": True,
                "new_retention_mode": new_mode.value,
                "new_config": config,
                "message": f"保持期間を「{config['name']}」に変更しました",
                "auto_delete_hours": config["hours"] if config["hours"] > 0 else "無期限",
                "next_reentry_required": config["hours"] > 0
            }
            
        except Exception as e:
            logger.error(f"保持期間変更エラー: {e}")
            return {"error": f"変更エラー: {str(e)}"}
    
    def get_user_experience_comparison(self) -> Dict[str, Any]:
        """
        ユーザーエクスペリエンス比較表
        
        Returns:
            Dict[str, Any]: UX比較情報
        """
        return {
            "comparison_table": {
                "保持期間": ["24時間", "7日間", "30日間", "無期限"],
                "再設定頻度": ["毎日", "週1回", "月1回", "不要"],
                "プライバシー": ["最高", "高", "中", "中"],
                "利便性": ["低", "中", "高", "最高"],
                "推奨用途": [
                    "一時利用・テスト",
                    "週単位の定期利用",
                    "月単位の継続利用",
                    "ビジネス・長期利用"
                ]
            },
            "ux_impact": {
                "ultra_private": {
                    "pros": ["最高プライバシー", "データ残存リスクゼロ"],
                    "cons": ["毎日再設定必要", "利便性低", "継続利用困難"]
                },
                "balanced": {
                    "pros": ["週1回設定で継続利用", "プライバシーと利便性両立"],
                    "cons": ["週末に再設定必要"]
                },
                "convenient": {
                    "pros": ["月1回設定のみ", "継続利用しやすい"],
                    "cons": ["30日間データ保持"]
                },
                "continuous": {
                    "pros": ["設定一度きり", "完全な継続利用", "ビジネス向け"],
                    "cons": ["手動削除まで保持", "忘れやすい"]
                }
            },
            "recommendations": {
                "個人・プライバシー重視": "balanced（7日間）",
                "個人・利便性重視": "convenient（30日間）",
                "ビジネス・自動化メイン": "continuous（無期限）",
                "テスト・一時利用": "ultra_private（24時間）"
            }
        }
    
    def get_auto_extension_options(self) -> Dict[str, Any]:
        """
        自動延長オプション（将来実装用）
        
        Returns:
            Dict[str, Any]: 自動延長オプション
        """
        return {
            "auto_extension_available": True,
            "options": {
                "usage_based": {
                    "name": "利用状況ベース自動延長",
                    "description": "アクセスがあった場合に自動で期間延長",
                    "implementation": "last_accessed更新時に期間リセット"
                },
                "schedule_based": {
                    "name": "スケジュールベース自動延長",
                    "description": "定期的にユーザーに延長確認",
                    "implementation": "メール・ブラウザ通知での延長案内"
                },
                "smart_prediction": {
                    "name": "スマート予測延長",
                    "description": "利用パターンを学習して最適な期間設定",
                    "implementation": "AI分析による個別最適化"
                }
            },
            "user_control": {
                "manual_extension": "ユーザーがいつでも期間延長可能",
                "mode_change": "保持モードの自由変更",
                "immediate_deletion": "即座削除オプション"
            }
        }


# グローバルインスタンス
flexible_retention = FlexibleRetentionManager()

def get_retention_options() -> Dict[str, Any]:
    """保持期間選択肢を取得"""
    return flexible_retention.get_retention_options()

def recommend_retention_mode(user_profile: Dict[str, Any]) -> str:
    """推奨保持期間を取得"""
    mode = flexible_retention.get_retention_recommendation(user_profile)
    return mode.value

def get_ux_comparison() -> Dict[str, Any]:
    """UX比較情報を取得"""
    return flexible_retention.get_user_experience_comparison()


if __name__ == "__main__":
    # 保持期間オプションの確認
    print("=== 柔軟なデータ保持期間設定 ===")
    
    options = get_retention_options()
    print("\n利用可能な保持期間:")
    for mode_id, config in options.items():
        print(f"\n{config['name']} ({mode_id}):")
        print(f"  期間: {config['days']}")
        print(f"  説明: {config['description']}")
        print(f"  再設定必要: {config['auto_reentry_required']}")
    
    print("\n=== UX比較 ===")
    ux = get_ux_comparison()
    print("推奨用途:")
    for use_case, recommendation in ux["recommendations"].items():
        print(f"  {use_case}: {recommendation}")