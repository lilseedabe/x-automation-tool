/**
 * 🤖 X自動反応ツール - ログインコンポーネント
 * 
 * ユーザー認証画面
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, UserPlus, Eye, EyeOff, Mail, Lock, User } from 'lucide-react';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    fullName: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // 認証処理の実装
    console.log('Form submitted:', formData);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
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
          className="card"
        >
          <div className="card-header">
            <div className="flex rounded-lg bg-gray-100 p-1">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  isLogin 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ログイン
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                  !isLogin 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                新規登録
              </button>
            </div>
          </div>

          <div className="card-body">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 新規登録時のみ表示 */}
              {!isLogin && (
                <>
                  <div className="form-group">
                    <label className="form-label">ユーザー名</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                      <input
                        type="text"
                        name="username"
                        className="form-input pl-10"
                        placeholder="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">フルネーム</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                      <input
                        type="text"
                        name="fullName"
                        className="form-input pl-10"
                        placeholder="田中 太郎"
                        value={formData.fullName}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                </>
              )}

              {/* メールアドレス */}
              <div className="form-group">
                <label className="form-label">メールアドレス</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="email"
                    name="email"
                    className="form-input pl-10"
                    placeholder="your@email.com"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              {/* パスワード */}
              <div className="form-group">
                <label className="form-label">パスワード</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    className="form-input pl-10 pr-10"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* 送信ボタン */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                className="w-full btn btn-primary flex items-center justify-center gap-2"
              >
                {isLogin ? (
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

            {/* 追加情報 */}
            <div className="mt-6 text-center">
              {isLogin ? (
                <p className="text-sm text-gray-600">
                  アカウントをお持ちでない方は{' '}
                  <button
                    onClick={() => setIsLogin(false)}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    新規登録
                  </button>
                </p>
              ) : (
                <p className="text-sm text-gray-600">
                  すでにアカウントをお持ちの方は{' '}
                  <button
                    onClick={() => setIsLogin(true)}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    ログイン
                  </button>
                </p>
              )}
            </div>
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