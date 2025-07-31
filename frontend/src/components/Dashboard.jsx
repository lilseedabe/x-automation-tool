/**
 * 🤖 X自動反応ツール - ダッシュボード
 * 
 * シンプルで実用的なダッシュボード画面
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  Users,
  Heart,
  MessageCircle,
  Repeat,
  Activity,
  Clock,
  Target,
  Zap,
  CheckCircle,
  Bot,
  Settings,
  Play,
  Pause,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState({
    totalLikes: 0,
    totalRetweets: 0,
    totalReplies: 0,
    totalFollowers: 0,
    todayActions: 0,
    queuedActions: 0,
    successRate: 0,
    activeTime: '0分',
    loading: true,
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  // 本番環境用のAPIデータ取得
  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token || !isAuthenticated) {
        setError('認証が必要です');
        return;
      }

      const response = await fetch('/api/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setStats({
        totalLikes: data.total_likes || 0,
        totalRetweets: data.total_retweets || 0,
        totalReplies: data.total_replies || 0,
        totalFollowers: data.total_followers || 0,
        todayActions: data.today_actions || 0,
        queuedActions: data.queued_actions || 0,
        successRate: data.success_rate || 0,
        activeTime: data.active_time || '0分',
        loading: false,
      });

      setRecentActivity(data.recent_activity || []);
      setChartData(data.chart_data || []);
      setIsRunning(data.is_running || false);

    } catch (error) {
      console.error('ダッシュボードデータ取得エラー:', error);
      setError('データの取得に失敗しました');
      setStats(prev => ({ ...prev, loading: false }));
    }
  };

  // 初回読み込みと定期更新
  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
      
      const interval = setInterval(() => {
        fetchDashboardData();
      }, 30000); // 30秒ごとに更新

      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const getActivityIcon = (type) => {
    switch (type) {
      case 'like':
        return <Heart className="h-4 w-4 text-red-500" />;
      case 'retweet':
        return <Repeat className="h-4 w-4 text-green-500" />;
      case 'reply':
        return <MessageCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'たった今';
    if (minutes < 60) return `${minutes}分前`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}時間前`;
    
    const days = Math.floor(hours / 24);
    return `${days}日前`;
  };

  // チャートの最大値を計算
  const getMaxValue = () => {
    const allValues = chartData.flatMap(item => [item.likes, item.retweets, item.replies]);
    return Math.max(...allValues);
  };

  const maxValue = getMaxValue();

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ダッシュボード
          </h1>
          <p className="text-gray-600">
            X自動反応ツールの活動状況
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
            isRunning 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isRunning ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">
              {isRunning ? '稼働中' : '停止中'}
            </span>
          </div>
          
          <button 
            onClick={() => setIsRunning(!isRunning)}
            className={`p-2 rounded-lg transition-colors ${
              isRunning 
                ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                : 'bg-green-100 text-green-600 hover:bg-green-200'
            }`}
          >
            {isRunning ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </button>
          
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <Settings className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: '今日のアクション',
            value: stats.todayActions,
            change: '+12%',
            icon: Activity,
            color: 'blue',
          },
          {
            title: '総いいね数',
            value: stats.totalLikes.toLocaleString(),
            change: '+8%',
            icon: Heart,
            color: 'red',
          },
          {
            title: '成功率',
            value: `${stats.successRate}%`,
            change: '優秀',
            icon: Target,
            color: 'green',
          },
          {
            title: '待機中',
            value: stats.queuedActions,
            change: 'アクション',
            icon: Clock,
            color: 'yellow',
          },
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className={`text-sm mt-1 ${
                  stat.color === 'green' ? 'text-green-600' : 'text-blue-600'
                }`}>
                  {stat.change}
                </p>
              </div>
              <div className={`p-3 rounded-lg ${
                stat.color === 'blue' ? 'bg-blue-100' :
                stat.color === 'red' ? 'bg-red-100' :
                stat.color === 'green' ? 'bg-green-100' : 'bg-yellow-100'
              }`}>
                <stat.icon className={`h-6 w-6 ${
                  stat.color === 'blue' ? 'text-blue-600' :
                  stat.color === 'red' ? 'text-red-600' :
                  stat.color === 'green' ? 'text-green-600' : 'text-yellow-600'
                }`} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* メインコンテンツ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* エンゲージメントチャート - 修正版 */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  週間エンゲージメント
                </h3>
                <p className="text-sm text-gray-500">
                  過去7日間のアクティビティ
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-sm text-gray-600">いいね</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">リツイート</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-600">返信</span>
              </div>
            </div>
          </div>

          {/* 修正されたチャート */}
          <div className="relative">
            <div className="h-64 flex items-end justify-between space-x-1 p-4 bg-gray-50 rounded-lg overflow-hidden">
              {chartData.map((item, index) => (
                <div key={item.name} className="flex-1 flex flex-col items-center max-w-16">
                  <div className="w-full relative mb-2 flex flex-col justify-end" style={{ height: '200px' }}>
                    {/* いいね */}
                    <div
                      className="w-full bg-red-500 mb-1 rounded-sm"
                      style={{ 
                        height: `${Math.max(4, (item.likes / maxValue) * 180)}px`,
                        maxHeight: '180px'
                      }}
                    ></div>
                    {/* リツイート */}
                    <div
                      className="w-full bg-green-500 mb-1 rounded-sm"
                      style={{ 
                        height: `${Math.max(4, (item.retweets / maxValue) * 180)}px`,
                        maxHeight: '180px'
                      }}
                    ></div>
                    {/* 返信 */}
                    <div
                      className="w-full bg-blue-500 rounded-sm"
                      style={{ 
                        height: `${Math.max(4, (item.replies / maxValue) * 180)}px`,
                        maxHeight: '180px'
                      }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-600 font-medium">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 最近のアクティビティ */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-green-100 rounded-lg">
              <Zap className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                最近のアクティビティ
              </h3>
              <p className="text-sm text-gray-500">
                リアルタイム更新
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
              >
                <div className="p-1 bg-white rounded shadow-sm">
                  {getActivityIcon(activity.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 text-sm">
                      {activity.target}
                    </span>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  </div>
                  <p className="text-sm text-gray-600 truncate">
                    {activity.content}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatTimeAgo(activity.timestamp)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <button className="w-full mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium">
            すべて表示
          </button>
        </div>
      </div>

      {/* AI分析サマリー */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Bot className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              AI分析サマリー
            </h3>
            <p className="text-sm text-gray-500">
              今日のパフォーマンス分析
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">エンゲージメント率</p>
              <p className="text-lg font-semibold text-green-600">+15.3%</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">リーチ数</p>
              <p className="text-lg font-semibold text-blue-600">12.4K</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Target className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">品質スコア</p>
              <p className="text-lg font-semibold text-purple-600">92/100</p>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start space-x-3">
            <Bot className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900 mb-1">
                AI推奨事項
              </h4>
              <p className="text-sm text-blue-800">
                午後7-9時の投稿でエンゲージメントが20%向上しています。
                明日はこの時間帯での活動を増やすことをお勧めします。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* X自動化機能の状況 */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Bot className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                X自動化機能
              </h3>
              <p className="text-sm text-gray-500">
                いいね♡とリポストの自動実行状況
              </p>
            </div>
          </div>
          
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isRunning 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {isRunning ? '自動実行中' : '停止中'}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 flex items-center">
              <Heart className="h-4 w-4 text-red-500 mr-2" />
              自動いいね機能
            </h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">今日の実行数</span>
                <span className="font-semibold text-red-600">{stats.totalLikes}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">成功率</span>
                <span className="font-semibold text-green-600">94.2%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">待機中</span>
                <span className="font-semibold text-blue-600">8件</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 flex items-center">
              <Repeat className="h-4 w-4 text-green-500 mr-2" />
              自動リポスト機能
            </h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">今日の実行数</span>
                <span className="font-semibold text-green-600">{stats.totalRetweets}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">成功率</span>
                <span className="font-semibold text-green-600">91.8%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">待機中</span>
                <span className="font-semibold text-blue-600">4件</span>
              </div>
            </div>
          </div>
        </div>

        {!isRunning && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
              <p className="text-sm text-yellow-800">
                自動化機能が停止中です。開始ボタンをクリックして自動いいね・リポストを再開してください。
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;