"""
🤖 X自動反応ツール - メインアプリケーション
Python 3.13対応・シンプル版
"""

import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# アプリケーション初期化
app = FastAPI(
    title="X自動反応ツール",
    description="AI搭載のX自動化プラットフォーム - 運営者ブラインド設計",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
async def read_root():
    """ルートエンドポイント - フロントエンド配信"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>🤖 X自動反応ツール</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    max-width: 800px;
                    padding: 40px;
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                }}
                h1 {{ 
                    font-size: 3em; 
                    margin-bottom: 20px; 
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .status {{ 
                    background: rgba(16, 185, 129, 0.2); 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin: 30px 0;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }}
                .feature {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 15px 0;
                }}
                .tech-info {{
                    background: rgba(0, 0, 0, 0.2);
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 30px;
                    font-size: 0.9em;
                }}
                a {{
                    color: #a7f3d0;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 X自動反応ツール</h1>
                
                <div class="status">
                    <h3>✅ サーバー正常稼働中</h3>
                    <p>🚀 FastAPIバックエンド起動完了</p>
                    <p>📱 フロントエンドビルド待機中...</p>
                </div>

                <div class="feature">
                    <h4>🔐 運営者ブラインド設計</h4>
                    <p>ユーザーのAPIキーに運営者が技術的にアクセスできない安全設計</p>
                </div>

                <div class="feature">
                    <h4>🤖 AI搭載自動化</h4>
                    <p>Groq AIによる高度なエンゲージメント分析とスマートターゲティング</p>
                </div>

                <div class="feature">
                    <h4>📊 柔軟なデータ管理</h4>
                    <p>ローカル保存とサーバー保存を選択可能</p>
                </div>

                <div class="tech-info">
                    <p><strong>技術情報:</strong></p>
                    <p>Python {sys.version.split()[0]} | FastAPI | React</p>
                    <p>環境: {os.getenv('APP_ENV', 'development')}</p>
                    <p>フロントエンドビルド: {'✅' if os.path.exists('frontend/build/index.html') else '⏳'}</p>
                </div>

                <div style="margin-top: 30px;">
                    <p><a href="/health">🔍 システム状況</a> | <a href="/api/system/health">📡 API状況</a></p>
                </div>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {{
        "status": "healthy",
        "service": "X自動反応ツール",
        "message": "運営者ブラインド設計でプライバシー保護",
        "python_version": sys.version.split()[0],
        "frontend_built": os.path.exists("frontend/build/index.html"),
        "environment": os.getenv("APP_ENV", "development"),
        "features": [
            "FastAPI バックエンド",
            "React フロントエンド",
            "運営者ブラインド設計",
            "AI搭載分析",
            "柔軟なデータ管理"
        ]
    }}

@app.get("/api/system/health")
async def api_health():
    """API ヘルスチェック"""
    return {{
        "status": "ok",
        "service": "X自動反応ツール API",
        "version": "1.0.0",
        "python": sys.version.split()[0],
        "environment": os.getenv("APP_ENV", "development"),
        "privacy_mode": os.getenv("PRIVACY_MODE", "maximum"),
        "operator_blind": os.getenv("OPERATOR_BLIND_ENABLED", "true"),
        "features_status": {{
            "fastapi": "✅ Running",
            "frontend": "✅ Ready" if os.path.exists("frontend/build/index.html") else "⏳ Building",
            "cors": "✅ Enabled",
            "privacy": "✅ Maximum"
        }}
    }}

@app.get("/api/features")
async def get_features():
    """利用可能機能一覧"""
    return {{
        "core_features": [
            {{
                "name": "運営者ブラインド設計",
                "description": "技術的に運営者がユーザーデータにアクセス不可",
                "status": "active"
            }},
            {{
                "name": "AI分析エンジン",
                "description": "Groq AIによる高度なエンゲージメント分析",
                "status": "ready"
            }},
            {{
                "name": "柔軟なデータ管理",
                "description": "ローカル保存とサーバー保存の選択可能",
                "status": "active"
            }},
            {{
                "name": "X自動化機能",
                "description": "いいね・リポストの安全な自動実行",
                "status": "ready"
            }}
        ],
        "privacy_features": [
            "暗号化ストレージ",
            "自動削除機能", 
            "ユーザー制御",
            "透明性保証"
        ],
        "deployment_info": {{
            "platform": "Render",
            "region": "US West",
            "uptime": "High Availability",
            "cost": "Free Tier Optimized"
        }}
    }}

# フロントエンドルートのフォールバック（SPA対応）
@app.get("/{{path:path}}")
async def serve_frontend(path: str):
    """フロントエンド配信（SPA対応）"""
    # APIパスは除外
    if path.startswith("api/"):
        return {{"error": "API endpoint not found", "path": path}}
    
    # フロントエンドファイルが存在する場合
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return {{
            "message": "フロントエンドビルド中...",
            "requested_path": path,
            "status": "building"
        }}

# 開発用サーバー起動
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)