-- 🗄️ X自動反応ツール - データベーススキーマ
-- 運営者ブラインド設計・プライバシー重視

-- ===================================================================
-- 🔐 拡張機能の有効化
-- ===================================================================

-- UUID生成用
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 暗号化関数用
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===================================================================
-- 🏗️ ユーザー管理テーブル
-- ===================================================================

-- ユーザーアカウントテーブル
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcryptハッシュ
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- メタデータ
    registration_ip VARCHAR(45), -- IPv6対応（INET → VARCHAR）
    user_agent TEXT,
    
    -- 設定
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    language VARCHAR(10) DEFAULT 'ja',
    
    -- 制約
    CONSTRAINT users_username_length CHECK (length(username) >= 3),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ユーザーテーブルのインデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ===================================================================
-- 🔑 APIキー管理テーブル（運営者ブラインド設計）
-- ===================================================================

-- X APIキー暗号化保存テーブル
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 暗号化されたAPIキー（運営者は復号不可）
    encrypted_api_key BYTEA NOT NULL,
    encrypted_api_secret BYTEA NOT NULL,
    encrypted_access_token BYTEA NOT NULL,
    encrypted_access_token_secret BYTEA NOT NULL,
    
    -- キー派生情報（ユーザーパスワードベース）
    key_salt BYTEA NOT NULL, -- ユーザー固有のソルト
    encryption_algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    
    -- メタデータ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE,
    
    -- X API情報
    x_username VARCHAR(50),
    x_user_id VARCHAR(50),
    api_permissions TEXT[], -- ['read', 'write', 'direct_messages']
    
    -- ステータス
    is_active BOOLEAN DEFAULT true,
    is_valid BOOLEAN DEFAULT true, -- API検証結果
    last_validation TIMESTAMP WITH TIME ZONE,
    
    -- 使用統計
    usage_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    CONSTRAINT unique_user_api_key UNIQUE(user_id)
);

-- APIキーテーブルのインデックス
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX idx_user_api_keys_is_active ON user_api_keys(is_active);
CREATE INDEX idx_user_api_keys_last_used ON user_api_keys(last_used);

-- ===================================================================
-- 🎯 自動化設定テーブル
-- ===================================================================

-- ユーザー自動化設定
CREATE TABLE automation_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 基本設定
    is_enabled BOOLEAN DEFAULT false,
    automation_mode VARCHAR(20) DEFAULT 'conservative', -- 'conservative', 'balanced', 'aggressive'
    
    -- いいね設定
    auto_like_enabled BOOLEAN DEFAULT true,
    like_daily_limit INTEGER DEFAULT 100,
    like_hourly_limit INTEGER DEFAULT 20,
    like_min_interval_minutes INTEGER DEFAULT 3,
    like_max_interval_minutes INTEGER DEFAULT 15,
    
    -- リポスト設定
    auto_repost_enabled BOOLEAN DEFAULT false,
    repost_daily_limit INTEGER DEFAULT 20,
    repost_hourly_limit INTEGER DEFAULT 5,
    repost_min_interval_minutes INTEGER DEFAULT 10,
    repost_max_interval_minutes INTEGER DEFAULT 60,
    
    -- AI分析設定
    ai_analysis_enabled BOOLEAN DEFAULT true,
    minimum_engagement_score INTEGER DEFAULT 50, -- 0-100
    target_keywords TEXT[],
    exclude_keywords TEXT[],
    
    -- 安全設定
    enable_blacklist BOOLEAN DEFAULT true,
    enable_rate_limiting BOOLEAN DEFAULT true,
    enable_human_like_timing BOOLEAN DEFAULT true,
    
    -- スケジュール設定
    active_hours_start TIME DEFAULT '09:00:00',
    active_hours_end TIME DEFAULT '22:00:00',
    active_days INTEGER[] DEFAULT '{1,2,3,4,5,6,7}', -- 月曜=1
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_automation UNIQUE(user_id)
);

-- 自動化設定のインデックス
CREATE INDEX idx_automation_settings_user_id ON automation_settings(user_id);
CREATE INDEX idx_automation_settings_is_enabled ON automation_settings(is_enabled);

-- ===================================================================
-- 📋 アクションキューテーブル
-- ===================================================================

-- 実行待ちアクション
CREATE TABLE action_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- アクション詳細
    action_type VARCHAR(20) NOT NULL, -- 'like', 'repost', 'reply'
    target_post_id VARCHAR(50) NOT NULL,
    target_user_id VARCHAR(50) NOT NULL,
    target_username VARCHAR(50),
    
    -- スケジューリング
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE,
    
    -- ステータス
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executing', 'completed', 'failed', 'cancelled'
    
    -- 結果
    result JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- AI分析結果
    ai_score INTEGER, -- 0-100
    ai_reasoning TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- アクションキューのインデックス
CREATE INDEX idx_action_queue_user_id ON action_queue(user_id);
CREATE INDEX idx_action_queue_status ON action_queue(status);
CREATE INDEX idx_action_queue_scheduled_at ON action_queue(scheduled_at);
CREATE INDEX idx_action_queue_action_type ON action_queue(action_type);

-- ===================================================================
-- 🚫 ブラックリストテーブル
-- ===================================================================

-- ユーザーブラックリスト
CREATE TABLE user_blacklist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- ブラックリスト対象
    blocked_user_id VARCHAR(50),
    blocked_username VARCHAR(50),
    blocked_keyword VARCHAR(255),
    
    -- 種別
    block_type VARCHAR(20) NOT NULL, -- 'user', 'keyword', 'domain'
    
    -- 理由
    reason VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT blacklist_target_check CHECK (
        (block_type = 'user' AND blocked_user_id IS NOT NULL) OR
        (block_type = 'keyword' AND blocked_keyword IS NOT NULL)
    )
);

-- ブラックリストのインデックス
CREATE INDEX idx_user_blacklist_user_id ON user_blacklist(user_id);
CREATE INDEX idx_user_blacklist_block_type ON user_blacklist(block_type);
CREATE INDEX idx_user_blacklist_blocked_user_id ON user_blacklist(blocked_user_id);

-- ===================================================================
-- 📊 活動ログテーブル
-- ===================================================================

-- アクション実行履歴
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- アクション詳細
    action_type VARCHAR(20) NOT NULL,
    target_post_id VARCHAR(50),
    target_user_id VARCHAR(50),
    target_username VARCHAR(50),
    
    -- 結果
    success BOOLEAN NOT NULL,
    response_data JSONB,
    error_message TEXT,
    
    -- タイミング
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    
    -- 分析データ
    ai_score INTEGER,
    engagement_result JSONB -- いいね数、リプライ数など
);

-- 活動ログのインデックス
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_executed_at ON activity_logs(executed_at);
CREATE INDEX idx_activity_logs_action_type ON activity_logs(action_type);
CREATE INDEX idx_activity_logs_success ON activity_logs(success);

-- ===================================================================
-- 🔒 セッション管理テーブル
-- ===================================================================

-- ユーザーセッション
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- セッション情報
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    
    -- 有効期限
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- クライアント情報
    ip_address VARCHAR(45), -- IPv6対応（INET → VARCHAR）
    user_agent TEXT,
    
    -- ステータス
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- セッションテーブルのインデックス
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- ===================================================================
-- 🔧 システム設定テーブル
-- ===================================================================

-- アプリケーション設定
CREATE TABLE system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 初期システム設定
INSERT INTO system_settings (key, value, description) VALUES 
('app_version', '1.0.0', 'アプリケーションバージョン'),
('maintenance_mode', 'false', 'メンテナンスモード'),
('max_users_per_day', '100', '1日あたり新規ユーザー上限'),
('default_daily_like_limit', '100', 'デフォルト1日いいね上限'),
('ai_analysis_enabled', 'true', 'AI分析機能有効フラグ'),
('operator_blind_mode', 'true', '運営者ブラインドモード');

-- ===================================================================
-- 🔄 トリガー・関数定義
-- ===================================================================

-- updated_atの自動更新関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにupdated_atトリガーを設定
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_api_keys_updated_at BEFORE UPDATE ON user_api_keys 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_automation_settings_updated_at BEFORE UPDATE ON automation_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_queue_updated_at BEFORE UPDATE ON action_queue 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 📈 統計ビュー
-- ===================================================================

-- ユーザー統計ビュー
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.created_at as user_since,
    COUNT(al.id) as total_actions,
    COUNT(al.id) FILTER (WHERE al.success = true) as successful_actions,
    COUNT(al.id) FILTER (WHERE al.action_type = 'like') as total_likes,
    COUNT(al.id) FILTER (WHERE al.action_type = 'repost') as total_reposts,
    MAX(al.executed_at) as last_action,
    CASE 
        WHEN COUNT(al.id) > 0 
        THEN ROUND((COUNT(al.id) FILTER (WHERE al.success = true)::numeric / COUNT(al.id)) * 100, 2)
        ELSE 0 
    END as success_rate_percent
FROM users u
LEFT JOIN activity_logs al ON u.id = al.user_id
GROUP BY u.id, u.username, u.created_at;

-- ===================================================================
-- 🔐 セキュリティ設定
-- ===================================================================

-- RLS (Row Level Security) の有効化
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_blacklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- ===================================================================
-- 🧹 クリーンアップジョブ用関数
-- ===================================================================

-- 期限切れセッション削除
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP OR is_active = false;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE 'plpgsql';

-- 古いログデータ削除（90日以前）
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM activity_logs 
    WHERE executed_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE 'plpgsql';

-- ===================================================================
-- ✅ スキーマ作成完了メッセージ
-- ===================================================================

DO $$
BEGIN
    RAISE NOTICE '🎉 X自動反応ツール データベーススキーマ作成完了!';
    RAISE NOTICE '📊 作成されたテーブル:';
    RAISE NOTICE '   - users (ユーザーアカウント)';
    RAISE NOTICE '   - user_api_keys (暗号化APIキー)';
    RAISE NOTICE '   - automation_settings (自動化設定)';
    RAISE NOTICE '   - action_queue (アクションキュー)';
    RAISE NOTICE '   - user_blacklist (ブラックリスト)';
    RAISE NOTICE '   - activity_logs (活動履歴)';
    RAISE NOTICE '   - user_sessions (セッション管理)';
    RAISE NOTICE '   - system_settings (システム設定)';
    RAISE NOTICE '🔐 セキュリティ機能:';
    RAISE NOTICE '   - 運営者ブラインド暗号化';
    RAISE NOTICE '   - Row Level Security';
    RAISE NOTICE '   - 自動クリーンアップ';
    RAISE NOTICE '✅ PostgreSQL VPS + SQLAlchemy 互換性対応完了!';
END;
$$;