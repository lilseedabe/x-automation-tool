/**
 * 🤖 X自動反応ツール - アクションキューコンポーネント
 * 
 * 自動実行されるアクションの管理とモニタリング
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Heart,
  Repeat,
  Play,
  Pause,
  X,
  CheckCircle,
  AlertCircle,
  Users,
  MessageSquare,
  TrendingUp,
  Calendar,
  Filter,
  Settings,
  RefreshCw,
  Timer,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../utils/api';

const ActionQueue = () => {
  const { isAuthenticated } = useAuth();
  const [actions, setActions] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const completedActions = actions.filter(action => action.status === 'completed');
  const pendingActions = actions.filter(action => action.status === 'pending');

  // API統合: アクションキュー取得
  const fetchActionQueue = async () => {
    try {
      if (!isAuthenticated) {
        setError('認証が必要です');
        setLoading(false);
        return;
      }

      console.log('📋 アクションキュー取得開始');
      const data = await api.getActionQueue();
      
      console.log('✅ アクションキュー取得完了:', data);
      
      // APIレスポンスをフロントエンド形式に変換
      const formattedActions = (data.actions || []).map(action => ({
        id: action.id,
        type: action.action_type,
        target: action.target_user || action.target,
        content: action.content || action.description,
        scheduledTime: new Date(action.scheduled_time || action.created_at),
        status: action.status,
      }));

      setActions(formattedActions);
      setError(null);
    } catch (error) {
      console.error('❌ アクションキュー取得エラー:', error);
      setError(`データの取得に失敗しました: ${error.message}`);
      // エラー時はデモデータを表示
      setActions([
        {
          id: 'demo-1',
          type: 'like',
          target: '@demo_user',
          content: 'デモ: いいねアクション',
          scheduledTime: new Date(Date.now() + 30000),
          status: 'pending',
        },
        {
          id: 'demo-2',
          type: 'retweet',
          target: '@demo_tech',
          content: 'デモ: リツイートアクション',
          scheduledTime: new Date(Date.now() + 60000),
          status: 'pending',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 初回読み込みと定期更新
  useEffect(() => {
    if (isAuthenticated) {
      fetchActionQueue();
      
      // 30秒ごとに更新
      const interval = setInterval(fetchActionQueue, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    let interval;
    if (isRunning) {
      interval = setInterval(() => {
        const now = new Date();
        setActions(prev => 
          prev.map(action => {
            if (action.status === 'pending' && action.scheduledTime <= now) {
              return { ...action, status: 'completed' };
            }
            return action;
          })
        );
      }, 1000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isRunning]);

  const handleCompleteAction = (actionId) => {
    setActions(prev =>
      prev.map(action =>
        action.id === actionId ? { ...action, status: 'completed' } : action
      )
    );
  };

  const handleRemoveAction = (actionId) => {
    setActions(prev => prev.filter(action => action.id !== actionId));
  };

  const handleToggleQueue = () => {
    setIsRunning(!isRunning);
  };

  const getActionIcon = (type) => {
    switch (type) {
      case 'like':
        return <Heart className="h-4 w-4" />;
      case 'retweet':
        return <Repeat className="h-4 w-4" />;
      case 'reply':
        return <MessageSquare className="h-4 w-4" />;
      case 'follow':
        return <Users className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimeRemaining = (scheduledTime) => {
    const now = new Date();
    const diff = scheduledTime - now;
    
    if (diff <= 0) return '実行中';
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    if (minutes > 0) {
      return `${minutes}分${seconds}秒後`;
    }
    return `${seconds}秒後`;
  };

  const filteredActions = actions.filter(action => {
    if (filter === 'all') return true;
    return action.status === filter;
  });

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Clock className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              アクションキュー
            </h3>
            <p className="text-sm text-gray-500">
              {pendingActions.length}件の待機中アクション
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleToggleQueue}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isRunning
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isRunning ? (
              <>
                <Pause className="h-4 w-4" />
                <span>一時停止</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>開始</span>
              </>
            )}
          </button>
          
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <Settings className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* 統計情報 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-1">
            <Timer className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">待機中</span>
          </div>
          <p className="text-2xl font-bold text-blue-600">
            {pendingActions.length}
          </p>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-1">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">完了</span>
          </div>
          <p className="text-2xl font-bold text-green-600">
            {completedActions.length}
          </p>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-1">
            <TrendingUp className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-900">実行率</span>
          </div>
          <p className="text-2xl font-bold text-purple-600">
            {actions.length > 0 
              ? Math.round((completedActions.length / actions.length) * 100)
              : 0}%
          </p>
        </div>
      </div>

      {/* フィルター */}
      <div className="flex items-center space-x-2 mb-4">
        <Filter className="h-4 w-4 text-gray-400" />
        <div className="flex space-x-1">
          {[
            { key: 'all', label: 'すべて' },
            { key: 'pending', label: '待機中' },
            { key: 'completed', label: '完了' },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === key
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* アクションリスト */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredActions.map((action) => (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${
                    action.type === 'like' ? 'bg-red-100 text-red-600' :
                    action.type === 'retweet' ? 'bg-green-100 text-green-600' :
                    action.type === 'reply' ? 'bg-blue-100 text-blue-600' :
                    'bg-purple-100 text-purple-600'
                  }`}>
                    {getActionIcon(action.type)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {action.target}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(action.status)}`}>
                        {action.status === 'pending' ? '待機中' :
                         action.status === 'completed' ? '完了' : 'エラー'}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-1 line-clamp-1">
                      {action.content}
                    </p>
                    
                    <div className="flex items-center space-x-4 mt-2">
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        <Calendar className="h-3 w-3" />
                        <span>
                          {action.scheduledTime.toLocaleTimeString('ja-JP', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      
                      {action.status === 'pending' && (
                        <div className="flex items-center space-x-1 text-xs text-blue-600">
                          <Clock className="h-3 w-3" />
                          <span>{formatTimeRemaining(action.scheduledTime)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {action.status === 'pending' && (
                    <button
                      onClick={() => handleCompleteAction(action.id)}
                      className="p-1 text-green-600 hover:bg-green-100 rounded transition-colors"
                      title="今すぐ実行"
                    >
                      <Play className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleRemoveAction(action.id)}
                    className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                    title="削除"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredActions.length === 0 && (
        <div className="text-center py-8">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">
            {filter === 'all' 
              ? 'アクションキューは空です'
              : `${filter === 'pending' ? '待機中' : '完了した'}アクションはありません`
            }
          </p>
        </div>
      )}

      {/* フッター */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <RefreshCw className="h-4 w-4" />
          <span>
            {isRunning ? '自動実行中...' : '一時停止中'}
          </span>
        </div>
        
        <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          すべてクリア
        </button>
      </div>
    </div>
  );
};

export default ActionQueue;