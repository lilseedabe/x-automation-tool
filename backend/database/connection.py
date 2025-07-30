"""
🗄️ X自動反応ツール - データベース接続管理
運営者ブラインド設計・PostgreSQL対応
"""

import os
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import asyncpg
from contextlib import asynccontextmanager

# ログ設定
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class DatabaseManager:
    """データベース接続管理クラス"""
    
    def __init__(self):
        self.async_engine = None
        self.async_session_maker = None
        self.sync_engine = None
        self.sync_session_maker = None
        self._initialized = False
    
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
    
    async def initialize(self):
        """データベース接続初期化"""
        if self._initialized:
            return
        
        try:
            # 非同期エンジン作成
            async_url = self.get_database_url(async_driver=True)
            self.async_engine = create_async_engine(
                async_url,
                poolclass=NullPool,  # VPS環境での接続プール最適化
                pool_pre_ping=True,
                pool_recycle=3600,
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
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # 同期セッションメーカー
            self.sync_session_maker = sessionmaker(
                bind=self.sync_engine,
                expire_on_commit=False
            )
            
            # 接続テスト
            await self.test_connection()
            
            self._initialized = True
            logger.info("📊 データベース接続初期化完了")
            
        except Exception as e:
            logger.error(f"❌ データベース接続初期化失敗: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """データベース接続テスト"""
        try:
            async with self.async_engine.begin() as conn:
                # text()でSQL文字列をラップ
                result = await conn.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
            if test_value == 1:
                logger.info("✅ データベース接続テスト成功")
                return True
            else:
                logger.error("❌ データベース接続テスト失敗")
                return False
                
        except Exception as e:
            logger.error(f"❌ データベース接続エラー: {str(e)}")
            return False
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """非同期セッション取得（コンテキストマネージャー）"""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
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
    await db_manager.initialize()

async def close_database():
    """アプリケーション終了時のDB接続クローズ"""
    await db_manager.close()

# 直接PostgreSQL接続（管理用）
class DirectPostgreSQLManager:
    """asyncpg直接接続管理（高パフォーマンス用）"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize_pool(self):
        """接続プール初期化"""
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "5432"))
        db_name = os.getenv("DB_NAME", "x_automation_db")
        db_user = os.getenv("DB_USER", "x_automation_user")
        db_password = os.getenv("DB_PASSWORD", "x_auto_secure_2025!")
        
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
            
        except Exception as e:
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

# ヘルスチェック関数
async def check_database_health() -> dict:
    """データベースヘルスチェック"""
    health_status = {
        "database": "unknown",
        "connection_test": False,
        "pool_status": "unknown",
        "response_time_ms": None
    }
    
    try:
        import time
        start_time = time.time()
        
        # SQLAlchemy接続テスト
        connection_ok = await db_manager.test_connection()
        health_status["connection_test"] = connection_ok
        
        # 応答時間計測
        response_time = (time.time() - start_time) * 1000
        health_status["response_time_ms"] = round(response_time, 2)
        
        # ステータス判定
        if connection_ok and response_time < 1000:
            health_status["database"] = "healthy"
        elif connection_ok:
            health_status["database"] = "slow"
        else:
            health_status["database"] = "unhealthy"
            
        # プール状態
        if direct_db.pool:
            health_status["pool_status"] = f"active ({direct_db.pool.get_size()} connections)"
        else:
            health_status["pool_status"] = "not_initialized"
            
    except Exception as e:
        health_status["database"] = "error"
        health_status["error"] = str(e)
        logger.error(f"❌ データベースヘルスチェックエラー: {str(e)}")
    
    return health_status

# クリーンアップタスク
async def cleanup_expired_data():
    """期限切れデータのクリーンアップ"""
    try:
        async with db_manager.get_session() as session:
            # text()でSQL文字列をラップ
            result = await session.execute(text("SELECT cleanup_expired_sessions()"))
            deleted_sessions = result.scalar()
            
            result = await session.execute(text("SELECT cleanup_old_logs()"))
            deleted_logs = result.scalar()
            
            logger.info(f"🧹 クリーンアップ完了: セッション{deleted_sessions}件, ログ{deleted_logs}件削除")
            
    except Exception as e:
        logger.error(f"❌ データクリーンアップエラー: {str(e)}")