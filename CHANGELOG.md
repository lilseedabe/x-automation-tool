# 📋 X自動反応ツール - 変更履歴

## [1.2.0] - 2025-01-29

### 🎉 主要機能追加

#### 🗄️ PostgreSQL VPS統合
- シンVPS (162.43.72.195) でのPostgreSQL 16データベース構築
- 非同期データベース接続 (asyncpg)
- ハイブリッド構成: Render (アプリ) + シンVPS (DB)

#### 👤 ユーザー管理システム
- JWT認証システム
- bcrypt パスワードハッシュ化
- セッション管理 (PostgreSQL保存)
- ユーザー登録・ログイン・プロフィール管理

#### 🔐 運営者ブラインド暗号化
- X APIキーのAES-256-GCM暗号化
- ユーザーパスワードベースのキー導出 (PBKDF2)
- 運営者が技術的に復号不可能な設計
- Row Level Security による データ分離

#### 🛡️ セキュリティ強化
- 暗号化ストレージ
- 自動セッション期限切れ
- fail2ban による攻撃対策
- ファイアウォール設定

### 📁 追加されたファイル

#### VPS セットアップ
- `vps-setup/01-postgresql-setup.sh` - 自動セットアップスクリプト
- `vps-setup/02-database-schema.sql` - データベーススキーマ
- `vps-setup/03-setup-instructions.md` - 詳細手順書

#### バックエンド
- `backend/database/connection.py` - データベース接続管理
- `backend/database/models.py` - SQLAlchemy + Pydantic モデル
- `backend/auth/user_service.py` - 認証・暗号化サービス
- `backend/api/auth_router.py` - 認証APIエンドポイント

### 🔄 更新されたファイル

#### コア
- `app.py` - PostgreSQL統合、認証システム統合
- `requirements.txt` - PostgreSQL依存関係追加
- `frontend/src/components/Login.jsx` - 2025年対応

### 🚀 新しいAPIエンドポイント

#### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - ユーザー情報取得
- `POST /api/auth/logout` - ログアウト
- `POST /api/auth/change-password` - パスワード変更

#### APIキー管理
- `POST /api/auth/api-keys` - X APIキー保存（暗号化）
- `GET /api/auth/api-keys` - APIキー状態取得
- `POST /api/auth/api-keys/test` - APIキー接続テスト
- `DELETE /api/auth/api-keys` - APIキー削除

#### 自動化設定
- `GET /api/auth/automation` - 自動化設定取得
- `PUT /api/auth/automation` - 自動化設定更新
- `POST /api/auth/automation/toggle` - 自動化ON/OFF

### 🗄️ データベーステーブル

作成されるテーブル:
- `users` - ユーザーアカウント
- `user_api_keys` - 暗号化APIキー（運営者ブラインド）
- `automation_settings` - 自動化設定
- `action_queue` - アクションキュー
- `user_blacklist` - ブラックリスト
- `activity_logs` - 活動履歴
- `user_sessions` - セッション管理
- `system_settings` - システム設定

### 🔧 技術スタック更新

#### 新規追加
- **asyncpg** - PostgreSQL非同期ドライバー
- **bcrypt** - パスワードハッシュ化
- **pyjwt** - JWT認証
- **cryptography** - AES-256-GCM暗号化

#### 継続使用
- **FastAPI 0.115.9+** - Python 3.13公式サポート
- **Pydantic 2.8+** - Python 3.13公式サポート
- **React** - フロントエンド
- **Tailwind CSS** - スタイリング

### 💰 コスト最適化

- **Render**: 無料プラン（フロントエンド・API）
- **シンVPS**: 月額約1,000円（1GB/1vCPU/30GB）
- **合計**: 月額約1,000円で完全なプライバシー保護

### 🛡️ プライバシー・セキュリティ

#### 運営者ブラインド設計
- APIキーは運営者が技術的に復号不可
- ユーザーパスワードベースの暗号化
- 透明性と信頼性の確保

#### データ保護
- HTTPS通信
- Row Level Security
- 自動データクリーンアップ
- fail2ban攻撃対策

### 🚦 デプロイメント

#### 環境変数
```bash
DATABASE_URL=postgresql+asyncpg://x_user:password@162.43.72.195:5432/x_automation
SECRET_KEY=your_32_character_secret_key
GROQ_API_KEY=your_groq_api_key
APP_ENV=production
```

#### セットアップ手順
1. シンVPSでPostgreSQL構築
2. データベーススキーマ適用
3. Render環境変数設定
4. GitHubプッシュ・デプロイ

---

## [1.1.0] - 2025-01-27

### ✅ Python 3.13対応完了
- FastAPI 0.115.9+ 公式サポート対応
- Pydantic 2.8+ 公式サポート対応
- 互換性問題完全解決

### 🔧 バグ修正
- 年表記を2024→2025に修正
- フロントエンドビルド問題解決

---

## [1.0.0] - 2025-01-26

### 🎉 初回リリース
- 基本的なX自動化機能
- AI分析機能 (Groq)
- React フロントエンド
- Render デプロイ対応