#!/usr/bin/env python3
"""
🔄 データベースマイグレーション実行スクリプト
APIキーキャッシュ機能のためのuser_sessionsテーブル更新
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# バックエンドディレクトリもパスに追加
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from backend.database.connection import db_manager, direct_db
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("カレントディレクトリでこのスクリプトを実行してください")
    sys.exit(1)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """マイグレーション実行"""
    try:
        print("🔄 データベースマイグレーション開始...")
        
        # データベース接続初期化
        await db_manager.initialize()
        
        # SQLファイル読み込み
        migration_file = project_root / "database_migration.sql"
        if not migration_file.exists():
            raise FileNotFoundError(f"マイグレーションファイルが見つかりません: {migration_file}")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("📄 マイグレーションSQL読み込み完了")
        
        # マイグレーション実行
        async with db_manager.get_session() as session:
            # SQLを行ごとに分割して実行（DO $$ブロック対応）
            sql_statements = []
            current_statement = ""
            in_do_block = False
            
            for line in migration_sql.split('\n'):
                line = line.strip()
                
                # コメント行をスキップ
                if line.startswith('--') or not line:
                    continue
                
                current_statement += line + "\n"
                
                # DO $$ブロック検出
                if line.startswith('DO $$'):
                    in_do_block = True
                elif line == '$$;' and in_do_block:
                    in_do_block = False
                    sql_statements.append(current_statement.strip())
                    current_statement = ""
                elif not in_do_block and line.endswith(';'):
                    sql_statements.append(current_statement.strip())
                    current_statement = ""
            
            # 残りのステートメントがあれば追加
            if current_statement.strip():
                sql_statements.append(current_statement.strip())
            
            print(f"📝 {len(sql_statements)}個のSQLステートメントを実行します")
            
            # 各ステートメントを実行
            for i, statement in enumerate(sql_statements, 1):
                if statement:
                    print(f"⚡ ステートメント {i} 実行中...")
                    try:
                        from sqlalchemy import text
                        result = await session.execute(text(statement))
                        
                        # 結果がある場合は表示
                        if result.returns_rows:
                            rows = result.fetchall()
                            for row in rows:
                                print(f"   📊 結果: {row}")
                        
                        await session.commit()
                        print(f"   ✅ ステートメント {i} 完了")
                        
                    except Exception as e:
                        print(f"   ⚠️ ステートメント {i} でエラー: {str(e)}")
                        await session.rollback()
                        # 既に存在するカラムの場合はエラーを無視
                        if "already exists" in str(e) or "duplicate column" in str(e):
                            print(f"   ℹ️ カラムは既に存在します（スキップ）")
                        else:
                            raise
        
        print("🎯 マイグレーション完了！")
        
        # 結果確認
        print("\n📋 マイグレーション結果確認:")
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            # テーブル構造確認
            result = await session.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'user_sessions' 
                AND column_name IN ('api_keys_cached', 'api_cache_expires_at')
                ORDER BY column_name
            """))
            
            columns = result.fetchall()
            if columns:
                print("✅ 新しいカラムが正常に追加されました:")
                for col in columns:
                    print(f"   • {col[0]} ({col[1]}, nullable: {col[2]}, default: {col[3]})")
            else:
                print("❌ 新しいカラムが見つかりません")
        
    except Exception as e:
        logger.error(f"❌ マイグレーションエラー: {str(e)}")
        raise
    finally:
        # データベース接続クローズ
        await db_manager.close()

def main():
    """メイン関数"""
    print("🚀 X自動反応ツール - データベースマイグレーション")
    print("=" * 50)
    
    try:
        # 環境変数チェック
        required_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ 必要な環境変数が設定されていません: {', '.join(missing_vars)}")
            print("以下の環境変数を設定してください:")
            for var in missing_vars:
                print(f"   export {var}=<値>")
            sys.exit(1)
        
        # マイグレーション実行
        asyncio.run(run_migration())
        print("\n🎉 マイグレーション正常完了！")
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()