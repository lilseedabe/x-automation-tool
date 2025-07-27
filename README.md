# 🤖 X自動反応ツール

**プライバシー重視のX（旧Twitter）自動反応システム**

運営者ブラインド設計により、ユーザーのAPIキーに運営者が一切アクセスできない、最高レベルのプライバシー保護を実現したX自動化ツールです。

## 🌟 特徴

### 🔐 **最高レベルのプライバシー保護**
- **運営者ブラインド設計**: 技術的に運営者がユーザーデータにアクセス不可
- **暗号化保存**: RSA-2048 + AES-256による強力な暗号化
- **自動削除**: 設定可能な期間後に自動でデータ削除
- **透明性**: データの保存場所・期間・アクセス権限が完全に明示

### 🚀 **高機能なX自動化**
- **AI分析**: Groq AIによる高度なエンゲージメント分析
- **スマートターゲティング**: 質の高いユーザーのみに自動反応
- **安全な実行**: レート制限遵守とブラックリスト機能
- **継続運用**: 24時間自動実行（選択可能）

### ⚖️ **法的安全性**
- **国内サーバー**: 日本国内でのデータ管理オプション
- **GDPR準拠**: EU一般データ保護規則に対応
- **運営者責任最小化**: 技術的制限により法的リスクを軽減

## 📊 **アーキテクチャ**

```
ユーザー
    ↓
┌─────────────────┐
│  React Frontend │ ← ローカル暗号化保存
└─────────────────┘
    ↓ HTTPS
┌─────────────────┐
│  FastAPI Backend│ ← 運営者ブラインド処理
└─────────────────┘
    ↓
┌─────────────────┐
│  PostgreSQL DB  │ ← 暗号化データのみ
└─────────────────┘
    ↓
┌─────────────────┐
│    Groq AI      │ ← 運営者一括管理
└─────────────────┘
```

## 🎯 **データ保存オプション**

### 1. **ローカル保存モード**（推奨・最高プライバシー）
- ✅ ブラウザのローカルストレージのみ
- ✅ サーバーには一切保存されない
- ✅ 運営者・第三者のアクセス完全不可
- ❌ 継続自動化には手動実行が必要

### 2. **運営者ブラインドモード**（継続自動化対応）
- ✅ 24時間継続自動実行
- ✅ 運営者が技術的にアクセス不可
- ✅ 暗号化サーバー保存
- ✅ 柔軟な保持期間設定（24時間〜無期限）

## 🚀 **デプロイメント**

### **Renderへのデプロイ**

#### **前提条件**
- GitHubアカウント
- Renderアカウント
- Groq APIキー

#### **ステップ1: GitHubリポジトリの準備**

```bash
# 1. リポジトリをクローン
git clone https://github.com/lilseedabe/x-automation-tool.git
cd x-automation-tool

# 2. 依存関係の確認
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. 環境変数ファイルの設定
cp .env.example .env
# .env ファイルを編集して必要な値を設定
```

#### **ステップ2: Renderでのデプロイ**

1. **Renderにログイン**
   - [render.com](https://render.com) にアクセス
   - GitHubアカウントで連携

2. **Web Serviceの作成**
   - 「New +」→ 「Web Service」
   - GitHub repository: `lilseedabe/x-automation-tool`
   - Branch: `main`

3. **設定値**
   ```
   Name: x-automation-tool
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

4. **環境変数の設定**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_32_character_secret_key
   APP_ENV=production
   OPERATOR_BLIND_ENABLED=true
   PRIVACY_MODE=maximum
   ```

5. **PostgreSQLデータベースの追加**
   - 「New +」→ 「PostgreSQL」
   - Name: `x-automation-db`
   - Plan: Starter (無料)

6. **データベース接続**
   - Web Serviceの環境変数に `DATABASE_URL` を追加
   - PostgreSQLの接続文字列を設定

#### **ステップ3: フロントエンドのデプロイ**

1. **Static Siteの作成**
   - 「New +」→ 「Static Site」
   - 同じGitHubリポジトリを選択

2. **設定値**
   ```
   Name: x-automation-frontend
   Build Command: cd frontend && npm ci && npm run build
   Publish Directory: frontend/build
   ```

3. **環境変数の設定**
   ```
   REACT_APP_API_URL=https://x-automation-tool.onrender.com
   REACT_APP_ENV=production
   REACT_APP_PRIVACY_MODE=maximum
   ```

### **自動デプロイの設定**

`render.yaml` ファイルが含まれているため、GitHubにプッシュするだけで自動デプロイされます：

```bash
# GitHubにプッシュ
git add .
git commit -m "🚀 Initial deployment setup"
git push origin main
```

## 🔧 **ローカル開発**

### **開発環境のセットアップ**

```bash
# 1. リポジトリをクローン
git clone https://github.com/lilseedabe/x-automation-tool.git
cd x-automation-tool

# 2. バックエンドのセットアップ
pip install -r requirements.txt
cp .env.example .env
# .env ファイルを編集

# 3. フロントエンドのセットアップ
cd frontend
npm install
cp .env.example .env.local
# .env.local ファイルを編集
cd ..

# 4. データベースの初期化（ローカル開発用）
python -c "
import asyncio
from backend.infrastructure.operator_blind_storage import initialize_database
asyncio.run(initialize_database())
"
```

### **開発サーバーの起動**

```bash
# バックエンド（ターミナル1）
python -m uvicorn backend.main:app --reload --port 8000

# フロントエンド（ターミナル2）
cd frontend
npm start
```

アプリケーションは以下のURLでアクセス可能：
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API文書: http://localhost:8000/docs

## 🔑 **API設定**

### **X (Twitter) API**
ユーザーが各自で取得・設定：

1. [X Developer Portal](https://developer.twitter.com/) でアプリ作成
2. 以下の4つのキーを取得：
   - API Key (Consumer Key)
   - API Key Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
3. アプリの設定画面で入力

### **Groq AI API**
運営者が一括管理：

1. [Groq Console](https://console.groq.com/) でAPIキー取得
2. Renderの環境変数 `GROQ_API_KEY` に設定
3. ユーザーは設定不要

## 🛡️ **セキュリティ**

### **データ保護**
- **暗号化アルゴリズム**: RSA-2048 + AES-256
- **キー管理**: ユーザー専用パスワード
- **保存場所**: 選択可能（ローカル or 暗号化サーバー）
- **アクセス制御**: 運営者は技術的にアクセス不可

### **プライバシー保証**
- **運営者ブラインド**: APIキーにアクセス不可
- **データ最小化**: 必要最小限のデータのみ保存
- **自動削除**: 設定期間後に自動削除
- **透明性**: 全ての処理が明示

### **セキュリティベストプラクティス**
- HTTPS通信の強制
- CSRFプロテクション
- レート制限
- 入力値検証
- セキュリティヘッダー

## 📈 **監視・運用**

### **ヘルスチェック**
- API: `/api/system/health`
- フロントエンド: 自動ヘルスチェック
- データベース: 接続確認

### **ログ・監視**
- アプリケーションログ
- エラートラッキング
- パフォーマンス監視
- アップタイム監視

### **バックアップ**
- データベース: 自動日次バックアップ
- 設定: GitHubリポジトリで管理
- ログ: Renderで自動管理

## 💰 **コスト**

### **Render無料プラン活用**
- **Web Service**: 750時間/月（約31日）
- **Static Site**: 100GBバンドウィズ/月
- **PostgreSQL**: 1GB + 1,000,000行
- **推定月額**: $0（無料プランのみ）

### **有料プラン（必要に応じて）**
- **Web Service**: $7/月〜
- **PostgreSQL**: $7/月〜
- **プロフェッショナル機能**: カスタムドメイン等

## 🤝 **コントリビューション**

### **開発に参加する**

```bash
# 1. フォーク
gh repo fork lilseedabe/x-automation-tool

# 2. ブランチ作成
git checkout -b feature/new-feature

# 3. 開発・テスト
# コード変更

# 4. プルリクエスト
git push origin feature/new-feature
# GitHubでPRを作成
```

### **イシューの報告**
- [GitHub Issues](https://github.com/lilseedabe/x-automation-tool/issues)
- バグ報告・機能要望・質問

## 📄 **ライセンス**

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🔗 **リンク**

- **本番環境**: https://x-automation-tool.onrender.com
- **API文書**: https://x-automation-tool.onrender.com/docs
- **GitHub**: https://github.com/lilseedabe/x-automation-tool
- **Issues**: https://github.com/lilseedabe/x-automation-tool/issues

## 📞 **サポート**

### **よくある質問**

**Q: APIキーは安全ですか？**
A: はい。運営者ブラインド設計により、技術的に運営者がアクセスできません。

**Q: 無料で使えますか？**
A: はい。Renderの無料プランで十分に運用可能です。

**Q: データはいつまで保存されますか？**
A: ユーザーが選択した期間（24時間〜無期限）後に自動削除されます。

**Q: 海外のサーバーにデータが送信されますか？**
A: Renderは米国のサービスですが、運営者ブラインド設計により最高レベルの保護を実現しています。

### **お問い合わせ**
- GitHub Issues: 技術的な質問・バグ報告
- メール: リポジトリのContacts参照

---

**🔐 プライバシー保証: このツールは運営者が技術的にユーザーデータにアクセスできない設計になっています。安心してご利用ください。**