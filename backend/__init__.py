"""
X API研究・分析ツール バックエンド

このパッケージは、X API研究・分析ツールのバックエンド機能を提供します。
FastAPIを使用したRESTful APIサーバーとして動作し、以下の機能を含みます：

- ユーザー認証・管理
- X API統合
- AI分析エンジン（Groq AI）
- データ収集・分析
- スケジュール管理
"""

__version__ = "1.0.0"
__author__ = "X Research Team"
__email__ = "research@example.com"

# パッケージ情報
__all__ = [
    "main",
    "auth",
    "ai", 
    "core",
    "services"
]

# ログ設定
import logging

# バックエンド専用ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ハンドラーの設定（重複を避けるために確認）
if not logger.handlers:
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)

logger.info(f"X API研究・分析ツール バックエンド v{__version__} 初期化完了")