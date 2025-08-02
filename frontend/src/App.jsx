/**
 * 🤖 X自動反応ツール - メインアプリケーション
 * 
 * React Router とグローバル状態管理の設定
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';

// Components
import Layout from './components/Layout';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import PostInput from './components/PostInput';
import ActionQueue from './components/ActionQueue';
import AIAnalysis from './components/AIAnalysis';
import BlacklistManager from './components/BlacklistManager';
import UserSettings from './components/UserSettings';
import AutomationPanel from './components/AutomationPanel';
import LoadingSpinner from './components/LoadingSpinner';
import FavoriteUsersManager from './components/FavoriteUsersManager'; // 追加

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (ログイン済みの場合はダッシュボードへリダイレクト)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return !isAuthenticated ? children : <Navigate to="/" replace />;
};

// Posts Page (Dashboard + PostInput)
const PostsPage = () => {
  const handlePost = (postData) => {
    console.log('新しい投稿:', postData);
    // ここで実際の投稿処理を実装
  };

  const handleAnalyze = (analysis) => {
    console.log('AI分析結果:', analysis);
  };

  return (
    <div className="space-y-6">
      <PostInput onPost={handlePost} onAnalyze={handleAnalyze} />
      <AIAnalysis />
    </div>
  );
};

// Reports Page (統計とレポート)
const ReportsPage = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          📊 詳細レポート
        </h2>
        <p className="text-gray-600">
          詳細な統計とパフォーマンス分析がここに表示されます。
        </p>
      </div>
    </div>
  );
};

// Help Page
const HelpPage = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          ❓ ヘルプ・サポート
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* よくある質問 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">よくある質問</h3>
            
            <div className="space-y-3">
              <details className="bg-gray-50 rounded-lg p-4">
                <summary className="font-medium text-gray-900 cursor-pointer">
                  自動化機能はどのように動作しますか？
                </summary>
                <p className="mt-2 text-sm text-gray-600">
                  X APIを使用して、設定されたキーワードや条件に基づいて自動的にいいねやリツイートを実行します。
                  レート制限を遵守し、安全に動作します。
                </p>
              </details>
              
              <details className="bg-gray-50 rounded-lg p-4">
                <summary className="font-medium text-gray-900 cursor-pointer">
                  APIキーはどのように保護されますか？
                </summary>
                <p className="mt-2 text-sm text-gray-600">
                  すべてのAPIキーは運営者ブラインド設計により暗号化保存され、
                  運営者でも閲覧することはできません。
                </p>
              </details>
              
              <details className="bg-gray-50 rounded-lg p-4">
                <summary className="font-medium text-gray-900 cursor-pointer">
                  AI分析はどの程度正確ですか？
                </summary>
                <p className="mt-2 text-sm text-gray-600">
                  Groq AIを使用した高精度な分析を提供していますが、
                  あくまで参考として活用してください。
                </p>
              </details>
            </div>
          </div>
          
          {/* 使い方ガイド */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">使い方ガイド</h3>
            
            <div className="space-y-3">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">1. 初期設定</h4>
                <p className="text-sm text-blue-800">
                  設定ページでX APIキーを登録し、自動化の条件を設定します。
                </p>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">2. 自動化開始</h4>
                <p className="text-sm text-green-800">
                  自動化パネルで機能を有効にし、対象キーワードを設定します。
                </p>
              </div>
              
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 mb-2">3. 分析・最適化</h4>
                <p className="text-sm text-purple-800">
                  AI分析結果を確認し、設定を最適化してパフォーマンスを向上させます。
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* 連絡先情報 */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">サポート</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">
              その他のご質問やサポートが必要な場合：
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• システム稼働状況：<code>/health</code> エンドポイントで確認</li>
              <li>• API文書：<code>/api/docs</code> で詳細確認</li>
              <li>• プライバシー保護：運営者ブラインド設計により完全保護</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Routes
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } 
      />
      
      {/* Protected Routes */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/automation" 
        element={
          <ProtectedRoute>
            <Layout>
              <AutomationPanel />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analysis" 
        element={
          <ProtectedRoute>
            <Layout>
              <AIAnalysis />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/posts" 
        element={
          <ProtectedRoute>
            <Layout>
              <PostsPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/queue" 
        element={
          <ProtectedRoute>
            <Layout>
              <ActionQueue />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/blacklist" 
        element={
          <ProtectedRoute>
            <Layout>
              <BlacklistManager />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/reports" 
        element={
          <ProtectedRoute>
            <Layout>
              <ReportsPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <Layout>
              <UserSettings />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      <Route
        path="/help"
        element={
          <ProtectedRoute>
            <Layout>
              <HelpPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// Main App Component
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;