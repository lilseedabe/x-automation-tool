/**
 * 🤖 X自動反応ツール - 認証フック
 * 
 * ユーザー認証とセッション管理
 */

import React, { useState, useEffect, createContext, useContext } from 'react';

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
      const savedToken = localStorage.getItem('token');
      
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
        localStorage.setItem('token', 'demo_token_' + Date.now());
        
        setUser(demoUser);
        setIsAuthenticated(true);
        setLoading(false);
        
        return { success: true, user: demoUser };
      }

      // 本番環境での実際のAPI呼び出し
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('ログインに失敗しました');
      }

      const data = await response.json();
      
      // 認証情報を保存
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('token', data.token);
      
      setUser(data.user);
      setIsAuthenticated(true);
      
      return { success: true, user: data.user };
      
    } catch (error) {
      console.error('ログインエラー:', error);
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
      // localStorage をクリア
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      
      setUser(null);
      setIsAuthenticated(false);
      
      // 本番環境ではサーバーサイドのログアウトも実行
      if (process.env.NODE_ENV === 'production') {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
      }
      
    } catch (error) {
      console.error('ログアウトエラー:', error);
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