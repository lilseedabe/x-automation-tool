/**
 * 🤖 X自動反応ツール - ログインコンポーネント（本番版）
 * 
 * ユーザー認証画面 - 完全実装版
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, UserPlus, Eye, EyeOff, Mail, Lock, User, AlertCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { vpsAPIKeyManager } from '../services/apiKeyManager';
import toast from 'react-hot-toast';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    fullName: ''
  });
  const [errors, setErrors] = useState({});

  // 認証フックを使用
  const { login } = useAuth();

  // フォームバリデーション
  const validateForm = () => {
    const newErrors = {};

    // メールアドレス検証
    if (!formData.email) {
      newErrors.email = 'メールアドレスを入力してください';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '有効なメールアドレスを入力してください';
    }

    // パスワード検証
    if (!formData.password) {
      newErrors.password = 'パスワードを入力してください';
    } else if (formData.password.length < 6) {
      newErrors.password = 'パスワードは6文字以上で入力してください';
    }

    // 新規登録時の追加検証
    if (!isLogin) {
      if (!formData.username) {
        newErrors.username = 'ユーザー名を入力してください';
      } else if (formData.username.length < 3) {
        newErrors.username = 'ユーザー名は3文字以上で入力してください';
      } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
        newErrors.username = 'ユーザー名は英数字とアンダースコアのみ使用できます';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // フォームバリデーション
    if (!validateForm()) {
      toast.error('入力内容をご確認ください');
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      if (isLogin) {
        // ログイン処理
        console.log('ログイン試行:', { email: formData.email });
        
        const result = await login({
          email: formData.email,
          password: formData.password
        });

        if (result.success) {
          toast.success('ログインしました！', {
            duration: 2000,
            icon: '🎉'
          });
          
          // ログイン成功後、VPS PostgreSQLのAPIキー状態を確認
          try {
            const [keyStatus, cachedStatus] = await Promise.all([
              vpsAPIKeyManager.getAPIKeyStatus(),
              vpsAPIKeyManager.checkCachedStatus()
            ]);
            
            if (keyStatus && cachedStatus.has_cached_keys) {
              console.log('✅ VPS APIキー設定済み & キャッシュ済み:', { keyStatus, cachedStatus });
              toast.success('APIキーが利用可能です（VPS管理）', {
                duration: 3000,
                icon: '🔐'
              });
            } else if (keyStatus && !cachedStatus.has_cached_keys) {
              console.log('⚠️ VPS APIキー設定済みだがキャッシュなし:', { keyStatus, cachedStatus });
              toast('APIキーの復号が必要です（パスワード入力）', {
                duration: 4000,
                icon: '🔓'
              });
            } else {
              console.log('⚠️ VPS APIキー未設定:', { keyStatus, cachedStatus });
              toast('APIキーをVPSに保存してください', {
                duration: 4000,
                icon: '⚙️'
              });
            }
          } catch (error) {
            console.warn('VPS APIキー状態確認エラー:', error);
            // エラーが発生してもログインは継続
            toast('APIキー状態確認でエラーが発生しました', {
              duration: 3000,
              icon: '⚠️'
            });
          }
          
          // useAuthフックによってisAuthenticatedが更新され、
          // App.jsxのProtectedRouteで自動的にダッシュボードにリダイレクトされます
        } else {
          console.error('ログインエラー:', result.error);
          toast.error(result.error || 'ログインに失敗しました');
          setErrors({ general: result.error || 'ログインに失敗しました' });
        }
      } else {
        // 新規登録処理
        console.log('新規登録試行:', { 
          username: formData.username, 
          email: formData.email,
          fullName: formData.fullName 
        });

        // 本番環境での新規登録API呼び出し
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: formData.username,
            email: formData.email,
            password: formData.password,
            fullName: formData.fullName || null
          }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
          toast.success('アカウントを作成しました！ログインしてください。', {
            duration: 4000,
            icon: '✅'
          });
          
          // ログインフォームに切り替え
          setIsLogin(true);
          setFormData(prev => ({ 
            ...prev, 
            username: '', 
            fullName: '',
            password: '' // セキュリティのためパスワードもクリア
          }));
        } else {
          console.error('登録エラー:', data);
          const errorMessage = data.detail || data.message || 'アカウント作成に失敗しました';
          toast.error(errorMessage);
          setErrors({ general: errorMessage });
        }
      }
    } catch (error) {
      console.error('認証エラー:', error);
      
      let errorMessage = '通信エラーが発生しました';
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'サーバーに接続できません。しばらく後でお試しください。';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage, {
        duration: 5000
      });
      setErrors({ general: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // エラーをクリア
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const toggleFormMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setFormData({
      email: '',
      password: '',
      username: '',
      fullName: ''
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full"
      >
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
          >
            <span className="text-2xl">🤖</span>
          </motion.div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            X自動反応ツール
          </h1>
          <p className="text-gray-600">
            AI駆動のソーシャルメディア自動化ツール
          </p>
        </div>

        {/* フォームカード */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
        >
          {/* タブ切り替え */}
          <div className="mb-6">
            <div className="flex rounded-lg bg-gray-100 p-1">
              <button
                onClick={() => setIsLogin(true)}
                disabled={isLoading}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  isLogin 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                } ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
              >
                ログイン
              </button>
              <button
                onClick={() => setIsLogin(false)}
                disabled={isLoading}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  !isLogin 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                } ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
              >
                新規登録
              </button>
            </div>
          </div>

          {/* 全般的なエラーメッセージ */}
          {errors.general && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700"
            >
              <AlertCircle size={16} />
              <span className="text-sm">{errors.general}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 新規登録時のみ表示 */}
            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ユーザー名 <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                    <input
                      type="text"
                      name="username"
                      className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                        errors.username ? 'border-red-300 bg-red-50' : 'border-gray-300'
                      }`}
                      placeholder="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      disabled={isLoading}
                      required={!isLogin}
                    />
                  </div>
                  {errors.username && (
                    <p className="mt-1 text-sm text-red-600">{errors.username}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">フルネーム</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                    <input
                      type="text"
                      name="fullName"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="田中 太郎"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>
                </div>
              </>
            )}

            {/* メールアドレス */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                メールアドレス <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="email"
                  name="email"
                  className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    errors.email ? 'border-red-300 bg-red-50' : 'border-gray-300'
                  }`}
                  placeholder="your@email.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  required
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* パスワード */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                パスワード <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  className={`w-full pl-10 pr-10 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    errors.password ? 'border-red-300 bg-red-50' : 'border-gray-300'
                  }`}
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
              {!isLogin && (
                <p className="mt-1 text-xs text-gray-500">6文字以上で入力してください</p>
              )}
            </div>

            {/* 送信ボタン */}
            <motion.button
              whileHover={!isLoading ? { scale: 1.02 } : {}}
              whileTap={!isLoading ? { scale: 0.98 } : {}}
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                isLoading 
                  ? 'bg-gray-400 cursor-not-allowed text-white' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg'
              }`}
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{isLogin ? 'ログイン中...' : 'アカウント作成中...'}</span>
                </>
              ) : isLogin ? (
                <>
                  <LogIn size={16} />
                  ログイン
                </>
              ) : (
                <>
                  <UserPlus size={16} />
                  アカウント作成
                </>
              )}
            </motion.button>
          </form>

          {/* フォーム切り替え */}
          <div className="mt-6 text-center">
            {isLogin ? (
              <p className="text-sm text-gray-600">
                アカウントをお持ちでない方は{' '}
                <button
                  onClick={toggleFormMode}
                  disabled={isLoading}
                  className={`text-blue-600 hover:text-blue-700 font-medium ${
                    isLoading ? 'cursor-not-allowed opacity-50' : ''
                  }`}
                >
                  新規登録
                </button>
              </p>
            ) : (
              <p className="text-sm text-gray-600">
                すでにアカウントをお持ちの方は{' '}
                <button
                  onClick={toggleFormMode}
                  disabled={isLoading}
                  className={`text-blue-600 hover:text-blue-700 font-medium ${
                    isLoading ? 'cursor-not-allowed opacity-50' : ''
                  }`}
                >
                  ログイン
                </button>
              </p>
            )}
          </div>
        </motion.div>

        {/* 機能紹介 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 grid grid-cols-2 gap-4 text-center"
        >
          <div className="p-4 bg-white/80 backdrop-blur rounded-lg">
            <div className="text-2xl mb-2">🧠</div>
            <h3 className="font-semibold text-gray-900 mb-1">AI分析</h3>
            <p className="text-xs text-gray-600">Groq AIによる投稿分析</p>
          </div>
          
          <div className="p-4 bg-white/80 backdrop-blur rounded-lg">
            <div className="text-2xl mb-2">⏰</div>
            <h3 className="font-semibold text-gray-900 mb-1">自動化</h3>
            <p className="text-xs text-gray-600">人間らしいタイミング</p>
          </div>
          
          <div className="p-4 bg-white/80 backdrop-blur rounded-lg">
            <div className="text-2xl mb-2">🚫</div>
            <h3 className="font-semibold text-gray-900 mb-1">安全性</h3>
            <p className="text-xs text-gray-600">ブラックリスト機能</p>
          </div>
          
          <div className="p-4 bg-white/80 backdrop-blur rounded-lg">
            <div className="text-2xl mb-2">👥</div>
            <h3 className="font-semibold text-gray-900 mb-1">マルチユーザー</h3>
            <p className="text-xs text-gray-600">複数アカウント対応</p>
          </div>
        </motion.div>

        {/* フッター */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© {new Date().getFullYear()} X自動反応ツール - AI駆動自動化システム</p>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
