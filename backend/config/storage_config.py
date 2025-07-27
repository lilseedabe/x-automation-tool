"""
統一データ管理設定（シンVPS専用）

全てのデータ管理をシンVPS + 運営者ブラインド方式に統一
ローカルファイル保存は完全廃止
"""

import os
from typing import Dict, Any
from enum import Enum

class StorageMode(Enum):
    """データ保存モード（シンVPS専用）"""
    SHIN_VPS_BLIND = "shin_vps_blind"  # シンVPS + 運営者ブラインド（推奨）
    LOCAL_BROWSER = "local_browser"    # ブラウザローカルストレージ（手動実行のみ）

class UnifiedStorageConfig:
    """
    統一データ管理設定
    
    シンVPS + 運営者ブラインド方式に統一
    ローカルファイル保存は廃止
    """
    
    def __init__(self):
        """初期化"""
        # 統一設定
        self.primary_storage = StorageMode.SHIN_VPS_BLIND
        self.fallback_storage = StorageMode.LOCAL_BROWSER
        
        # シンVPS設定
        self.shin_vps_config = {
            "provider": "シンクラウド（GMOインターネット）",
            "location": "日本国内データセンター",
            "database_type": "MySQL 8.0",
            "encryption": "RSA-2048 + AES-256",
            "operator_access": False,  # 運営者アクセス不可
            "auto_delete_hours": 24,
            "cost_per_month": "770円〜",
            "privacy_level": "最高"
        }
        
        # 廃止される設定
        self.deprecated_storages = [
            "local_file_system",     # data/users/ 廃止
            "render_postgresql",     # Render PostgreSQL 廃止
            "render_file_storage",   # Render ファイル保存 廃止
        ]
    
    def get_active_storage_mode(self) -> StorageMode:
        """
        アクティブなストレージモードを取得
        
        Returns:
            StorageMode: 現在のストレージモード
        """
        # 環境変数での強制指定をチェック
        forced_mode = os.getenv("FORCE_STORAGE_MODE")
        if forced_mode == "local_browser":
            return StorageMode.LOCAL_BROWSER
        
        # デフォルトはシンVPS
        return StorageMode.SHIN_VPS_BLIND
    
    def get_database_url(self) -> str:
        """
        データベースURL取得（シンVPS用）
        
        Returns:
            str: データベース接続URL
        """
        # シンVPS MySQL接続URL
        return os.getenv("SHIN_VPS_DATABASE_URL") or os.getenv("DATABASE_URL") or ""
    
    def is_local_file_system_disabled(self) -> bool:
        """
        ローカルファイルシステムが無効化されているかチェック
        
        Returns:
            bool: 無効化フラグ
        """
        return True  # 常に無効（シンVPS統一のため）
    
    def get_storage_migration_plan(self) -> Dict[str, Any]:
        """
        ストレージ移行計画を取得
        
        Returns:
            Dict[str, Any]: 移行計画
        """
        return {
            "current_state": "複数のストレージ方式が混在",
            "target_state": "シンVPS + 運営者ブラインド統一",
            "migration_steps": [
                "1. ローカルファイル保存（data/users/）を廃止",
                "2. Render関連設定を削除",
                "3. シンVPS設定に統一",
                "4. 運営者ブラインド・ストレージのみ有効化",
                "5. ユーザーデータを新システムに移行案内"
            ],
            "deprecated_paths": [
                "data/users/",
                "data/users.json",
                "backend/services/local_storage.py",
                "backend/database/render_storage.py"
            ],
            "new_architecture": {
                "primary": "backend/infrastructure/operator_blind_storage.py",
                "fallback": "frontend/src/services/apiKeyManager.js (ローカルストレージ)",
                "database": "シンVPS MySQL",
                "encryption": "ユーザー専用キー + 運営者ブラインド"
            }
        }
    
    def get_user_options(self) -> Dict[str, Any]:
        """
        ユーザー向け選択肢を取得
        
        Returns:
            Dict[str, Any]: ユーザー選択肢
        """
        return {
            "recommended": {
                "mode": "shin_vps_blind",
                "name": "シンVPS継続実行モード",
                "description": "24時間自動実行・運営者アクセス不可",
                "privacy_level": "最高",
                "cost": "無料（運営者負担）",
                "features": [
                    "✅ 運営者が技術的にデータアクセス不可",
                    "✅ 日本国内サーバー（シンVPS）",
                    "✅ 24時間継続自動実行",
                    "✅ 暗号化＋自動削除",
                    "✅ 国際データ移転なし"
                ]
            },
            "alternative": {
                "mode": "local_browser",
                "name": "手動実行モード",
                "description": "ブラウザローカルストレージのみ",
                "privacy_level": "最高",
                "cost": "無料",
                "features": [
                    "✅ ブラウザのローカルストレージのみ",
                    "✅ サーバーには一切保存されない",
                    "✅ 手動実行のみ",
                    "❌ 継続自動実行なし"
                ]
            },
            "deprecated": [
                "render_postgresql（廃止）",
                "local_file_system（廃止）",
                "mixed_storage（廃止）"
            ]
        }
    
    def get_environment_config(self) -> Dict[str, str]:
        """
        環境設定を取得
        
        Returns:
            Dict[str, str]: 環境変数設定
        """
        return {
            # シンVPS設定
            "SHIN_VPS_DATABASE_URL": "mysql+asyncio://username:password@your-shin-vps.com:3306/x_automation_db",
            "STORAGE_MODE": "shin_vps_blind",
            "OPERATOR_BLIND_ENABLED": "true",
            
            # Groq AI（運営者管理）
            "GROQ_API_KEY": "your_groq_api_key_here",
            
            # セキュリティ設定
            "AUTO_DELETE_HOURS": "24",
            "ENCRYPTION_LEVEL": "maximum",
            "PRIVACY_MODE": "operator_blind",
            
            # 廃止設定（無効化）
            "LOCAL_FILE_STORAGE_ENABLED": "false",
            "RENDER_STORAGE_ENABLED": "false",
            "MULTI_STORAGE_MODE": "false",
            
            # サーバー情報
            "SERVER_PROVIDER": "シンクラウド",
            "SERVER_LOCATION": "日本",
            "MONTHLY_COST": "770円〜"
        }


# グローバルインスタンス
unified_config = UnifiedStorageConfig()

def get_storage_config() -> UnifiedStorageConfig:
    """統一ストレージ設定を取得"""
    return unified_config

def is_shin_vps_mode() -> bool:
    """シンVPSモードかチェック"""
    return unified_config.get_active_storage_mode() == StorageMode.SHIN_VPS_BLIND

def is_local_file_deprecated() -> bool:
    """ローカルファイルシステムが廃止されているかチェック"""
    return unified_config.is_local_file_system_disabled()

def get_migration_plan() -> Dict[str, Any]:
    """移行計画を取得"""
    return unified_config.get_storage_migration_plan()


if __name__ == "__main__":
    # 設定確認
    config = get_storage_config()
    
    print("=== 統一データ管理設定 ===")
    print(f"アクティブモード: {config.get_active_storage_mode()}")
    print(f"シンVPSモード: {is_shin_vps_mode()}")
    print(f"ローカルファイル廃止: {is_local_file_deprecated()}")
    
    print("\n=== 移行計画 ===")
    migration = get_migration_plan()
    for step in migration["migration_steps"]:
        print(f"  {step}")
    
    print("\n=== ユーザー選択肢 ===")
    options = config.get_user_options()
    print(f"推奨: {options['recommended']['name']}")
    print(f"代替: {options['alternative']['name']}")
    print(f"廃止: {', '.join(options['deprecated'])}")