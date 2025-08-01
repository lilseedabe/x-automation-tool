# 🔧 VPSでのマイグレーション実行手順（簡単版）

## 📝 概要
既存の`user_sessions`テーブルに2つのカラムを追加するだけの軽微な変更です。

### 追加されるカラム：
- `api_keys_cached` (真偽値): APIキーがキャッシュされているかのフラグ
- `api_cache_expires_at` (日時): キャッシュの有効期限

## 🚀 実行手順（5分程度）

### 1. VPSにSSH接続
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

### 4. マイグレーション実行（3つの方法から選択）

#### 🔥 **方法A: 自動スクリプト実行（推奨）**
```bash
chmod +x migrate-database.sh
./migrate-database.sh
```

#### 🐍 **方法B: Pythonスクリプト実行**
```bash
python run_migration.py
```

#### 🗄️ **方法C: 直接SQL実行**
```bash
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database_migration.sql
```

### 5. サービス再起動
```bash
sudo systemctl restart x-automation-tool
```

## ✅ 動作確認
1. ブラウザでログインページにアクセス
2. 既存のユーザーでログイン
3. エラーが発生しないことを確認
4. ログアウト→再ログインでAPIキーが保持されることを確認

## 🛡️ 安全性
- **既存データは一切変更されません**
- **新しいカラムのみ追加**
- **ロールバック可能**
- **ダウンタイム約30秒**

---
**質問があれば遠慮なくお聞きください！**