/**
 * 🤖 X自動反応ツール - エラーバウンダリー
 * 
 * アプリケーション全体のエラーハンドリング
 */

import React from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      isMetaMaskError: false 
    };
  }

  static getDerivedStateFromError(error) {
    // MetaMaskエラーかどうかを判定
    const isMetaMaskError = error?.message?.includes?.('MetaMask') || 
                           error?.stack?.includes?.('chrome-extension') ||
                           error?.stack?.includes?.('metamask');
    
    return { 
      hasError: true,
      isMetaMaskError 
    };
  }

  componentDidCatch(error, errorInfo) {
    // MetaMaskエラーの場合はログに記録するだけ
    if (error?.message?.includes?.('MetaMask') || 
        error?.stack?.includes?.('chrome-extension') ||
        error?.stack?.includes?.('metamask')) {
      console.warn('MetaMask関連エラーを検出しましたが、アプリケーションには影響ありません:', error);
      this.setState({ 
        hasError: false, // MetaMaskエラーはアプリに影響させない
        isMetaMaskError: true 
      });
      return;
    }

    console.error('エラーバウンダリーでエラーをキャッチしました:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
      hasError: true,
      isMetaMaskError: false
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    // MetaMaskエラーの場合は通常通りレンダリング
    if (this.state.isMetaMaskError && !this.state.hasError) {
      return this.props.children;
    }

    // アプリケーションエラーの場合のみエラー画面を表示
    if (this.state.hasError && !this.state.isMetaMaskError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
            {/* エラーアイコン */}
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>

            {/* エラーメッセージ */}
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              問題が発生しました
            </h1>
            
            <p className="text-gray-600 mb-6">
              申し訳ございません。予期しないエラーが発生しました。
              ページを再読み込みするか、ホームに戻ってお試しください。
            </p>

            {/* アクションボタン */}
            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-5 h-5" />
                <span>ページを再読み込み</span>
              </button>
              
              <button
                onClick={this.handleGoHome}
                className="w-full flex items-center justify-center space-x-2 bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Home className="w-5 h-5" />
                <span>ホームに戻る</span>
              </button>
            </div>

            {/* エラー詳細（開発環境のみ） */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 flex items-center space-x-2">
                  <Bug className="w-4 h-4" />
                  <span>エラー詳細（開発用）</span>
                </summary>
                <div className="mt-3 p-3 bg-gray-100 rounded text-xs font-mono overflow-auto max-h-32">
                  <div className="text-red-600 font-semibold mb-2">
                    {this.state.error.toString()}
                  </div>
                  <div className="text-gray-600">
                    {this.state.errorInfo.componentStack}
                  </div>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// MetaMaskエラーを無視するためのグローバルエラーハンドラー
if (typeof window !== 'undefined') {
  const originalErrorHandler = window.onerror;
  
  window.onerror = (message, source, lineno, colno, error) => {
    // MetaMask関連のエラーは無視
    if (typeof message === 'string' && 
        (message.includes('MetaMask') || 
         message.includes('chrome-extension') ||
         source?.includes?.('chrome-extension'))) {
      console.warn('MetaMask関連エラーを検出しましたが、無視します:', message);
      return true; // エラーを処理済みとしてマーク
    }
    
    // その他のエラーは元のハンドラーに委譲
    if (originalErrorHandler) {
      return originalErrorHandler(message, source, lineno, colno, error);
    }
    
    return false;
  };

  // Promise の unhandled rejection も処理
  window.addEventListener('unhandledrejection', (event) => {
    if (event.reason?.message?.includes?.('MetaMask') ||
        event.reason?.stack?.includes?.('chrome-extension')) {
      console.warn('MetaMask関連のPromise rejectionを検出しましたが、無視します:', event.reason);
      event.preventDefault(); // デフォルトの処理を防ぐ
    }
  });
}

export default ErrorBoundary;