# 🚀 シンVPS - X自動反応ツール PostgreSQL セットアップ手順

## 📋 前提条件確認

✅ **VPS情報**
- OS: Ubuntu 25.04
- メモリ: 1GB  
- vCPU: 1コア
- ストレージ: 30GB SSD
- IPアドレス: 162.43.72.xxx

## 🔐 Step 1: VPSにSSHログイン

### 1-1. SSH接続
```bash
# あなたのPCから実行
ssh root@162.43.72.XXX
```

> ⚠️ 初回ログイン時は、シンVPS管理画面で「rootパスワード」を確認してください

### 1-2. 接続確認
```bash
# VPS内で実行 - システム情報確認
uname -a
free -h
df -h
```

## 📦 Step 2: セットアップファイルのダウンロード

### 2-1. 作業ディレクトリ作成
```bash
# VPS内で実行
mkdir -p /opt/x-automation-setup
cd /opt/x-automation-setup
```

### 2-2. GitHubからファイル取得
```bash
# VPS内で実行
wget https://raw.githubusercontent.com/lilseedabe/x-automation-tool/main/vps-setup/01-postgresql-setup.sh
wget https://raw.githubusercontent.com/lilseedabe/x-automation-tool/main/vps-setup/02-database-schema.sql

# 実行権限付与
chmod +x 01-postgresql-setup.sh
```

## 🐘 Step 3: PostgreSQL自動セットアップ実行

### 3-1. メインセットアップ実行
```bash
# VPS内で実行
./01-postgresql-setup.sh
```

> このスクリプトで以下が自動実行されます：
> - PostgreSQL 16インストール
> - データベース・ユーザー作成
> - 外部接続設定
> - セキュリティ設定
> - 軽量チューニング

### 3-2. 実行結果の確認
セットアップ完了後、以下の情報が表示されます：

```
🎉 PostgreSQL VPS セットアップ完了！
================================================
📊 設定情報:
  データベース名: x_automation_db
  ユーザー名: x_automation_user  
  パスワード: x_auto_secure_2025!
  ポート: 5432
  IPアドレス: 162.43.72.XXX

🔗 接続文字列（Render用）:
  postgresql://x_automation_user:x_auto_secure_2025!@162.43.72.XXX:5432/x_automation_db
```

## 🗄️ Step 4: データベーススキーマ作成

### 4-1. スキーマ適用
```bash
# VPS内で実行
sudo -u postgres psql -d x_automation_db -f 02-database-schema.sql
```

### 4-2. テーブル作成確認
```bash
# VPS内で実行
sudo -u postgres psql -d x_automation_db -c "\dt"
```

以下のテーブルが作成されていれば成功：
- users
- user_api_keys
- automation_settings
- action_queue
- user_blacklist
- activity_logs
- user_sessions
- system_settings

## 🔗 Step 5: Render側の設定

### 5-1. Render環境変数設定
Renderのダッシュボードで以下の環境変数を設定：

```bash
# データベース接続（VPS）
DATABASE_URL=postgresql://x_automation_user:x_auto_secure_2025!@162.43.72.XXX:5432/x_automation_db

# またはindividual設定
DB_HOST=162.43.72.XXX
DB_PORT=5432
DB_NAME=x_automation_db
DB_USER=x_automation_user
DB_PASSWORD=x_auto_secure_2025!

# その他必須環境変数
SECRET_KEY=your_32_character_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
APP_ENV=production
```

### 5-2. Render再デプロイ
環境変数設定後、Manual Deployを実行

## ✅ Step 6: 接続テスト

### 6-1. VPS側でのテスト
```bash
# VPS内で実行 - 外部からの接続許可確認
sudo netstat -plnt | grep 5432
sudo ufw status

# データベース接続テスト
psql postgresql://x_automation_user:x_auto_secure_2025!@localhost:5432/x_automation_db -c "SELECT 'Connection successful!' as status;"
```

### 6-2. Render側でのテスト
Renderアプリの以下エンドポイントにアクセス：
- `https://your-app.onrender.com/api/system/health`

レスポンスで `"database": "healthy"` が表示されれば成功

## 🛡️ Step 7: セキュリティ強化（推奨）

### 7-1. パスワード変更
```bash
# VPS内で実行 - より強力なパスワードに変更
sudo -u postgres psql -c "ALTER USER x_automation_user PASSWORD 'your_super_secure_password_2025!';"
```

### 7-2. ファイアウォール確認
```bash
# VPS内で実行
sudo ufw status verbose
```

### 7-3. fail2ban確認
```bash
# VPS内で実行
sudo systemctl status fail2ban
sudo fail2ban-client status postgresql
```

## 📊 Step 8: 監視・メンテナンス設定

### 8-1. 自動バックアップ設定
```bash
# VPS内で実行 - 日次バックアップスクリプト作成
cat > /opt/x-automation-setup/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/x-automation-backup"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U x_automation_user -d x_automation_db > "$BACKUP_DIR/x_automation_backup_$DATE.sql"

# 7日以上古いバックアップ削除
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

chmod +x /opt/x-automation-setup/backup.sh

# Cron設定（毎日午前3時）
echo "0 3 * * * /opt/x-automation-setup/backup.sh" | crontab -
```

### 8-2. ログ監視設定
```bash
# VPS内で実行
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

## 🚨 トラブルシューティング

### Q1: PostgreSQLが起動しない
```bash
# サービス状態確認
sudo systemctl status postgresql

# ログ確認
sudo journalctl -u postgresql -f

# 再起動
sudo systemctl restart postgresql
```

### Q2: 外部から接続できない
```bash
# 設定ファイル確認
sudo cat /etc/postgresql/16/main/postgresql.conf | grep listen_addresses
sudo cat /etc/postgresql/16/main/pg_hba.conf | tail -5

# ポート確認
sudo netstat -plnt | grep 5432
sudo ufw status | grep 5432
```

### Q3: Renderから接続できない
1. VPS IPアドレス確認: `hostname -I`
2. Render環境変数の接続文字列確認
3. Renderのログでエラー詳細確認

## 📈 パフォーマンス最適化

### メモリ使用量確認
```bash
# VPS内で実行
sudo -u postgres psql -c "
SELECT 
    setting, 
    unit,
    source 
FROM pg_settings 
WHERE name IN (
    'shared_buffers', 
    'effective_cache_size', 
    'work_mem',
    'maintenance_work_mem'
);"
```

### 接続数監視
```bash
# VPS内で実行
sudo -u postgres psql -c "
SELECT 
    count(*) as active_connections,
    max_conn.setting as max_connections
FROM pg_stat_activity psa
JOIN pg_settings max_conn ON max_conn.name = 'max_connections'
GROUP BY max_conn.setting;"
```

## 🎉 セットアップ完了

✅ PostgreSQL VPS環境構築完了
✅ Render連携設定完了  
✅ セキュリティ設定完了
✅ 運営者ブラインド暗号化対応

これで、X自動反応ツールのユーザーアカウントとAPIキーを安全に管理するデータベース環境が完成しました！

---

## 📞 サポート

問題が発生した場合は、以下の情報を収集してください：

1. VPS システム情報: `uname -a && free -h`
2. PostgreSQL ログ: `/var/log/postgresql/postgresql-16-main.log`
3. Render ログ: アプリのログ画面
4. エラーメッセージの詳細

継続的な運用のため、定期的なバックアップとセキュリティアップデートを実行してください。