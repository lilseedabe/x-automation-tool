-- 🔄 APIキーキャッシュ機能対応のためのデータベースマイグレーション
-- user_sessions テーブルに新しいカラムを追加

-- 既存テーブル確認
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'user_sessions'
);

-- api_keys_cached カラムが存在するかチェック
SELECT EXISTS (
    SELECT FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'user_sessions' 
    AND column_name = 'api_keys_cached'
);

-- api_cache_expires_at カラムが存在するかチェック
SELECT EXISTS (
    SELECT FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'user_sessions' 
    AND column_name = 'api_cache_expires_at'
);

-- 新しいカラムを追加（存在しない場合のみ）
DO $$
BEGIN
    -- api_keys_cached カラム追加
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'user_sessions' 
        AND column_name = 'api_keys_cached'
    ) THEN
        ALTER TABLE user_sessions 
        ADD COLUMN api_keys_cached BOOLEAN DEFAULT FALSE NOT NULL;
        
        RAISE NOTICE '✅ api_keys_cached カラムを追加しました';
    ELSE
        RAISE NOTICE '⚠️ api_keys_cached カラムは既に存在します';
    END IF;
    
    -- api_cache_expires_at カラム追加
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'user_sessions' 
        AND column_name = 'api_cache_expires_at'
    ) THEN
        ALTER TABLE user_sessions 
        ADD COLUMN api_cache_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;
        
        RAISE NOTICE '✅ api_cache_expires_at カラムを追加しました';
    ELSE
        RAISE NOTICE '⚠️ api_cache_expires_at カラムは既に存在します';
    END IF;
END $$;

-- 追加後の確認
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'user_sessions' 
AND column_name IN ('api_keys_cached', 'api_cache_expires_at')
ORDER BY column_name;

-- インデックス追加（パフォーマンス向上のため）
CREATE INDEX IF NOT EXISTS idx_user_sessions_api_cache_expires 
ON user_sessions(api_cache_expires_at) 
WHERE api_cache_expires_at IS NOT NULL;

RAISE NOTICE '🎯 マイグレーション完了！';