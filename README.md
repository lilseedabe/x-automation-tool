# 🤖 X自動反応ツール

AI搭載のX自動化プラットフォーム - 運営者ブラインド設計でプライバシー重視

## 🌟 特徴

### 🔐 運営者ブラインド設計
- **完全なプライバシー保護**: ユーザーのX APIキーを運営者が技術的に復号不可能
- **ユーザーパスワードベース暗号化**: AES-256-GCM + PBKDF2
- **透明性**: オープンソースで設計の透明性を保証

### 🏗️ ハイブリッド構成
- **Render**: FastAPI + React フロントエンド（無料）
- **シンVPS**: PostgreSQL データベース（月額1,000円）
- **コスト効率**: 高性能・安全性・コストのバランス

### 🤖 AI搭載自動化
- **Groq AI分析**: 高度なエンゲージメント評価
- **スマートターゲティング**: 質の高いユーザーのみに自動反応
- **人間らしいタイミング**: 自然な間隔での自動化

### 🛡️ エンタープライズレベルのセキュリティ
- **JWT認証**: セキュアなトークンベース認証
- **bcryptハッシュ化**: 業界標準のパスワード保護
- **Row Level Security**: データベースレベルでのユーザー分離
- **fail2ban**: 攻撃対策・ブルートフォース防止

## 🚀 クイックスタート

### 前提条件
- Node.js 18+
- Python 3.13
- PostgreSQL (VPS)

### インストール

1. **リポジトリクローン**
```bash
git clone https://github.com/lilseedabe/x-automation-tool.git
cd x-automation-tool
```

2. **依存関係インストール**
```bash
# Python依存関係
pip install -r requirements.txt

# Node.js依存関係
cd frontend
npm install
cd ..
```

3. **フロントエンドビルド**
```bash
cd frontend
npm run build
cd ..
```

4. **環境変数設定**
```bash
# .env ファイル作成
cp .env.example .env

# 必須環境変数
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your_32_character_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
```

5. **アプリケーション起動**
```bash
python app.py
```

## 🗄️ PostgreSQL VPS セットアップ

### シンVPS 自動セットアップ

1. **VPSにSSHログイン**
```bash
ssh root@your-vps-ip
```

2. **セットアップスクリプト実行**
```bash
wget https://raw.githubusercontent.com/lilseedabe/x-automation-tool/main/vps-setup/01-postgresql-setup.sh
chmod +x 01-postgresql-setup.sh
./01-postgresql-setup.sh
```

3. **データベーススキーマ適用**
```bash
wget https://raw.githubusercontent.com/lilseedabe/x-automation-tool/main/vps-setup/02-database-schema.sql
sudo -u postgres psql -d x_automation_db -f 02-database-schema.sql
```

詳細な手順は [`vps-setup/03-setup-instructions.md`](vps-setup/03-setup-instructions.md) を参照してください。

## 🔑 API エンドポイント

### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - ユーザー情報取得
- `POST /api/auth/logout` - ログアウト

### APIキー管理（運営者ブラインド）
- `POST /api/auth/api-keys` - X APIキー暗号化保存
- `GET /api/auth/api-keys` - APIキー状態取得
- `POST /api/auth/api-keys/test` - APIキー接続テスト
- `DELETE /api/auth/api-keys` - APIキー削除

### 自動化設定
- `GET /api/auth/automation` - 自動化設定取得
- `PUT /api/auth/automation` - 自動化設定更新
- `POST /api/auth/automation/toggle` - 自動化ON/OFF

### システム
- `GET /health` - ヘルスチェック
- `GET /api/system/health` - 詳細システム状態
- `GET /api/docs` - Swagger API文書

## 🏗️ アーキテクチャ

```
┌─────────────────┐    HTTPS    ┌──────────────────┐
│     ユーザー      │ ◄────────► │   Render (無料)   │
└─────────────────┘             │  FastAPI + React │
                                └─────────┬────────┘
                                          │ 暗号化通信
                                          ▼
                                ┌─────────────────────┐
                                │   シンVPS (1,000円)  │
                                │  PostgreSQL 16 DB  │
                                │   運営者ブラインド   │
                                └─────────────────────┘
```

### 運営者ブラインド設計
```
[ユーザーパスワード] + [ソルト] 
         ↓ PBKDF2 (100,000回)
    [暗号化キー] 
         ↓ AES-256-GCM
   [暗号化APIキー] → PostgreSQL保存

※運営者はユーザーパスワードを知らないため復号不可能
```

## 🛡️ セキュリティ

### データ保護
- **暗号化**: X APIキーはAES-256-GCMで暗号化
- **パスワード**: bcrypt + ソルトでハッシュ化
- **通信**: HTTPS強制・CORS設定
- **データベース**: Row Level Security

### アクセス制御
- **JWT認証**: 24時間有効期限
- **セッション管理**: PostgreSQL保存
- **自動ログアウト**: 期限切れ自動処理
- **リフレッシュトークン**: 30日間有効

### 攻撃対策
- **fail2ban**: ブルートフォース攻撃防止
- **レート制限**: API呼び出し制限
- **入力検証**: Pydantic による厳密な検証
- **SQLインジェクション**: SQLAlchemy ORM使用

## 💰 料金・コスト

### 推奨構成
- **Render (無料プラン)**: $0/月
  - FastAPI バックエンド
  - React フロントエンド
  - 自動デプロイ
  
- **シンVPS**: 約1,000円/月
  - 1GB RAM / 1vCPU
  - 30GB SSD (NVMe)
  - PostgreSQL 16

### 合計コスト
**月額約1,000円** で完全なプライバシー保護とエンタープライズレベルのセキュリティを実現

## 🔧 開発

### 技術スタック
- **バックエンド**: FastAPI 0.115.9+ (Python 3.13)
- **フロントエンド**: React 18 + Tailwind CSS
- **データベース**: PostgreSQL 16 + asyncpg
- **認証**: JWT + bcrypt
- **暗号化**: AES-256-GCM + PBKDF2
- **AI**: Groq LLM
- **デプロイ**: Render + VPS

### 開発環境セットアップ
```bash
# 開発モード起動
export APP_ENV=development
export DB_DEBUG=true
python app.py

# フロントエンド開発サーバー
cd frontend
npm start
```

### テスト
```bash
# バックエンドテスト
pytest

# フロントエンドテスト
cd frontend
npm test
```

## 📋 環境変数

### 必須
- `DATABASE_URL` - PostgreSQL接続文字列
- `SECRET_KEY` - JWT署名用秘密鍵 (32文字以上)
- `GROQ_API_KEY` - Groq AI APIキー

### オプション
- `APP_ENV` - 環境 (development/production)
- `PRIVACY_MODE` - プライバシーモード (maximum)
- `OPERATOR_BLIND_ENABLED` - 運営者ブラインド (true)
- `DB_DEBUG` - データベースデバッグ (false)

## 🤝 コントリビューション

1. フォーク
2. フィーチャーブランチ作成 (`git checkout -b feature/amazing-feature`)
3. コミット (`git commit -m 'Add amazing feature'`)
4. プッシュ (`git push origin feature/amazing-feature`)
5. プルリクエスト作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Webフレームワーク
- [React](https://reactjs.org/) - ユーザーインターフェース
- [PostgreSQL](https://www.postgresql.org/) - 堅牢なデータベース
- [Groq](https://groq.com/) - 高速AI推論
- [Render](https://render.com/) - 簡単デプロイプラットフォーム
- [シンVPS](https://www.shin-vps.jp/) - 高性能VPS

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/lilseedabe/x-automation-tool/issues)
- **Wiki**: [詳細ドキュメント](https://github.com/lilseedabe/x-automation-tool/wiki)
- **Security**: セキュリティ問題は非公開で報告してください

---

## ⚠️ 免責事項

このツールは教育・研究目的で提供されています。X（旧Twitter）の利用規約を遵守し、適切に使用してください。自動化による問題は使用者の責任となります。

## 🏆 実績

- ✅ Python 3.13 公式サポート
- ✅ 運営者ブラインド暗号化実装
- ✅ エンタープライズレベルセキュリティ
- ✅ 月額1,000円での高性能運用
- ✅ 完全なプライバシー保護

**🎉 X自動反応ツール - プライバシーファーストなソーシャルメディア自動化プラットフォーム**