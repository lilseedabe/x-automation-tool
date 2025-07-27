#!/bin/bash

# 🚀 X自動反応ツール - GitHubプッシュ & Renderデプロイスクリプト
# 機密情報を適切に除外してGitHubにプッシュ

set -e  # エラー時に停止

echo "🤖 X自動反応ツール - デプロイメント準備"
echo "=========================================="

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
echo_info "前提条件をチェック中..."

# Git の確認
if ! command -v git &> /dev/null; then
    echo_error "Git がインストールされていません"
    exit 1
fi

# Node.js の確認
if ! command -v node &> /dev/null; then
    echo_error "Node.js がインストールされていません"
    exit 1
fi

# Python の確認
if ! command -v python3 &> /dev/null; then
    echo_error "Python 3 がインストールされていません"
    exit 1
fi

echo_success "前提条件チェック完了"

# 機密情報チェック
echo_info "機密情報の除外チェック中..."

# .env ファイルの確認
if [ -f ".env" ]; then
    echo_warning ".env ファイルが存在します（.gitignoreで除外済み）"
fi

# data/users/ の確認
if [ -d "data/users" ]; then
    echo_warning "data/users/ フォルダが存在します（.gitignoreで除外済み）"
fi

# logs/ の確認
if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
    echo_warning "logs/ フォルダにファイルが存在します（.gitignoreで除外済み）"
fi

echo_success "機密情報チェック完了"

# Git の初期化・設定
echo_info "Git リポジトリを初期化中..."

# 既にGitリポジトリかチェック
if [ ! -d ".git" ]; then
    git init
    echo_success "Git リポジトリを初期化しました"
else
    echo_info "既存のGit リポジトリを使用します"
fi

# リモートリポジトリの設定
REPO_URL="https://github.com/lilseedabe/x-automation-tool.git"

# 既存のリモートをチェック
if git remote | grep -q "origin"; then
    echo_info "既存のリモートリポジトリを使用します"
    git remote set-url origin $REPO_URL
else
    git remote add origin $REPO_URL
    echo_success "リモートリポジトリを追加しました: $REPO_URL"
fi

# フロントエンドの依存関係確認
echo_info "フロントエンドの依存関係をチェック中..."

cd frontend

if [ ! -d "node_modules" ]; then
    echo_info "npm install を実行中..."
    npm install
    echo_success "フロントエンドの依存関係をインストールしました"
else
    echo_info "フロントエンドの依存関係は既にインストール済みです"
fi

# フロントエンドのビルドテスト
echo_info "フロントエンドのビルドテスト中..."
npm run build
echo_success "フロントエンドのビルドテスト完了"

cd ..

# Python 依存関係の確認
echo_info "Python依存関係をチェック中..."

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo_info "Python仮想環境を作成中..."
    python3 -m venv venv
    echo_success "Python仮想環境を作成しました"
fi

# 依存関係のインストール
echo_info "Python依存関係をインストール中..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
pip install --upgrade pip
pip install -r requirements.txt
echo_success "Python依存関係をインストールしました"

# gitignore チェック
echo_info ".gitignore の内容をチェック中..."

GITIGNORE_ITEMS=(
    ".env"
    "data/users/"
    "logs/"
    "node_modules/"
    "__pycache__/"
    "venv/"
    "*.log"
)

for item in "${GITIGNORE_ITEMS[@]}"; do
    if grep -q "$item" .gitignore; then
        echo_success ".gitignore に $item が含まれています"
    else
        echo_warning ".gitignore に $item が含まれていません"
    fi
done

# 除外されるべきファイルがGitに追跡されていないかチェック
echo_info "追跡されるべきでないファイルをチェック中..."

SHOULD_BE_IGNORED=(
    ".env"
    "data/users/"
    "logs/"
)

for item in "${SHOULD_BE_IGNORED[@]}"; do
    if git check-ignore "$item" >/dev/null 2>&1; then
        echo_success "$item は適切に除外されます"
    else
        if [ -e "$item" ]; then
            echo_warning "$item が存在しますが、除外設定を確認してください"
        fi
    fi
done

# ファイルの追加とコミット
echo_info "ファイルをGitに追加中..."

# ステージングエリアに追加
git add .

# 追加されたファイルの確認
echo_info "以下のファイルがコミットされます:"
git diff --cached --name-only | head -20

# コミットメッセージの作成
COMMIT_MESSAGE="🚀 Initial deployment setup

✨ Features:
- 運営者ブラインド設計実装
- プライバシー重視のX自動化ツール
- Render対応デプロイメント設定

🔧 Technical:
- FastAPI + React アーキテクチャ
- PostgreSQL データベース対応
- Groq AI統合
- 暗号化ストレージシステム

🛡️ Security:
- 機密情報の適切な除外
- 運営者アクセス不可設計
- 自動削除機能

📦 Deployment:
- render.yaml 設定完了
- 環境変数テンプレート作成
- CI/CD 準備完了"

# コミットの実行
echo_info "変更をコミット中..."
git commit -m "$COMMIT_MESSAGE"
echo_success "コミットが完了しました"

# ブランチの確認・設定
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo_info "ブランチを main に変更中..."
    git checkout -b main 2>/dev/null || git checkout main
fi

# プッシュ前の最終確認
echo_warning "=========================================="
echo_warning "GitHubにプッシュする前の最終確認"
echo_warning "=========================================="
echo ""
echo "リポジトリURL: $REPO_URL"
echo "ブランチ: $(git branch --show-current)"
echo "コミット: $(git log --oneline -1)"
echo ""
echo "除外されているファイル:"
echo "- .env (環境変数)"
echo "- data/users/ (ユーザーデータ)"
echo "- logs/ (ログファイル)"
echo "- node_modules/ (Node.js依存関係)"
echo "- venv/ (Python仮想環境)"
echo ""

# ユーザー確認
read -p "GitHubにプッシュしますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo_info "GitHubにプッシュ中..."
    
    # プッシュの実行
    git push -u origin main
    
    echo_success "=========================================="
    echo_success "✅ GitHubへのプッシュが完了しました！"
    echo_success "=========================================="
    echo ""
    echo "🔗 リポジトリURL: $REPO_URL"
    echo ""
    echo "📋 次のステップ（Renderデプロイ）:"
    echo "1. Render.com にログイン"
    echo "2. 'New +' → 'Web Service'"
    echo "3. GitHub repository: lilseedabe/x-automation-tool"
    echo "4. Branch: main"
    echo "5. Environment: Python"
    echo "6. Build Command: pip install -r requirements.txt"
    echo "7. Start Command: python -m uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
    echo ""
    echo "🔑 必要な環境変数:"
    echo "- GROQ_API_KEY (あなたのGroq APIキー)"
    echo "- SECRET_KEY (32文字以上のランダム文字列)"
    echo "- DATABASE_URL (RenderのPostgreSQLから自動設定)"
    echo ""
    echo "🎉 設定が完了すると、自動的にデプロイが開始されます！"
    
else
    echo_info "プッシュをキャンセルしました"
    echo ""
    echo "💡 後でプッシュする場合は以下のコマンドを実行:"
    echo "git push -u origin main"
fi

echo ""
echo_success "🤖 デプロイメント準備スクリプトが完了しました！"