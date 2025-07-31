#!/bin/bash

# 🔄 X自動反応ツール - GitHubリモート同期 & プッシュ

echo "🤖 X自動反応ツール - GitHubリモート同期 & プッシュ"
echo "=================================================="

# 現在の状態確認
echo "📋 現在のGit状態確認中..."
git status

echo ""
echo "🔄 リモートリポジトリから最新変更を取得中..."

# リモートの最新情報を取得
git fetch origin

echo ""
echo "📊 ローカルとリモートの差分確認中..."

# ローカルとリモートの差分を確認
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "✅ ローカルとリモートは同期されています"
elif [ $LOCAL = $BASE ]; then
    echo "⬇️ リモートに新しい変更があります（Fast-forward可能）"
elif [ $REMOTE = $BASE ]; then
    echo "⬆️ ローカルに新しい変更があります"
else
    echo "🔀 ローカルとリモートの両方に変更があります（マージが必要）"
fi

echo ""
echo "📥 リモートの変更を統合中..."

# リモートの変更をプル（マージコミットを作成）
git pull origin main --no-rebase

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ マージでコンフリクトが発生しました"
    echo "📋 コンフリクト解決手順："
    echo "  1. コンフリクトファイルを手動編集"
    echo "  2. git add <解決したファイル>"
    echo "  3. git commit"
    echo "  4. このスクリプトを再実行"
    echo ""
    echo "🔍 コンフリクトファイル："
    git diff --name-only --diff-filter=U
    exit 1
fi

echo ""
echo "✅ リモート変更の統合完了"

echo ""
echo "📦 ローカル変更をコミット中..."

# ローカル変更があるかチェック
if [[ -n $(git status --porcelain) ]]; then
    echo "💾 新しい変更をコミット中..."
    
    # 全ファイルをステージング
    git add .
    
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
- Authentication: register, login, logout, user info
- API Key Management: operator-blind encrypted storage
- Automation Settings: configuration management

## 🗄️ Database Tables Created
8 tables with complete user management and operator-blind encryption

## 🔧 Tech Stack Updates
- asyncpg, bcrypt, pyjwt, cryptography, SQLAlchemy 2.0+

## 🛡️ Privacy & Security
Complete operator-blind design with enterprise-level security

## 💰 Cost Optimization
~¥1,000/month for complete privacy protection

Ready for production with PostgreSQL VPS integration! 🎊"

    if [ $? -eq 0 ]; then
        echo "✅ コミット成功"
    else
        echo "❌ コミット失敗"
        exit 1
    fi
else
    echo "📝 新しいローカル変更はありません"
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
    echo "📋 反映された内容:"
    echo "  🗄️ PostgreSQL VPS統合"
    echo "  👤 ユーザー管理システム"
    echo "  🔐 運営者ブラインド暗号化"
    echo "  🛡️ エンタープライズセキュリティ"
    echo "  📚 完全なドキュメント"
    echo ""
    echo "🔗 次のステップ:"
    echo "  1. Renderで環境変数設定:"
    echo "     DATABASE_URL=postgresql+asyncpg://x_user:password@162.43.72.195:5432/x_automation"
    echo "     SECRET_KEY=your_32_character_secret_key_here"
    echo "     GROQ_API_KEY=your_groq_api_key_here"
    echo ""
    echo "  2. Renderで自動デプロイ確認"
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
    echo "  - 再度このスクリプトを実行"
    exit 1
fi

echo ""
echo "📊 最終状態確認:"
git log --oneline -5
echo ""
echo "🎉 全ての変更がGitHubに正常に反映されました！"