"""
🗄️ X自動反応ツール - データベース接続管理（完成版）
運営者ブラインド設計・PostgreSQL対応・Render最適化
"""

import os
import logging
import asyncio
import time
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
import asyncpg
from contextlib import asynccontextmanager

# ログ設定
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class DatabaseManager:
    """データベース接続管理クラス（完成版）"""
    
    def __init__(self):
        self.async_engine = None
        self.async_session_maker = None
        self.sync_engine = None
        self.sync_session_maker = None
        self._initialized = False
        self.max_retries = 5
        self.retry_delay = 2  # 基本待機時間（秒）
        self.connection_timeout = 30
    
    def get_database_url(self, async_driver: bool = True) -> str:
        """データベースURL取得"""
        # 環境変数から接続情報取得
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "x_automation_db")
        db_user = os.getenv("DB_USER", "x_automation_user")
        db_password = os.getenv("DB_PASSWORD", "x_auto_secure_2025!")
        
        # 従来のDATABASE_URL環境変数も対応
        if database_url := os.getenv("DATABASE_URL"):
            if async_driver and not database_url.startswith("postgresql+asyncpg://"):
                # 非同期用に変換
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            elif not async_driver and database_url.startswith("postgresql+asyncpg://"):
                # 同期用に変換
                database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            return database_url
        
        # 個別環境変数から構築
        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        return f"{driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    async def _test_connection_with_retry(self) -> bool:
        """接続テスト（リトライ機能付き）"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"🔌 データベース接続テスト (試行 {attempt}/{self.max_retries})")
                
                # 接続テスト実行
                async with self.async_engine.begin() as conn:
                    result = await conn.execute(text("SELECT 1 as test"))
                    test_value = result.scalar()
                
                if test_value == 1:
                    logger.info(f"✅ データベース接続成功 (試行 {attempt})")
                    return True
                else:
                    logger.warning(f"⚠️ 接続テスト異常値: {test_value}")
                    last_error = f"Unexpected test result: {test_value}"
                    
            except (OperationalError, DisconnectionError) as e:
                last_error = str(e)
                logger.warning(f"⚠️ 試行 {attempt} 失敗 (接続エラー): {str(e)}")
                
                # 接続エラーの詳細分析
                if "could not connect to server" in str(e).lower():
                    logger.info("🔄 VPSデータベースサーバーへの接続を再試行中...")
                elif "timeout" in str(e).lower():
                    logger.info("⏱️ 接続タイムアウト - 再試行中...")
                elif "connection refused" in str(e).lower():
                    logger.warning("🚫 接続拒否 - VPSのファイアウォール設定を確認してください")
                
            except SQLAlchemyError as e:
                last_error = str(e)
                logger.warning(f"⚠️ 試行 {attempt} 失敗 (SQLAlchemyエラー): {str(e)}")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ 試行 {attempt} 失敗 (予期しないエラー): {str(e)}")
            
            # 最後の試行でない場合は待機
            if attempt < self.max_retries:
                wait_time = self.retry_delay * attempt  # 段階的に待機時間を増加
                logger.info(f"⏳ {wait_time}秒後に再試行...")
                await asyncio.sleep(wait_time)
        
        # すべての試行が失敗した場合
        logger.error(f"❌ すべての接続試行が失敗しました。最後のエラー: {last_error}")
        return False
    
    async def initialize(self):
        """データベース接続初期化（完成版）"""
        if self._initialized:
            logger.info("📊 データベースは既に初期化済みです")
            return
        
        start_time = time.time()
        logger.info("🗄️ データベース接続初期化開始...")
        
        try:
            # 接続URL取得とログ出力
            async_url = self.get_database_url(async_driver=True)
            logger.info(f"🔗 接続先: {async_url.split('@')[1] if '@' in async_url else 'localhost'}")
            
            # 非同期エンジン作成（Render + VPS環境最適化）
            self.async_engine = create_async_engine(
                async_url,
                poolclass=NullPool,  # VPS環境での接続プール最適化
                connect_args={
                    "server_settings": {
                        "application_name": "x_automation_tool_render",
                        "jit": "off"  # パフォーマンス最適化
                    },
                    "command_timeout": self.connection_timeout
                },
                echo=os.getenv("DB_DEBUG", "false").lower() == "true"
            )
            
            # 非同期セッションメーカー
            self.async_session_maker = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 同期エンジン（管理用）
            sync_url = self.get_database_url(async_driver=False)
            self.sync_engine = create_engine(
                sync_url,
                poolclass=NullPool,
                connect_args={
                    "application_name": "x_automation_tool_sync",
                    "connect_timeout": self.connection_timeout
                }
            )
            
            # 同期セッションメーカー
            self.sync_session_maker = sessionmaker(
                bind=self.sync_engine,
                expire_on_commit=False
            )
            
            # 接続テスト（リトライ機能付き）
            logger.info("🔍 データベース接続テスト開始...")
            connection_success = await self._test_connection_with_retry()
            
            if connection_success:
                self._initialized = True
                elapsed_time = time.time() - start_time
                logger.info(f"✅ データベース接続初期化完了 ({elapsed_time:.2f}秒)")
                
                # 接続情報をログ出力
                await self._log_connection_info()
            else:
                raise Exception("データベース接続テストに失敗しました")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ データベース接続初期化失敗 ({elapsed_time:.2f}秒): {str(e)}")
            
            # デバッグ情報の出力
            await self._log_debug_info()
            raise
    
    async def _log_connection_info(self):
        """接続情報をログ出力"""
        try:
            async with self.async_engine.begin() as conn:
                # PostgreSQLバージョン確認
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"📊 PostgreSQL: {version.split(',')[0] if version else 'Unknown'}")
                
                # 接続数確認
                result = await conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
                connections = result.scalar()
                logger.info(f"🔗 アクティブ接続数: {connections}")
                
        except Exception as e:
            logger.warning(f"⚠️ 接続情報取得失敗: {str(e)}")
    
    async def _log_debug_info(self):
        """デバッグ情報をログ出力"""
        logger.error("🔍 デバッグ情報:")
        logger.error(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
        logger.error(f"  DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
        logger.error(f"  DB_PORT: {os.getenv('DB_PORT', 'Not set')}")
        logger.error(f"  DB_NAME: {os.getenv('DB_NAME', 'Not set')}")
        logger.error(f"  DB_USER: {os.getenv('DB_USER', 'Not set')}")
        logger.error(f"  Environment: {os.getenv('RENDER', 'Not Render') if os.getenv('RENDER') else 'Local'}")
        logger.error(f"  APP_ENV: {os.getenv('APP_ENV', 'Not set')}")
    
    async def test_connection(self) -> bool:
        """データベース接続テスト（公開メソッド）"""
        if not self._initialized:
            logger.info("🔄 データベース未初期化 - 初期化を実行中...")
            await self.initialize()
        
        return await self._test_connection_with_retry()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """非同期セッション取得（コンテキストマネージャー）"""
        if not self._initialized:
            await self.initialize()
        
        session = None
        try:
            session = self.async_session_maker()
            yield session
            await session.commit()
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"❌ セッションエラー: {str(e)}")
            raise
        finally:
            if session:
                await session.close()
    
    def get_sync_session(self):
        """同期セッション取得"""
        if not self.sync_session_maker:
            # 同期エンジン初期化
            sync_url = self.get_database_url(async_driver=False)
            self.sync_engine = create_engine(sync_url)
            self.sync_session_maker = sessionmaker(bind=self.sync_engine)
        
        return self.sync_session_maker()
    
    async def close(self):
        """データベース接続クローズ"""
        logger.info("🔄 データベース接続をクローズ中...")
        
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        
        self._initialized = False
        logger.info("📊 データベース接続をクローズしました")

# グローバルインスタンス
db_manager = DatabaseManager()

# 便利関数
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependencyで使用するDBセッション取得"""
    async with db_manager.get_session() as session:
        yield session

async def init_database():
    """アプリケーション起動時のDB初期化"""
    try:
        await db_manager.initialize()
    except Exception as e:
        logger.error(f"❌ データベース初期化エラー: {str(e)}")
        raise

async def close_database():
    """アプリケーション終了時のDB接続クローズ"""
    await db_manager.close()

# 直接PostgreSQL接続（管理用）
class DirectPostgreSQLManager:
    """asyncpg直接接続管理（高パフォーマンス用）"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.max_retries = 3
    
    async def initialize_pool(self):
        """接続プール初期化（リトライ対応）"""
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "5432"))
        db_name = os.getenv("DB_NAME", "x_automation_db")
        db_user = os.getenv("DB_USER", "x_automation_user")
        db_password = os.getenv("DB_PASSWORD", "x_auto_secure_2025!")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.pool = await asyncpg.create_pool(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password,
                    min_size=1,
                    max_size=5,  # VPS 1GBメモリ対応
                    command_timeout=60
                )
                logger.info("🏊 asyncpg接続プール初期化完了")
                return
                
            except Exception as e:
                logger.warning(f"⚠️ asyncpg接続プール初期化失敗 (試行 {attempt}): {str(e)}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 * attempt)
                else:
                    logger.error(f"❌ asyncpg接続プール初期化失敗: {str(e)}")
                    raise
    
    @asynccontextmanager
    async def get_connection(self):
        """直接接続取得"""
        if not self.pool:
            await self.initialize_pool()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args):
        """クエリ実行"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_command(self, command: str, *args):
        """コマンド実行"""
        async with self.get_connection() as conn:
            return await conn.execute(command, *args)
    
    async def close_pool(self):
        """接続プールクローズ"""
        if self.pool:
            await self.pool.close()
            logger.info("🏊 asyncpg接続プールをクローズしました")

# 直接接続マネージャーインスタンス
direct_db = DirectPostgreSQLManager()

# ヘルスチェック関数（改善版）
async def check_database_health() -> dict:
    """データベースヘルスチェック（詳細版）"""
    health_status = {
        "database": "unknown",
        "connection_test": False,
        "pool_status": "unknown",
        "response_time_ms": None,
        "last_error": None,
        "retry_count": 0
    }
    
    try:
        start_time = time.time()
        
        # 接続テスト
        connection_ok = await db_manager.test_connection()
        health_status["connection_test"] = connection_ok
        
        # 応答時間計測
        response_time = (time.time() - start_time) * 1000
        health_status["response_time_ms"] = round(response_time, 2)
        
        # ステータス判定
        if connection_ok:
            if response_time < 1000:
                health_status["database"] = "healthy"
            elif response_time < 5000:
                health_status["database"] = "slow"
            else:
                health_status["database"] = "very_slow"
        else:
            health_status["database"] = "unhealthy"
            
        # プール状態
        if direct_db.pool:
            health_status["pool_status"] = f"active ({direct_db.pool.get_size()} connections)"
        else:
            health_status["pool_status"] = "not_initialized"
            
    except Exception as e:
        health_status["database"] = "error"
        health_status["last_error"] = str(e)
        logger.error(f"❌ データベースヘルスチェックエラー: {str(e)}")
    
    return health_status

# クリーンアップタスク（エラーハンドリング強化）
async def cleanup_expired_data():
    """期限切れデータのクリーンアップ"""
    try:
        async with db_manager.get_session() as session:
            # 期限切れセッション削除
            try:
                result = await session.execute(text("SELECT cleanup_expired_sessions()"))
                deleted_sessions = result.scalar() or 0
            except Exception:
                deleted_sessions = 0
                logger.warning("⚠️ セッションクリーンアップ関数が存在しません")
            
            # 古いログ削除
            try:
                result = await session.execute(text("SELECT cleanup_old_logs()"))
                deleted_logs = result.scalar() or 0
            except Exception:
                deleted_logs = 0
                logger.warning("⚠️ ログクリーンアップ関数が存在しません")
            
            logger.info(f"🧹 クリーンアップ完了: セッション{deleted_sessions}件, ログ{deleted_logs}件削除")
            
    except Exception as e:
        logger.error(f"❌ データクリーンアップエラー: {str(e)}")

# 接続状態監視
async def monitor_connection():
    """接続状態の定期監視"""
    while True:
        try:
            health = await check_database_health()
            if health["database"] != "healthy":
                logger.warning(f"⚠️ データベース状態: {health['database']}")
            
            await asyncio.sleep(300)  # 5分ごとに監視
            
        except Exception as e:
            logger.error(f"❌ 接続監視エラー: {str(e)}")
            await asyncio.sleep(60)  # エラー時は1分後に再試行
