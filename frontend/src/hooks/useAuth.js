/**
 * 🤖 X自動反応ツール - 認証フック（APIクライアント対応版）
 *
 * ユーザー認証とセッション管理
 */

import React, { useState, useEffect, createContext, useContext } from 'react';
import apiClient from '../utils/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // 開発環境では自動的にデモユーザーでログイン
    if (process.env.NODE_ENV === 'development') {
      setTimeout(() => {
        const demoUser = {
          id: 'demo_user',
          name: 'デモユーザー',
          email: 'demo@example.com',
          twitter_username: '@demo_user',
          avatar: null,
          plan: 'premium',
          settings: {
            autoLike: true,
            autoRetweet: true,
            autoReply: false,
            dailyLimit: 100,
            timezone: 'Asia/Tokyo',
          }
        };
        
        setUser(demoUser);
        setIsAuthenticated(true);
        setLoading(false);
      }, 1000); // 1秒後にログイン完了
    } else {
      // 本番環境では通常の認証フロー
      checkAuthStatus();
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      // localStorage から認証情報を確認
      const savedUser = localStorage.getItem('user');
      const savedToken = localStorage.getItem('access_token'); // 🔧 キー名を修正
      
      if (savedUser && savedToken) {
        setUser(JSON.parse(savedUser));
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('認証状態の確認中にエラーが発生しました:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    setLoading(true);
    
    try {
      // デモ用：任意の認証情報でログインを許可
      if (process.env.NODE_ENV === 'development') {
        const demoUser = {
          id: 'demo_user',
          name: 'デモユーザー',
          email: credentials.email || 'demo@example.com',
          twitter_username: '@demo_user',
          avatar: null,
          plan: 'premium',
          settings: {
            autoLike: true,
            autoRetweet: true,
            autoReply: false,
            dailyLimit: 100,
            timezone: 'Asia/Tokyo',
          }
        };
        
        // localStorage に保存
        localStorage.setItem('user', JSON.stringify(demoUser));
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        
        setUser(demoUser);
        setIsAuthenticated(true);
        setLoading(false);
        
        return { success: true, user: demoUser };
      }

      // 🔧 APIクライアントを使用したログイン
      console.log('🔗 API呼び出し開始:', credentials);
      
      const data = await apiClient.login(credentials);
      console.log('📋 レスポンスデータ:', data);
      
      // 🔧 認証情報を正しく保存
      if (data.access_token && data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        setUser(data.user);
        setIsAuthenticated(true);
        
        console.log('✅ ログイン成功:', data.user.username);
        return { success: true, user: data.user };
      } else {
        throw new Error('レスポンスデータが不正です');
      }
      
    } catch (error) {
      console.error('❌ ログインエラー:', error);
      return { 
        success: false, 
        error: error.message || 'ログインに失敗しました' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      console.log('👋 ログアウト処理開始');
      
      // 🔧 修正: トークンを削除前に取得
      const token = localStorage.getItem('access_token');
      console.log('🎫 使用するトークン:', token ? `${token.substring(0, 20)}...` : 'なし');
      
      // 本番環境ではサーバーサイドのログアウトも実行
      if (process.env.NODE_ENV === 'production' && token && token !== 'null') {
        try {
          console.log('📡 サーバーログアウト実行');
          await apiClient.logout();
          console.log('✅ サーバーログアウト成功');
        } catch (fetchError) {
          console.warn('⚠️ サーバーログアウトエラー:', fetchError.message);
        }
      }
      
      // 🔧 ローカルストレージをクリア（サーバー処理後）
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      setUser(null);
      setIsAuthenticated(false);
      
      console.log('✅ ログアウト完了');
      
    } catch (error) {
      console.error('❌ ログアウトエラー:', error);
      // エラーでもローカルの状態はクリア
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');  
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
  };

  return React.createElement(AuthContext.Provider, { value }, children);
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default useAuth;
