#!/usr/bin/env python3
"""
X API研究・分析ツール メイン起動スクリプト

このスクリプトはアプリケーション全体を起動・管理します。
バックエンド（FastAPI）とフロントエンド（React開発サーバー）の両方を管理できます。
"""

import asyncio
import os
import sys
import subprocess
import signal
import time
import logging
from pathlib import Path
from typing import Optional, List
import argparse

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ProcessManager:
    """プロセス管理クラス"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        
    def add_process(self, process: subprocess.Popen, name: str):
        """プロセスを管理リストに追加"""
        self.processes.append(process)
        logger.info(f"プロセス '{name}' (PID: {process.pid}) を開始しました")
        
    def terminate_all(self):
        """すべての管理プロセスを終了"""
        logger.info("すべてのプロセスを終了しています...")
        
        for process in self.processes:
            if process.poll() is None:  # プロセスが実行中の場合
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"プロセス {process.pid} の正常終了がタイムアウト。強制終了します。")
                    process.kill()
                except Exception as e:
                    logger.error(f"プロセス {process.pid} の終了中にエラー: {e}")
        
        self.processes.clear()
        logger.info("すべてのプロセスを終了しました")


def setup_directories():
    """必要なディレクトリを作成"""
    directories = [
        'data',
        'data/users',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"ディレクトリを作成/確認: {directory}")


def check_dependencies():
    """依存関係の確認"""
    logger.info("依存関係を確認しています...")
    
    # Python 3.9以上の確認
    if sys.version_info < (3, 9):
        logger.error("Python 3.9以上が必要です")
        return False
    
    # 必要なPythonパッケージの確認
    required_packages = ['fastapi', 'uvicorn', 'dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"不足しているパッケージ: {', '.join(missing_packages)}")
        logger.info("pip install -r requirements.txt を実行してください")
        return False
    
    # Node.js の確認（フロントエンド用）
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Node.js バージョン: {result.stdout.strip()}")
        else:
            logger.warning("Node.js が見つかりません。フロントエンドの起動はスキップされます。")
    except FileNotFoundError:
        logger.warning("Node.js が見つかりません。フロントエンドの起動はスキップされます。")
    
    logger.info("依存関係の確認完了")
    return True


def start_backend(process_manager: ProcessManager):
    """バックエンドサーバー（FastAPI）を起動"""
    logger.info("バックエンドサーバーを起動しています...")
    
    # 環境変数から設定を取得
    host = os.getenv('BACKEND_HOST', '127.0.0.1')
    port = int(os.getenv('BACKEND_PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # uvicornコマンドを構築
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'backend.main:app',
        '--host', host,
        '--port', str(port),
    ]
    
    if debug:
        cmd.extend(['--reload', '--log-level', 'debug'])
    
    try:
        process = subprocess.Popen(cmd, cwd=project_root)
        process_manager.backend_process = process
        process_manager.add_process(process, 'Backend')
        
        logger.info(f"バックエンドサーバー起動完了: http://{host}:{port}")
        logger.info(f"API ドキュメント: http://{host}:{port}/docs")
        
        return process
    except Exception as e:
        logger.error(f"バックエンドサーバーの起動に失敗: {e}")
        return None


def start_frontend(process_manager: ProcessManager):
    """フロントエンドサーバー（React）を起動"""
    frontend_dir = project_root / 'frontend'
    
    if not frontend_dir.exists():
        logger.warning("フロントエンドディレクトリが見つかりません")
        return None
    
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        logger.warning("package.json が見つかりません。フロントエンドをスキップします")
        return None
    
    logger.info("フロントエンドサーバーを起動しています...")
    
    try:
        # npm install の確認
        node_modules = frontend_dir / 'node_modules'
        if not node_modules.exists():
            logger.info("依存関係をインストールしています...")
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        
        # React開発サーバーを起動
        process = subprocess.Popen(
            ['npm', 'start'],
            cwd=frontend_dir,
            env={**os.environ, 'BROWSER': 'none'}  # ブラウザの自動起動を無効化
        )
        
        process_manager.frontend_process = process
        process_manager.add_process(process, 'Frontend')
        
        host = os.getenv('FRONTEND_HOST', '127.0.0.1')
        port = int(os.getenv('FRONTEND_PORT', 3000))
        logger.info(f"フロントエンドサーバー起動完了: http://{host}:{port}")
        
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"npm install に失敗: {e}")
        return None
    except Exception as e:
        logger.error(f"フロントエンドサーバーの起動に失敗: {e}")
        return None


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='X API研究・分析ツール')
    parser.add_argument('--backend-only', action='store_true', help='バックエンドのみ起動')
    parser.add_argument('--frontend-only', action='store_true', help='フロントエンドのみ起動')
    parser.add_argument('--no-deps-check', action='store_true', help='依存関係チェックをスキップ')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("X API研究・分析ツール 起動中...")
    logger.info("=" * 60)
    
    # 依存関係の確認
    if not args.no_deps_check and not check_dependencies():
        logger.error("依存関係の確認に失敗しました")
        sys.exit(1)
    
    # 必要なディレクトリの作成
    setup_directories()
    
    # プロセス管理インスタンス
    process_manager = ProcessManager()
    
    # シグナルハンドラーの設定
    def signal_handler(signum, frame):
        logger.info(f"シグナル {signum} を受信。アプリケーションを終了します...")
        process_manager.terminate_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # サーバー起動
        if not args.frontend_only:
            backend_process = start_backend(process_manager)
            if not backend_process:
                logger.error("バックエンドの起動に失敗しました")
                sys.exit(1)
        
        if not args.backend_only:
            frontend_process = start_frontend(process_manager)
            # フロントエンドの起動失敗は致命的エラーではない
        
        logger.info("=" * 60)
        logger.info("アプリケーション起動完了!")
        logger.info("Ctrl+C で終了")
        logger.info("=" * 60)
        
        # メインループ
        while True:
            time.sleep(1)
            
            # プロセスの生存確認
            for process in process_manager.processes[:]:  # コピーを作成してイテレート
                if process.poll() is not None:
                    logger.warning(f"プロセス {process.pid} が予期せず終了しました")
                    process_manager.processes.remove(process)
            
            # すべてのプロセスが終了した場合
            if not process_manager.processes:
                logger.warning("すべてのプロセスが終了しました")
                break
                
    except KeyboardInterrupt:
        logger.info("Ctrl+C が押されました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
    finally:
        process_manager.terminate_all()


if __name__ == '__main__':
    main()