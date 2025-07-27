/**
 * 🤖 X自動反応ツール - メインエントリーポイント
 * 
 * Reactアプリケーションの初期化とレンダリング
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// React Query DevToolsをコメントアウト（不要なため）
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

import './styles/index.css';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import reportWebVitals from './reportWebVitals';

// React Query設定
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5分
    },
  },
});

// MetaMaskエラーを完全に無視するグローバル設定
const suppressMetaMaskErrors = () => {
  // console.error をオーバーライドしてMetaMask関連エラーをフィルタ
  const originalConsoleError = console.error;
  console.error = (...args) => {
    const message = args.join(' ');
    if (message.includes('MetaMask') || 
        message.includes('chrome-extension') || 
        message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn')) {
      // MetaMask関連エラーは表示しない
      return;
    }
    originalConsoleError.apply(console, args);
  };

  // console.warn も同様に処理
  const originalConsoleWarn = console.warn;
  console.warn = (...args) => {
    const message = args.join(' ');
    if (message.includes('MetaMask') || 
        message.includes('chrome-extension') ||
        message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn')) {
      // MetaMask関連警告は表示しない
      return;
    }
    originalConsoleWarn.apply(console, args);
  };
};

// MetaMaskエラー抑制を初期化
suppressMetaMaskErrors();

// ルートコンテナを取得
const container = document.getElementById('root');
const root = createRoot(container);

// アプリケーションをレンダリング
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
        
        {/* 通知システム */}
        <Toaster
          position="top-right"
          reverseOrder={false}
          gutter={8}
          containerClassName=""
          containerStyle={{}}
          toastOptions={{
            // デフォルト設定
            className: '',
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            // 成功通知
            success: {
              duration: 3000,
              theme: {
                primary: 'green',
                secondary: 'black',
              },
            },
            // エラー通知
            error: {
              duration: 5000,
              theme: {
                primary: 'red',
                secondary: 'black',
              },
            },
          }}
        />
        
        {/* React Query DevToolsを完全に削除 */}
        {/* 
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
        */}
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// パフォーマンス測定
reportWebVitals((metric) => {
  // MetaMask関連のメトリクスは除外
  if (metric.name && !metric.name.includes('MetaMask')) {
    console.log('Performance metric:', metric);
  }
});

// 追加のMetaMaskエラー処理
document.addEventListener('DOMContentLoaded', () => {
  // MetaMask関連のDOMエラーを無視
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // MetaMask関連の要素があれば非表示にする
            const metaMaskElements = node.querySelectorAll('[data-metamask], [class*="metamask"]');
            metaMaskElements.forEach((element) => {
              element.style.display = 'none';
            });
          }
        });
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});

// Service Workerのエラーハンドリング
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('error', (event) => {
    if (event.error?.message?.includes?.('MetaMask')) {
      // MetaMask関連のService Workerエラーは無視
      event.preventDefault();
    }
  });
}

export default App;