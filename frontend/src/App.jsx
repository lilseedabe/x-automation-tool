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