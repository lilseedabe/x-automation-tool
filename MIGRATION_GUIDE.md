# 🔄 データベースマイグレーションガイド

## 概要

APIキー永続化問題を解決するため、`user_sessions`テーブルに新しいカラムを追加するマイグレーションです。

### 追加されるカラム
- `api_keys_cached` (BOOLEAN): APIキーがキャッシュされているかのフラグ
- `api_cache_expires_at` (TIMESTAMP WITH TIME ZONE): キャッシュの有効期限

## 🚀 VPSでの実行手順

### 1. SSHでVPSにログイン
```bash
ssh root@your-vps-ip
```

### 2. プロジェクトディレクトリに移動
```bash
cd /path/to/x-automation-tool
```

### 3. 最新コードを取得
```bash
git pull origin main
```

### 4. マイグレーション実行権限を付与
```bash
chmod +x migrate-database.sh
```

### 5. マイグレーション実行
```bash
./migrate-database.sh
```

### 6. サービス再起動
```bash
# systemdの場合
sudo systemctl restart x-automation-tool

# supervisorの場合
sudo supervisorctl restart x-automation-tool

# PM2の場合
pm2 restart x-automation-tool
```

## 🛠️ 手動実行（Pythonスクリプト）

シェルスクリプトが使えない場合：

```bash
# 1. 仮想環境アクティブ化（必要に応じて）
source venv/bin/activate  # または source .venv/bin/activate

# 2. 環境変数確認
echo $DB_HOST $DB_NAME $DB_USER

# 3. マイグレーション実行
python run_migration.py
```

## 🗄️ 直接SQL実行（PostgreSQL）

データベースに直接接続して実行する場合：

```bash
# 1. PostgreSQLに接続
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# 2. SQLファイルを実行
\i database_migration.sql

# 3. 結果確認
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'user_sessions' 
AND column_name IN ('api_keys_cached', 'api_cache_expires_at')
ORDER BY column_name;
```

## ✅ マイグレーション成功確認

### 1. ログイン動作確認
- ブラウザでログインページにアクセス
- 既存のユーザーでログイン
- エラーが発生しないことを確認

### 2. APIキーキャッシュ機能確認
- ログイン後、ユーザー設定でAPIキーが表示されること
- ログアウト後、再ログインでAPIキーが保持されること

### 3. データベース確認
```sql
-- 新しいカラムの存在確認
\d user_sessions

-- キャッシュデータの確認
SELECT id, user_id, api_keys_cached, api_cache_expires_at 
FROM user_sessions 
WHERE api_keys_cached = true 
LIMIT 5;
```

## 🔧 トラブルシューティング

### エラー1: `column "api_keys_cached" already exists`
**解決策**: このエラーは無害です。カラムが既に存在するため、マイグレーションは自動的にスキップされます。

### エラー2: `Connection refused`
**原因**: データベース接続設定が正しくない
**解決策**: 
```bash
# 環境変数を確認
echo $DATABASE_URL
echo $DB_HOST $DB_PORT $DB_NAME $DB_USER

# .env.productionファイルを確認
cat .env.production
```

### エラー3: `Permission denied`
**原因**: データベースユーザーの権限不足
**解決策**: 
```sql
-- PostgreSQLで権限付与
GRANT ALL PRIVILEGES ON TABLE user_sessions TO your_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO your_user;
```

### エラー4: `ImportError: No module named`
**原因**: 必要なPythonライブラリがインストールされていない
**解決策**: 
```bash
pip install -r requirements.txt
```

## 📋 ロールバック手順

マイグレーションを元に戻す必要がある場合：

```sql
-- カラムを削除（注意: データが失われます）
ALTER TABLE user_sessions DROP COLUMN IF EXISTS api_keys_cached;
ALTER TABLE user_sessions DROP COLUMN IF EXISTS api_cache_expires_at;

-- インデックスを削除
DROP INDEX IF EXISTS idx_user_sessions_api_cache_expires;
```

## 🔒 セキュリティ注意事項

- マイグレーション実行前にデータベースのバックアップを取ることを推奨
- 本番環境では低トラフィック時に実行することを推奨
- マイグレーション中はサービスが一時的に利用できなくなる可能性があります

## 📞 サポート

マイグレーションで問題が発生した場合は、以下の情報を含めてお問い合わせください：

1. エラーメッセージの全文
2. 実行したコマンド
3. 環境情報（OS、Pythonバージョン、PostgreSQLバージョン）
4. データベース接続設定（パスワードは除く）

---

**最終更新**: 2025-08-01  
**対象バージョン**: v2.0.0以降