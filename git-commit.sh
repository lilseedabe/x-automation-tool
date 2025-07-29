#!/bin/bash

# 🚀 X自動反応ツール - PostgreSQL VPS統合 GitHubコミット

echo "🤖 X自動反応ツール - PostgreSQL VPS統合のGitHubコミット"
echo "=================================================="

# 現在の状態確認
echo "📋 変更ファイル確認中..."
git status

echo ""
echo "📦 主要な追加・変更内容:"
echo "  ✅ PostgreSQL VPS統合"
echo "  ✅ ユーザー管理システム"  
echo "  ✅ 運営者ブラインド暗号化"
echo "  ✅ JWT認証システム"
echo "  ✅ APIキー暗号化管理"
echo "  ✅ セキュリティ強化"
echo ""

# ユーザーに確認
read -p "これらの変更をGitHubにコミット・プッシュしますか？ (y/N): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "❌ コミットをキャンセルしました"
    exit 1
fi

echo ""
echo "🔄 GitHubへの反映を開始..."

# 全ファイルをステージング
echo "📁 ファイルをステージング中..."
git add .

# 変更されたファイルリスト表示
echo ""
echo "📋 ステージングされたファイル:"
git diff --cached --name-only

echo ""
echo "💾 コミット実行中..."

# コミット実行
git commit -m "🗄️ Add PostgreSQL VPS + User Management System

## 🎉 Major Features Added

### 🏗️ PostgreSQL VPS Integration
- シンVPS (162.43.72.195) PostgreSQL 16 database
- Hybrid architecture: Render (app) + VPS (database)
- Async database connection with asyncpg
- Cost-optimized: ~¥1,000/month for complete privacy

### 👤 User Management System  
- JWT authentication with bcrypt password hashing
- Session management stored in PostgreSQL
- User registration, login, profile management
- Password change functionality

### 🔐 Operator-Blind Encryption
- X API keys encrypted with AES-256-GCM
- User password-based key derivation (PBKDF2)
- Technically impossible for operators to decrypt
- Row Level Security for data isolation

### 🛡️ Enterprise-Level Security
- fail2ban for attack prevention
- Firewall configuration
- Automatic session cleanup
- Encrypted storage with transparent design

## 📁 New Files Added

### VPS Setup
- vps-setup/01-postgresql-setup.sh (Auto setup script)
- vps-setup/02-database-schema.sql (Database schema)
- vps-setup/03-setup-instructions.md (Detailed instructions)

### Backend
- backend/database/connection.py (DB connection management)
- backend/database/models.py (SQLAlchemy + Pydantic models)
- backend/auth/user_service.py (Auth + encryption services)
- backend/api/auth_router.py (Authentication API endpoints)

### Documentation  
- CHANGELOG.md (Complete change history)
- README.md (Updated with PostgreSQL VPS integration)

## 🔄 Updated Files
- app.py (PostgreSQL integration, auth system)
- requirements.txt (PostgreSQL dependencies)
- frontend/src/components/Login.jsx (2025 copyright)

## 🚀 New API Endpoints

### Authentication
- POST /api/auth/register (User registration)
- POST /api/auth/login (Login)
- GET /api/auth/me (User info)
- POST /api/auth/logout (Logout)

### API Key Management (Operator-Blind)
- POST /api/auth/api-keys (Store encrypted X API keys)
- GET /api/auth/api-keys (Get API key status)
- POST /api/auth/api-keys/test (Test API connection)
- DELETE /api/auth/api-keys (Delete API keys)

### Automation Settings
- GET /api/auth/automation (Get automation settings)
- PUT /api/auth/automation (Update automation settings)
- POST /api/auth/automation/toggle (Toggle automation on/off)

## 🗄️ Database Tables Created
- users (User accounts)
- user_api_keys (Encrypted API keys - operator blind)
- automation_settings (Automation configuration)
- action_queue (Action queue)
- user_blacklist (Blacklist management)
- activity_logs (Activity history)
- user_sessions (Session management)
- system_settings (System configuration)

## 🔧 Tech Stack Updates
- asyncpg (PostgreSQL async driver)
- bcrypt (Password hashing)
- pyjwt (JWT authentication)  
- cryptography (AES-256-GCM encryption)
- SQLAlchemy 2.0+ (Async ORM)

## 🛡️ Privacy & Security
- Complete operator-blind design
- User password-based encryption
- Enterprise-level security
- Transparent open-source design
- HTTPS + CORS security
- Row Level Security in PostgreSQL

## 💰 Cost Optimization
- Render: Free tier (Frontend + API)
- 真VPS: ~¥1,000/month (1GB/1vCPU/30GB)
- Total: ~¥1,000/month for complete privacy protection

Ready for production with PostgreSQL VPS integration! 🎊"

if [ $? -eq 0 ]; then
    echo "✅ コミット成功"
else
    echo "❌ コミット失敗"
    exit 1
fi

echo ""
echo "🚀 GitHubにプッシュ中..."

# プッシュ実行
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ 🎉 GitHubへの反映完了！"
    echo "=================================================="
    echo ""
    echo "📋 コミット内容:"
    echo "  🗄️ PostgreSQL VPS統合"
    echo "  👤 ユーザー管理システム"
    echo "  🔐 運営者ブラインド暗号化"
    echo "  🛡️ エンタープライズセキュリティ"
    echo ""
    echo "🔗 次のステップ:"
    echo "  1. Renderで環境変数設定"
    echo "  2. 自動デプロイ確認"
    echo "  3. PostgreSQL VPS接続テスト"
    echo ""
    echo "🌐 GitHub Repository:"
    echo "  https://github.com/lilseedabe/x-automation-tool"
    echo ""
    echo "🎊 PostgreSQL VPS + 運営者ブラインド設計完成！"
else
    echo ""
    echo "❌ プッシュ失敗"
    echo "📋 トラブルシューティング:"
    echo "  - インターネット接続を確認"
    echo "  - GitHub認証情報を確認"
    echo "  - git pull で最新化してから再実行"
    exit 1
fi