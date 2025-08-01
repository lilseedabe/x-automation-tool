#!/bin/bash

# 🔄 VPSでのデータベースマイグレーション実行スクリプト
# APIキーキャッシュ機能のためのuser_sessionsテーブル更新

set -e  # エラー時に停止

echo "🚀 X自動反応ツール - データベースマイグレーション"
echo "=" 50

# カレントディレクトリをスクリプトのディレクトリに変更
cd "$(dirname "$0")"

# Python仮想環境があるかチェック
if [ -d "venv" ]; then
    echo "📦 Python仮想環境をアクティブ化中..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Python仮想環境をアクティブ化中..."
    source .venv/bin/activate
else
    echo "⚠️  仮想環境が見つかりません。システムPythonを使用します"
fi

# 必要な環境変数がセットされているかチェック
required_vars=("DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ 必要な環境変数が設定されていません: ${missing_vars[*]}"
    echo "以下の環境変数を設定してください:"
    for var in "${missing_vars[@]}"; do
        echo "   export $var=<値>"
    done
    exit 1
fi

# .env.productionファイルがあれば読み込み
if [ -f ".env.production" ]; then
    echo "📄 .env.production を読み込み中..."
    export $(cat .env.production | grep -v '^#' | xargs)
fi

echo "🔍 データベース接続確認中..."
echo "   ホスト: $DB_HOST"
echo "   データベース: $DB_NAME"
echo "   ユーザー: $DB_USER"

# 依存関係インストール確認
echo "📦 依存関係の確認中..."
python -c "import asyncpg, sqlalchemy" 2>/dev/null || {
    echo "❌ 必要なライブラリがインストールされていません"
    echo "pip install -r requirements.txt を実行してください"
    exit 1
}

echo "✅ 依存関係OK"

# マイグレーション実行
echo "🔄 マイグレーション実行中..."
python run_migration.py

if [ $? -eq 0 ]; then
    echo "🎉 マイグレーション正常完了！"
    echo "🔄 Webサービスを再起動してください:"
    echo "   sudo systemctl restart x-automation-tool"
    echo "   または"
    echo "   sudo supervisorctl restart x-automation-tool"
else
    echo "❌ マイグレーションでエラーが発生しました"
    exit 1
fi