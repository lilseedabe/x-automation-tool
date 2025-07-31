#!/bin/bash

# 🔄 GitHub → ローカル 変更取得スクリプト
# GitHubで直接編集した内容をローカルに安全に反映

echo "🔄 GitHub → ローカル 変更同期スクリプト"
echo "=================================================="

# 現在のGit状態確認
echo "📋 現在のローカル状態確認中..."
echo ""
echo "🏷️  現在のブランチ:"
git branch --show-current

echo ""
echo "📊 ローカルファイルの状態:"
git status --porcelain

if [[ -n $(git status --porcelain) ]]; then
    echo ""
    echo "⚠️  ローカルに未コミットの変更があります！"
    echo "📁 変更されたファイル:"
    git status --short
    echo ""
    read -p "これらの変更をスタッシュ（一時保存）しますか？ (y/N): " stash_confirm
    
    if [[ $stash_confirm == [yY] || $stash_confirm == [yY][eE][sS] ]]; then
        echo "💾 ローカル変更をスタッシュ中..."
        git stash push -m "Local changes before GitHub sync $(date '+%Y-%m-%d %H:%M:%S')"
        echo "✅ ローカル変更をスタッシュしました"
        STASHED=true
    else
        echo "❌ 同期をキャンセルしました"
        echo ""
        echo "📋 次の手順で手動で処理してください:"
        echo "  1. 重要な変更をコミット: git add . && git commit -m 'Local changes'"
        echo "  2. または変更を破棄: git reset --hard HEAD"
        echo "  3. 再度このスクリプトを実行"
        exit 1
    fi
else
    echo "✅ ローカルに未コミットの変更はありません"
    STASHED=false
fi

echo ""
echo "🌐 GitHubから最新変更を取得中..."

# リモート情報更新
git fetch origin

echo ""
echo "📊 ローカルとGitHubの差分確認中..."

# コミット履歴比較
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

echo "🏠 ローカル最新コミット: ${LOCAL_COMMIT:0:8}"
echo "🌐 GitHub最新コミット:  ${REMOTE_COMMIT:0:8}"

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ ローカルとGitHubは同期されています"
    
    if [ "$STASHED" = true ]; then
        echo ""
        read -p "スタッシュした変更を復元しますか？ (y/N): " restore_confirm
        if [[ $restore_confirm == [yY] || $restore_confirm == [yY][eE][sS] ]]; then
            echo "🔄 スタッシュした変更を復元中..."
            git stash pop
            echo "✅ 変更を復元しました"
        fi
    fi
    
    echo "🎉 同期完了！"
    exit 0
fi

echo ""
echo "📥 GitHubの変更をローカルに取り込み中..."

# Fast-forward可能かチェック
MERGE_BASE=$(git merge-base HEAD origin/main)

if [ "$LOCAL_COMMIT" = "$MERGE_BASE" ]; then
    echo "⚡ Fast-forward可能です"
    git merge origin/main --ff-only
    
    if [ $? -eq 0 ]; then
        echo "✅ Fast-forwardマージ成功"
    else
        echo "❌ Fast-forwardマージ失敗"
        exit 1
    fi
    
elif [ "$REMOTE_COMMIT" = "$MERGE_BASE" ]; then
    echo "⬆️  ローカルが先行しています（GitHubより新しい）"
    echo "⚠️  GitHubをローカルの内容で更新する必要があります"
    echo ""
    read -p "GitHubにローカルの変更をプッシュしますか？ (y/N): " push_confirm
    
    if [[ $push_confirm == [yY] || $push_confirm == [yY][eE][sS] ]]; then
        echo "🚀 GitHubにプッシュ中..."
        git push origin main
        echo "✅ プッシュ完了"
    else
        echo "ℹ️  プッシュをスキップしました"
    fi
    
else
    echo "🔀 両方に変更があります（マージが必要）"
    echo ""
    echo "⚠️  マージコンフリクトが発生する可能性があります"
    read -p "マージを実行しますか？ (y/N): " merge_confirm
    
    if [[ $merge_confirm == [yY] || $merge_confirm == [yY][eE][sS] ]]; then
        echo "🔀 マージ実行中..."
        git merge origin/main
        
        if [ $? -eq 0 ]; then
            echo "✅ マージ成功"
        else
            echo "❌ マージコンフリクトが発生しました"
            echo ""
            echo "📋 コンフリクト解決手順:"
            echo "  1. コンフリクトファイルを編集して解決"
            echo "  2. git add <解決したファイル>"
            echo "  3. git commit"
            echo ""
            echo "🔍 コンフリクトファイル:"
            git diff --name-only --diff-filter=U
            exit 1
        fi
    else
        echo "❌ マージをキャンセルしました"
        exit 1
    fi
fi

# スタッシュ復元
if [ "$STASHED" = true ]; then
    echo ""
    read -p "スタッシュした変更を復元しますか？ (y/N): " restore_confirm
    if [[ $restore_confirm == [yY] || $restore_confirm == [yY][eE][sS] ]]; then
        echo "🔄 スタッシュした変更を復元中..."
        git stash pop
        
        if [ $? -eq 0 ]; then
            echo "✅ 変更を復元しました"
        else
            echo "⚠️  復元時にコンフリクトが発生しました"
            echo "📋 手動で解決してください"
        fi
    fi
fi

echo ""
echo "📊 同期後の状態:"
git log --oneline -5

echo ""
echo "📁 変更されたファイル:"
git diff --name-only HEAD~1 HEAD

echo ""
echo "=================================================="
echo "✅ 🎉 GitHub → ローカル 同期完了！"
echo "=================================================="
echo ""
echo "📋 実行された作業:"
echo "  🌐 GitHubから最新変更を取得"
echo "  🔄 ローカルに変更を統合"
echo "  💾 必要に応じてローカル変更をスタッシュ"
echo ""
echo "🔗 次のステップ:"
echo "  1. 変更内容を確認: git log --oneline -10"
echo "  2. ファイル内容を確認: git show HEAD"
echo "  3. 開発継続: 通常通りコード編集"
echo ""
echo "🎊 GitHubで編集した内容がローカルに反映されました！"