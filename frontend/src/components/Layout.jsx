/**
 * 🤖 X自動反応ツール - レイアウトコンポーネント
 *
 * アプリケーション全体のレイアウト構造
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Home,
  Bot,
  BarChart3,
  MessageSquare,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  User,
  Shield,
  Clock,
  Target,
  HelpCircle,
  ChevronDown,
  Heart,
  Repeat,
  Zap,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../utils/api';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const [automationStats, setAutomationStats] = useState({
    todayLikes: 0,
    todayRetweets: 0,
    isRunning: false,
    loading: true
  });
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();

  const navigation = [
    {
      name: 'ダッシュボード',
      href: '/',
      icon: Home,
      current: location.pathname === '/',
    },
    {
      name: 'X自動化パネル',
      href: '/automation',
      icon: Zap,
      current: location.pathname === '/automation',
      featured: true, // 新機能として強調
    },
    {
      name: 'AI分析',
      href: '/analysis',
      icon: Bot,
      current: location.pathname === '/analysis',
    },
    {
      name: '投稿管理',
      href: '/posts',
      icon: MessageSquare,
      current: location.pathname === '/posts',
    },
    {
      name: 'アクションキュー',
      href: '/queue',
      icon: Clock,
      current: location.pathname === '/queue',
    },
    {
      name: 'ブラックリスト',
      href: '/blacklist',
      icon: Shield,
      current: location.pathname === '/blacklist',
    },
    {
      name: 'レポート',
      href: '/reports',
      icon: BarChart3,
      current: location.pathname === '/reports',
    },
    {
      name: '設定',
      href: '/settings',
      icon: Settings,
      current: location.pathname === '/settings',
    },
  ];

  // API統計データ取得
  const fetchLayoutStats = async () => {
    if (!isAuthenticated) return;
    
    try {
      // ダッシュボード統計取得（通知数と自動化統計のため）
      const data = await api.getDashboardStats();
      
      // 通知数の計算（キューにあるアクション数をベース）
      setNotificationCount(data.stats?.queued_actions || 0);
      
      // 自動化統計の更新
      setAutomationStats({
        todayLikes: data.stats?.total_likes || 0,
        todayRetweets: data.stats?.total_retweets || 0,
        isRunning: data.is_running || false,
        loading: false
      });
    } catch (error) {
      console.error('レイアウト統計取得エラー:', error);
      setAutomationStats(prev => ({ ...prev, loading: false }));
    }
  };

  // 初回読み込みと定期更新
  useEffect(() => {
    if (isAuthenticated) {
      fetchLayoutStats();
      
      // 1分ごとに更新
      const interval = setInterval(fetchLayoutStats, 60000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const toggleProfileDropdown = () => {
    setProfileDropdownOpen(!profileDropdownOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* サイドバー (デスクトップ) */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-lg">
          {/* ロゴ */}
          <div className="flex h-16 shrink-0 items-center">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Bot className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  X自動反応ツール
                </h1>
                <p className="text-xs text-gray-500">AI Powered</p>
              </div>
            </div>
          </div>

          {/* ナビゲーション */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={`group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors relative ${
                          item.current
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-700 hover:text-blue-700 hover:bg-gray-50'
                        } ${item.featured ? 'ring-2 ring-purple-200 bg-purple-50' : ''}`}
                      >
                        <item.icon
                          className={`h-6 w-6 shrink-0 ${
                            item.current ? 'text-blue-700' : 
                            item.featured ? 'text-purple-700' :
                            'text-gray-400 group-hover:text-blue-700'
                          }`}
                          aria-hidden="true"
                        />
                        <span className={item.featured ? 'text-purple-900 font-bold' : ''}>
                          {item.name}
                        </span>
                        {item.featured && (
                          <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full flex items-center justify-center">
                            <span className="text-xs text-white font-bold">!</span>
                          </span>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* 自動化機能ステータス */}
              <li className="mt-auto">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="flex items-center space-x-1">
                      <Heart className="h-4 w-4 text-red-500" />
                      <Repeat className="h-4 w-4 text-green-500" />
                    </div>
                    <span className="text-sm font-bold text-gray-900">
                      自動化機能
                    </span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-600">今日のいいね:</span>
                      <span className="font-semibold text-red-600">
                        {automationStats.loading ? '--' : `${automationStats.todayLikes}件`}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">今日のリポスト:</span>
                      <span className="font-semibold text-green-600">
                        {automationStats.loading ? '--' : `${automationStats.todayRetweets}件`}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      automationStats.isRunning
                        ? 'bg-green-500 animate-pulse'
                        : 'bg-gray-400'
                    }`}></div>
                    <span className={`text-xs font-medium ${
                      automationStats.isRunning
                        ? 'text-green-700'
                        : 'text-gray-600'
                    }`}>
                      {automationStats.loading
                        ? '確認中...'
                        : automationStats.isRunning
                          ? '稼働中'
                          : '停止中'
                      }
                    </span>
                  </div>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* モバイルサイドバー */}
      {sidebarOpen && (
        <div className="relative z-50 lg:hidden" role="dialog" aria-modal="true">
          <div className="fixed inset-0 bg-gray-900/80" onClick={toggleSidebar}></div>
          <div className="fixed inset-0 flex">
            <div className="relative mr-16 flex w-full max-w-xs flex-1">
              <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                <button type="button" className="-m-2.5 p-2.5" onClick={toggleSidebar}>
                  <span className="sr-only">Close sidebar</span>
                  <X className="h-6 w-6 text-white" aria-hidden="true" />
                </button>
              </div>

              <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
                {/* モバイルロゴ */}
                <div className="flex h-16 shrink-0 items-center">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Bot className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h1 className="text-lg font-bold text-gray-900">
                        X自動反応ツール
                      </h1>
                    </div>
                  </div>
                </div>

                {/* モバイルナビゲーション */}
                <nav className="flex flex-1 flex-col">
                  <ul role="list" className="flex flex-1 flex-col gap-y-7">
                    <li>
                      <ul role="list" className="-mx-2 space-y-1">
                        {navigation.map((item) => (
                          <li key={item.name}>
                            <Link
                              to={item.href}
                              onClick={toggleSidebar}
                              className={`group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 relative ${
                                item.current
                                  ? 'bg-blue-50 text-blue-700'
                                  : 'text-gray-700 hover:text-blue-700 hover:bg-gray-50'
                              } ${item.featured ? 'ring-2 ring-purple-200 bg-purple-50' : ''}`}
                            >
                              <item.icon
                                className={`h-6 w-6 shrink-0 ${
                                  item.current ? 'text-blue-700' : 
                                  item.featured ? 'text-purple-700' :
                                  'text-gray-400 group-hover:text-blue-700'
                                }`}
                                aria-hidden="true"
                              />
                              <span className={item.featured ? 'text-purple-900 font-bold' : ''}>
                                {item.name}
                              </span>
                              {item.featured && (
                                <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full flex items-center justify-center">
                                  <span className="text-xs text-white font-bold">!</span>
                                </span>
                              )}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* メインコンテンツ */}
      <div className="lg:pl-72">
        {/* トップバー */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={toggleSidebar}
          >
            <span className="sr-only">Open sidebar</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>

          {/* セパレーター */}
          <div className="h-6 w-px bg-gray-200 lg:hidden" aria-hidden="true" />

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="relative flex flex-1">
              {/* パンくずリスト */}
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Home className="h-4 w-4" />
                <span>/</span>
                <span className="text-gray-900 font-medium">
                  {navigation.find(item => item.current)?.name || 'ダッシュボード'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* 通知 */}
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 relative"
              >
                <span className="sr-only">View notifications</span>
                <Bell className="h-6 w-6" aria-hidden="true" />
                {notificationCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-xs text-white font-medium">
                      {notificationCount > 99 ? '99+' : notificationCount}
                    </span>
                  </span>
                )}
              </button>

              {/* セパレーター */}
              <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" aria-hidden="true" />

              {/* プロフィールドロップダウン */}
              <div className="relative">
                <button
                  type="button"
                  className="-m-1.5 flex items-center p-1.5"
                  onClick={toggleProfileDropdown}
                >
                  <span className="sr-only">Open user menu</span>
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="hidden lg:block text-left">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.name || 'ユーザー'}
                      </p>
                      <p className="text-xs text-gray-500">管理者</p>
                    </div>
                    <ChevronDown className="hidden lg:block h-4 w-4 text-gray-400" />
                  </div>
                </button>

                {profileDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="absolute right-0 z-10 mt-2.5 w-48 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5"
                  >
                    <Link
                      to="/settings"
                      className="block px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50"
                      onClick={() => setProfileDropdownOpen(false)}
                    >
                      設定
                    </Link>
                    <Link
                      to="/help"
                      className="flex items-center px-3 py-1 text-sm leading-6 text-gray-900 hover:bg-gray-50"
                      onClick={() => setProfileDropdownOpen(false)}
                    >
                      <HelpCircle className="h-4 w-4 mr-2" />
                      ヘルプ
                    </Link>
                    <hr className="my-1" />
                    <button
                      onClick={() => {
                        setProfileDropdownOpen(false);
                        handleLogout();
                      }}
                      className="flex items-center w-full px-3 py-1 text-sm leading-6 text-red-600 hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      ログアウト
                    </button>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* メインコンテンツエリア */}
        <main className="py-10">
          <div className="px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>

      {/* プロフィールドロップダウンの背景クリック */}
      {profileDropdownOpen && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={toggleProfileDropdown}
        ></div>
      )}
    </div>
  );
};

export default Layout;