#!/bin/bash

# 🐘 X自動反応ツール - PostgreSQL VPS セットアップスクリプト
# シンVPS Ubuntu 25.04 対応

set -e  # エラー時に停止

echo "🤖 X自動反応ツール - PostgreSQL VPS セットアップ開始"
echo "=================================================="

# 色付きメッセージ関数
function echo_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

function echo_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

function echo_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

function echo_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

# 前提条件チェック
echo_info "システム情報確認中..."
echo "OS: $(lsb_release -d | cut -f2)"
echo "メモリ: $(free -h | grep '^Mem:' | awk '{print $2}')"
echo "ディスク: $(df -h / | tail -1 | awk '{print $2}')"
echo "IPアドレス: $(hostname -I | awk '{print $1}')"

# 1. システム更新
echo_info "システムパッケージを更新中..."
apt update && apt upgrade -y
echo_success "システム更新完了"

# 2. PostgreSQL インストール
echo_info "PostgreSQL 16をインストール中..."
apt install -y postgresql postgresql-contrib postgresql-client
echo_success "PostgreSQL インストール完了"

# 3. PostgreSQL サービス開始・自動起動設定
echo_info "PostgreSQL サービス設定中..."
systemctl start postgresql
systemctl enable postgresql
echo_success "PostgreSQL サービス設定完了"

# 4. PostgreSQL バージョン確認
POSTGRES_VERSION=$(sudo -u postgres psql -c "SELECT version();" | head -3 | tail -1)
echo_success "PostgreSQL インストール確認: $POSTGRES_VERSION"

# 5. データベースとユーザー作成
echo_info "X自動反応ツール用データベース作成中..."

# PostgreSQL スーパーユーザーで実行
sudo -u postgres psql <<EOF
-- データベース作成
CREATE DATABASE x_automation_db 
    WITH ENCODING='UTF8' 
    LC_COLLATE='C' 
    LC_CTYPE='C';

-- アプリケーション用ユーザー作成
CREATE USER x_automation_user WITH PASSWORD 'x_auto_secure_2025!';

-- 権限付与
GRANT ALL PRIVILEGES ON DATABASE x_automation_db TO x_automation_user;

-- データベース所有者変更
ALTER DATABASE x_automation_db OWNER TO x_automation_user;

-- 接続確認
\l
\du
EOF

echo_success "データベースとユーザー作成完了"

# 6. PostgreSQL設定ファイル更新（外部接続許可）
echo_info "PostgreSQL外部接続設定中..."

# postgresql.conf 設定
POSTGRES_CONF="/etc/postgresql/16/main/postgresql.conf"
cp $POSTGRES_CONF ${POSTGRES_CONF}.backup

# 外部接続許可設定
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" $POSTGRES_CONF

# 軽量チューニング（1GB RAM対応）
cat >> $POSTGRES_CONF <<EOF

# X自動反応ツール 軽量チューニング（1GB RAM）
shared_buffers = 128MB
effective_cache_size = 512MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.7
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
max_worker_processes = 2
max_parallel_workers_per_gather = 1
max_parallel_workers = 2
max_parallel_maintenance_workers = 1
EOF

echo_success "postgresql.conf 設定完了"

# 7. pg_hba.conf 設定（認証方法）
echo_info "PostgreSQL認証設定中..."

PG_HBA_CONF="/etc/postgresql/16/main/pg_hba.conf"
cp $PG_HBA_CONF ${PG_HBA_CONF}.backup

# Render等外部からの接続許可（パスワード認証）
cat >> $PG_HBA_CONF <<EOF

# X自動反応ツール 外部接続許可
host    x_automation_db    x_automation_user    0.0.0.0/0    md5
host    x_automation_db    x_automation_user    ::/0         md5
EOF

echo_success "pg_hba.conf 設定完了"

# 8. ファイアウォール設定（UFW）
echo_info "ファイアウォール設定中..."

# UFW有効化（有効でない場合）
ufw --force enable

# PostgreSQLポート開放
ufw allow 5432/tcp
ufw allow ssh

# 設定確認
ufw status
echo_success "ファイアウォール設定完了"

# 9. PostgreSQL再起動
echo_info "PostgreSQL再起動中..."
systemctl restart postgresql
sleep 3

# サービス状態確認
systemctl status postgresql --no-pager -l
echo_success "PostgreSQL再起動完了"

# 10. 接続テスト
echo_info "データベース接続テスト中..."
sudo -u postgres psql -d x_automation_db -c "SELECT 'PostgreSQL接続成功!' as status;"
echo_success "データベース接続テスト成功"

# 11. セキュリティ設定
echo_info "セキュリティ強化設定中..."

# fail2ban インストール（ブルートフォース攻撃対策）
apt install -y fail2ban

# PostgreSQL用jail設定
cat > /etc/fail2ban/jail.d/postgresql.conf <<EOF
[postgresql]
enabled = true
port = 5432
filter = postgresql
logpath = /var/log/postgresql/postgresql-16-main.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

systemctl restart fail2ban
echo_success "セキュリティ設定完了"

# 12. 設定情報表示
echo ""
echo "=================================================="
echo_success "🎉 PostgreSQL VPS セットアップ完了！"
echo "=================================================="
echo ""
echo "📊 設定情報:"
echo "  データベース名: x_automation_db"
echo "  ユーザー名: x_automation_user"
echo "  パスワード: x_auto_secure_2025!"
echo "  ポート: 5432"
echo "  IPアドレス: $(hostname -I | awk '{print $1}')"
echo ""
echo "🔗 接続文字列（Render用）:"
echo "  postgresql://x_automation_user:x_auto_secure_2025!@$(hostname -I | awk '{print $1}'):5432/x_automation_db"
echo ""
echo "📋 次のステップ:"
echo "  1. Renderの環境変数 DATABASE_URL を上記接続文字列に設定"
echo "  2. FastAPIアプリでデータベーステーブル作成"
echo "  3. 接続テスト実行"
echo ""
echo_warning "⚠️  セキュリティ注意事項:"
echo "  - 本番環境では強力なパスワードに変更してください"
echo "  - 定期的なバックアップを設定してください"
echo "  - PostgreSQLのアップデートを定期実行してください"
echo ""
echo_success "セットアップスクリプト実行完了 🚀"