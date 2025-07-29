"""
🤖 X自動反応ツール - シンプル版FastAPIメイン
Python 3.13対応版
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
    description="AI搭載のX自動化プラットフォーム",
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
    """ルートエンドポイント"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return HTMLResponse("""
        <html>
            <head>
                <title>🤖 X自動反応ツール</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        margin: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        flex-direction: column;
                    }
                    .container {
                        max-width: 600px;
                        padding: 40px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }
                    h1 { font-size: 2.5em; margin-bottom: 20px; }
                    p { font-size: 1.2em; margin-bottom: 15px; }
                    .status { 
                        background: rgba(16, 185, 129, 0.2); 
                        padding: 15px; 
                        border-radius: 10px; 
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 X自動反応ツール</h1>
                    <div class="status">
                        <p>✅ FastAPIサーバーが正常に起動しました</p>
                        <p>🚀 バックエンドAPI稼働中</p>
                        <p>📱 フロントエンドをビルド中...</p>
                    </div>
                    <p>AI搭載のX自動化プラットフォーム</p>
                    <p>運営者ブラインド設計でプライバシー保護</p>
                    <p><small>Python {sys.version}</small></p>
                </div>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "message": "X自動反応ツール - API稼働中",
        "python_version": sys.version,
        "frontend_built": os.path.exists("frontend/build/index.html")
    }

@app.get("/api/system/health")
async def api_health():
    """API ヘルスチェック"""
    return {
        "status": "ok",
        "service": "X自動反応ツール",
        "version": "1.0.0",
        "python": sys.version.split()[0],
        "environment": os.getenv("APP_ENV", "development")
    }

# フロントエンドルートのフォールバック
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """フロントエンド配信（SPA対応）"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    else:
        return {"message": f"Frontend not built yet. Requested path: {path}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)