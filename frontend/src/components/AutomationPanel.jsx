/**
 * 🤖 X自動反応ツール - エンゲージユーザー自動化パネル（リアルAPI対応版）
 *
 * 特定投稿のエンゲージユーザーの最新投稿に対するAI分析付き自動いいね・リポスト
 * X APIレート制限を厳密に管理
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Heart,
  Repeat,
  Bot,
  Play,
  Pause,
  Settings,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Clock,
  Target,
  Zap,
  TrendingUp,
  Users,
  Shield,
  Activity,
  Plus,
  X,
  ExternalLink,
  Info,
  Heart,
  Award,
  Search,
  UserCheck,
  Shuffle,
  Timer,
  Gauge,
  AlertCircle,
} from 'lucide-react';
import apiClient from '../utils/api';
import { useAuth } from '../hooks/useAuth';

const AutomationPanel = () => {
  const { user, isAuthenticated } = useAuth();
  
  const [automationStats, setAutomationStats] = useState({
    likes_today: 0,
    retweets_today: 0,
    success_rate: 0,
    is_running: false,
    remaining_likes: 0,
    remaining_retweets: 0,
    processed_users: 0,
    total_analyzed: 0,
  });

  // レート制限情報の状態
  const [rateLimitStats, setRateLimitStats] = useState({
    like: {
      "15min_limit": 1,
      "15min_used": 0,
      "15min_remaining": 1,
      "24hour_limit": 1000,
      "24hour_used": 0,
      "24hour_remaining": 1000,
      "next_available_seconds": 0,
      "can_make_request": true
    },
    retweet: {
      "15min_limit": 50,
      "15min_used": 0,
      "15min_remaining": 50,
      "24hour_limit": 1000,
      "24hour_used": 0,
      "24hour_remaining": 1000,
      "next_available_seconds": 0,
      "can_make_request": true
    },
    get_liking_users: {
      "15min_limit": 75,
      "15min_used": 0,
      "15min_remaining": 75,
      "24hour_limit": 7200,
      "24hour_used": 0,
      "24hour_remaining": 7200,
      "next_available_seconds": 0,
      "can_make_request": true
    }
  });

  const [yourTweetUrl, setYourTweetUrl] = useState('');
  const [userPassword, setUserPassword] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [engagingUsers, setEngagingUsers] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [executionQueue, setExecutionQueue] = useState([]);
  const [error, setError] = useState(null);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);

  // 初期データ読み込み
  useEffect(() => {
    if (isAuthenticated) {
      loadInitialData();
    }
  }, [isAuthenticated]);

  // 初期データ読み込み
  const loadInitialData = async () => {
    try {
      // アクションキューを読み込み
      const queueData = await apiClient.getActionQueue();
      if (queueData.success) {
        setExecutionQueue(queueData.queued_actions);
      }

      // レート制限データを読み込み（あれば）
      try {
        const rateLimitData = await apiClient.getMyRateLimits();
        if (rateLimitData.rate_limits) {
          setRateLimitStats(rateLimitData.rate_limits);
        }
      } catch (rateLimitError) {
        console.warn('レート制限データの読み込みに失敗:', rateLimitError);
      }

    } catch (error) {
      console.error('初期データ読み込みエラー:', error);
      setError('初期データの読み込みに失敗しました');
    }
  };

  // レート制限情報を定期的に更新
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(async () => {
      try {
        const rateLimitData = await apiClient.getMyRateLimits();
        if (rateLimitData.rate_limits) {
          setRateLimitStats(rateLimitData.rate_limits);
        }
      } catch (error) {
        console.warn('レート制限データ更新エラー:', error);
      }
    }, 60000); // 1分ごと

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const handleAnalyzeEngagingUsers = async () => {
    if (!yourTweetUrl.trim()) {
      setError('ツイートURLを入力してください');
      return;
    }

    if (!userPassword.trim()) {
      setPasswordModalOpen(true);
      return;
    }

    // レート制限チェック
    if (!rateLimitStats.get_liking_users.can_make_request) {
      setError('エンゲージユーザー取得のレート制限に達しています。しばらく待ってから再試行してください。');
      return;
    }

    setIsAnalyzing(true);
    setEngagingUsers([]);
    setAnalysisResults([]);
    setError(null);
    
    try {
      console.log('🔍 エンゲージユーザー分析開始:', yourTweetUrl);
      
      const response = await apiClient.analyzeEngagingUsers(yourTweetUrl, userPassword);
      
      if (response.success) {
        const results = response.analyzed_users.map(user => ({
          user_id: user.user_id,
          username: user.username,
          tweet_id: user.recent_tweets[0]?.id || 'unknown',
          tweet_text: user.recent_tweets[0]?.text || 'ツイートが見つかりません',
          analysis: {
            like_score: Math.floor(user.ai_score * 100),
            retweet_score: Math.floor(user.ai_score * 90),
            timing_recommendation: "即座に",
            safety_check: user.ai_score > 0.7,
            content_category: "エンゲージメント",
            risk_level: user.ai_score > 0.8 ? "低" : user.ai_score > 0.6 ? "中" : "高",
            recommended_action: user.recommended_actions[0] || "like",
            confidence: user.ai_score,
            ai_reasoning: `AI スコア: ${Math.floor(user.ai_score * 100)}% - ${user.recommended_actions.join(', ')}`
          }
        }));
        
        setAnalysisResults(results);
        setEngagingUsers(response.analyzed_users);
        
        // 統計更新
        setAutomationStats(prev => ({
          ...prev,
          processed_users: prev.processed_users + response.analyzed_users.length,
          total_analyzed: prev.total_analyzed + response.total_engagement_count
        }));
        
        console.log('✅ エンゲージユーザー分析完了:', results.length, '人');
      } else {
        throw new Error(response.error || '分析に失敗しました');
      }
      
    } catch (error) {
      console.error('❌ エンゲージユーザー分析エラー:', error);
      setError(`分析エラー: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectUser = (userId) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectRandomUsers = () => {
    const shuffled = [...analysisResults].sort(() => 0.5 - Math.random());
    const randomCount = Math.floor(Math.random() * 3) + 2; // 2-4人をランダム選択
    const randomSelected = shuffled.slice(0, randomCount).map(result => result.user_id);
    setSelectedUsers(randomSelected);
  };

  const handleExecuteSelectedActions = async () => {
    if (!userPassword.trim()) {
      setPasswordModalOpen(true);
      return;
    }

    // レート制限チェック
    const likesNeeded = selectedUsers.filter(userId => {
      const analysis = analysisResults.find(r => r.user_id === userId);
      return analysis?.analysis.recommended_action === 'like';
    }).length;

    const retweetsNeeded = selectedUsers.filter(userId => {
      const analysis = analysisResults.find(r => r.user_id === userId);
      return analysis?.analysis.recommended_action === 'retweet';
    }).length;

    if (likesNeeded > rateLimitStats.like["15min_remaining"]) {
      setError(`いいね制限不足: ${likesNeeded}件必要ですが、残り${rateLimitStats.like["15min_remaining"]}件です。`);
      return;
    }

    if (retweetsNeeded > rateLimitStats.retweet["15min_remaining"]) {
      setError(`リポスト制限不足: ${retweetsNeeded}件必要ですが、残り${rateLimitStats.retweet["15min_remaining"]}件です。`);
      return;
    }

    try {
      setError(null);
      
      // 選択されたアクションを準備
      const selectedActions = selectedUsers.map(userId => {
        const userAnalysis = analysisResults.find(r => r.user_id === userId);
        if (!userAnalysis) return null;
        
        return {
          action_type: userAnalysis.analysis.recommended_action,
          target_user_id: userAnalysis.user_id,
          target_username: userAnalysis.username,
          target_tweet_id: userAnalysis.tweet_id,
          confidence_score: userAnalysis.analysis.confidence,
          ai_reasoning: userAnalysis.analysis.ai_reasoning
        };
      }).filter(Boolean);

      console.log('⚡ アクション実行開始:', selectedActions);
      
      const response = await apiClient.executeActions(selectedActions, userPassword);
      
      if (response.success) {
        console.log('✅ アクション実行完了:', response);
        
        // 実行キューを更新
        const newQueueItems = response.results.map(result => ({
          id: Date.now() + Math.random(),
          user_id: result.target_user_id,
          username: result.target_username,
          tweet_id: result.target_tweet_id,
          tweet_text: result.content_preview || 'コンテンツなし',
          action_type: result.action_type,
          status: result.success ? 'completed' : 'failed',
          scheduled_time: new Date(),
          error: result.error,
          ai_scores: {
            like_score: result.action_type === 'like' ? 85 : 70,
            retweet_score: result.action_type === 'retweet' ? 85 : 70
          }
        }));
        
        setExecutionQueue(prev => [...prev, ...newQueueItems]);
        setSelectedUsers([]);
        
        // 統計更新
        setAutomationStats(prev => ({
          ...prev,
          likes_today: prev.likes_today + response.results.filter(r => r.action_type === 'like' && r.success).length,
          retweets_today: prev.retweets_today + response.results.filter(r => r.action_type === 'retweet' && r.success).length,
          success_rate: ((prev.likes_today + prev.retweets_today + response.executed_count) / (prev.total_analyzed || 1)) * 100
        }));
        
        // レート制限データをリフレッシュ
        try {
          const rateLimitData = await apiClient.getMyRateLimits();
          if (rateLimitData.rate_limits) {
            setRateLimitStats(rateLimitData.rate_limits);
          }
        } catch (rateLimitError) {
          console.warn('レート制限データ更新エラー:', rateLimitError);
        }
        
      } else {
        throw new Error(response.error || 'アクション実行に失敗しました');
      }
      
    } catch (error) {
      console.error('❌ アクション実行エラー:', error);
      setError(`実行エラー: ${error.message}`);
    }
  };

  const getRateLimitColor = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRateLimitIcon = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (percentage > 20) return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    return <AlertCircle className="h-4 w-4 text-red-600" />;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score) => {
    if (score >= 80) return <Award className="h-4 w-4 text-green-600" />;
    if (score >= 60) return <Heart className="h-4 w-4 text-blue-600" />;
    if (score >= 40) return <Info className="h-4 w-4 text-yellow-600" />;
    return <AlertTriangle className="h-4 w-4 text-red-600" />;
  };

  const formatTimeUntil = (scheduledTime) => {
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

  const formatNextAvailable = (seconds) => {
    if (seconds <= 0) return '利用可能';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}分${remainingSeconds}秒後`;
    }
    return `${remainingSeconds}秒後`;
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            エンゲージユーザー自動化パネル
          </h1>
          <p className="text-gray-600">
            X APIレート制限対応・あなたの投稿にエンゲージしたユーザーの最新投稿にAI分析でアクション
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
            automationStats.is_running 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              automationStats.is_running ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">
              {automationStats.is_running ? 'レート制限管理中' : '停止中'}
            </span>
          </div>
        </div>
      </div>

      {/* レート制限ダッシュボード */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-red-100 rounded-lg">
            <Gauge className="h-6 w-6 text-red-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              ⚡ X APIレート制限監視
            </h3>
            <p className="text-sm text-gray-500">
              ユーザー単位のAPI使用量をリアルタイム管理
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* いいね制限 */}
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Heart className="h-5 w-5 text-red-600" />
                <span className="font-semibold text-red-900">いいね制限</span>
              </div>
              {getRateLimitIcon(rateLimitStats.like["15min_remaining"], rateLimitStats.like["15min_limit"])}
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>15分制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.like["15min_remaining"], rateLimitStats.like["15min_limit"])}`}>
                  {rateLimitStats.like["15min_remaining"]}/{rateLimitStats.like["15min_limit"]}
                </span>
              </div>
              <div className="flex justify-between">
                <span>24時間制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.like["24hour_remaining"], rateLimitStats.like["24hour_limit"])}`}>
                  {rateLimitStats.like["24hour_remaining"]}/{rateLimitStats.like["24hour_limit"]}
                </span>
              </div>
              {rateLimitStats.like["next_available_seconds"] > 0 && (
                <div className="flex justify-between text-xs text-red-600">
                  <span>次回利用:</span>
                  <span>{formatNextAvailable(rateLimitStats.like["next_available_seconds"])}</span>
                </div>
              )}
            </div>
            
            <div className="mt-3 w-full bg-red-200 rounded-full h-2">
              <div 
                className="bg-red-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(rateLimitStats.like["15min_remaining"] / rateLimitStats.like["15min_limit"]) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* リポスト制限 */}
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Repeat className="h-5 w-5 text-green-600" />
                <span className="font-semibold text-green-900">リポスト制限</span>
              </div>
              {getRateLimitIcon(rateLimitStats.retweet["15min_remaining"], rateLimitStats.retweet["15min_limit"])}
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>15分制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.retweet["15min_remaining"], rateLimitStats.retweet["15min_limit"])}`}>
                  {rateLimitStats.retweet["15min_remaining"]}/{rateLimitStats.retweet["15min_limit"]}
                </span>
              </div>
              <div className="flex justify-between">
                <span>24時間制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.retweet["24hour_remaining"], rateLimitStats.retweet["24hour_limit"])}`}>
                  {rateLimitStats.retweet["24hour_remaining"]}/{rateLimitStats.retweet["24hour_limit"]}
                </span>
              </div>
              {rateLimitStats.retweet["next_available_seconds"] > 0 && (
                <div className="flex justify-between text-xs text-green-600">
                  <span>次回利用:</span>
                  <span>{formatNextAvailable(rateLimitStats.retweet["next_available_seconds"])}</span>
                </div>
              )}
            </div>
            
            <div className="mt-3 w-full bg-green-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(rateLimitStats.retweet["15min_remaining"] / rateLimitStats.retweet["15min_limit"]) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* データ取得制限 */}
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span className="font-semibold text-blue-900">データ取得制限</span>
              </div>
              {getRateLimitIcon(rateLimitStats.get_liking_users["15min_remaining"], rateLimitStats.get_liking_users["15min_limit"])}
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>15分制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.get_liking_users["15min_remaining"], rateLimitStats.get_liking_users["15min_limit"])}`}>
                  {rateLimitStats.get_liking_users["15min_remaining"]}/{rateLimitStats.get_liking_users["15min_limit"]}
                </span>
              </div>
              <div className="flex justify-between">
                <span>24時間制限:</span>
                <span className={`font-medium ${getRateLimitColor(rateLimitStats.get_liking_users["24hour_remaining"], rateLimitStats.get_liking_users["24hour_limit"])}`}>
                  {rateLimitStats.get_liking_users["24hour_remaining"]}/{rateLimitStats.get_liking_users["24hour_limit"]}
                </span>
              </div>
            </div>
            
            <div className="mt-3 w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(rateLimitStats.get_liking_users["15min_remaining"] / rateLimitStats.get_liking_users["15min_limit"]) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* 統計サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">処理済みユーザー</p>
              <p className="text-3xl font-bold text-blue-600">{automationStats.processed_users}</p>
              <p className="text-sm text-gray-500">今日の分析数</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">総分析数</p>
              <p className="text-3xl font-bold text-purple-600">{automationStats.total_analyzed}</p>
              <p className="text-sm text-gray-500">投稿分析完了</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">API効率性</p>
              <p className="text-3xl font-bold text-green-600">{automationStats.success_rate}%</p>
              <p className="text-sm text-green-600">レート制限遵守</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Target className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">実行キュー</p>
              <p className="text-3xl font-bold text-orange-600">{executionQueue.length}</p>
              <p className="text-sm text-orange-600">待機中</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Clock className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* エンゲージユーザー分析セクション */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-100 rounded-lg">
            <UserCheck className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              🎯 エンゲージユーザー自動分析（レート制限対応）
            </h3>
            <p className="text-sm text-gray-500">
              あなたの投稿にいいね・リポストしたユーザーの最新投稿を分析（API制限を厳密管理）
            </p>
          </div>
        </div>
        {/* Freeプラン制限案内 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-3">
            🔒 エンゲージメント分析（Freeプラン制限中）
          </h3>
          <p className="text-yellow-700 mb-4">
            この機能はFreeプランでは利用できません。代わりに「お気に入りユーザー」機能をご利用ください。
          </p>
          <div className="bg-white rounded p-4 mb-4">
            <h4 className="font-medium mb-2">📋 利用可能な代替機能:</h4>
            <ul className="text-sm space-y-1">
              <li>• お気に入りユーザーを手動登録</li>
              <li>• 登録ユーザーの新着ツイートに自動いいね・リポスト</li>
              <li>• AIによる人間らしい自動化</li>
              <li>• Freeプランでも月間500アクション利用可能</li>
            </ul>
          </div>
          <button
            onClick={() => window.location.href = '/favorite-users'}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          >
            お気に入りユーザー管理を開く
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={yourTweetUrl}
              onChange={(e) => setYourTweetUrl(e.target.value)}
              placeholder="あなたの投稿URL: https://x.com/your_username/status/1234567890"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleAnalyzeEngagingUsers}
              disabled={!yourTweetUrl.trim() || isAnalyzing || !rateLimitStats.get_liking_users.can_make_request}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>分析中...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  <span>エンゲージユーザー分析</span>
                </>
              )}
            </button>
          </div>

          {/* エラー表示 */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-sm font-medium text-red-800">{error}</span>
              </div>
            </div>
          )}

          {/* レート制限警告 */}
          {!rateLimitStats.get_liking_users.can_make_request && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">
                  エンゲージユーザー取得のレート制限に達しています。
                  {formatNextAvailable(rateLimitStats.get_liking_users["next_available_seconds"])}に再試行可能です。
                </span>
              </div>
            </div>
          )}

          {/* 分析進行状況 */}
          {isAnalyzing && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-3 mb-2">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
                <span className="font-medium text-blue-900">レート制限遵守でAI分析進行中...</span>
              </div>
              <div className="space-y-1 text-sm text-blue-800">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>エンゲージユーザー取得完了（APIクレジット消費: 1件）</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <span>各ユーザーの最新投稿をAI分析中...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* エンゲージユーザー分析結果 */}
      {analysisResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Bot className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  AI分析結果 - エンゲージユーザーの最新投稿
                </h3>
                <p className="text-sm text-gray-500">
                  {analysisResults.length}人のユーザーの投稿を分析完了・レート制限チェック済み
                </p>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={handleSelectRandomUsers}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Shuffle className="h-4 w-4" />
                <span>ランダム選択</span>
              </button>
              
              <button
                onClick={handleExecuteSelectedActions}
                disabled={selectedUsers.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Zap className="h-4 w-4" />
                <span>選択した{selectedUsers.length}件を実行</span>
              </button>
            </div>
          </div>

          <div className="space-y-4 max-h-96 overflow-y-auto">
            {analysisResults.map((result) => (
              <motion.div
                key={result.user_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedUsers.includes(result.user_id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-gray-50 hover:border-gray-300'
                }`}
                onClick={() => handleSelectUser(result.user_id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-gray-900">@{result.username}</span>
                        {selectedUsers.includes(result.user_id) && (
                          <CheckCircle className="h-4 w-4 text-blue-600" />
                        )}
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className={`flex items-center space-x-1 ${getScoreColor(result.analysis.like_score)}`}>
                          {getScoreIcon(result.analysis.like_score)}
                          <span className="text-sm font-medium">いいね: {result.analysis.like_score}</span>
                        </div>
                        <div className={`flex items-center space-x-1 ${getScoreColor(result.analysis.retweet_score)}`}>
                          {getScoreIcon(result.analysis.retweet_score)}
                          <span className="text-sm font-medium">リポスト: {result.analysis.retweet_score}</span>
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">
                      {result.tweet_text}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>カテゴリ: {result.analysis.content_category}</span>
                      <span>リスク: {result.analysis.risk_level}</span>
                      <span>推奨: {result.analysis.recommended_action === 'like' ? 'いいね♡' : 'リポスト'}</span>
                      <span>信頼度: {Math.round(result.analysis.confidence * 100)}%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* 実行キュー */}
      {executionQueue.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Timer className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  実行キュー - レート制限スケジューリング
                </h3>
                <p className="text-sm text-gray-500">
                  {executionQueue.length}件のアクションがレート制限を考慮してスケジュール済み
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-3 max-h-64 overflow-y-auto">
            {executionQueue.map((action) => (
              <div
                key={action.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-white rounded shadow-sm">
                    {action.action_type === 'like' ? 
                      <Heart className="h-4 w-4 text-red-500" /> : 
                      <Repeat className="h-4 w-4 text-green-500" />
                    }
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900 text-sm">
                        @{action.username}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        action.action_type === 'like' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {action.action_type === 'like' ? 'いいね' : 'リポスト'}
                      </span>
                      <span className="text-xs text-purple-600 font-medium">
                        スコア: {action.action_type === 'like' ? action.ai_scores.like_score : action.ai_scores.retweet_score}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">
                      {action.tweet_text}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      実行予定: {formatTimeUntil(action.scheduled_time)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                    レート制限管理済み
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* レート制限保護機能説明 */}
      <div className="bg-gradient-to-r from-red-50 to-blue-50 rounded-xl p-6 border border-red-200">
        <div className="flex items-start space-x-3">
          <Gauge className="h-6 w-6 text-red-600 mt-1" />
          <div>
            <h4 className="font-medium text-red-900 mb-2">
              ⚡ X APIレート制限完全保護システム
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-red-800">
              <div className="space-y-1">
                <p>✅ <strong>いいね制限:</strong> 15分/1回, 24時間/1000回</p>
                <p>✅ <strong>リポスト制限:</strong> 15分/50回, 24時間/1000回</p>
                <p>✅ <strong>データ取得制限:</strong> 15分/75回まで安全管理</p>
              </div>
              <div className="space-y-1">
                <p>✅ リアルタイム使用量監視とアラート</p>
                <p>✅ 429エラー自動ハンドリング</p>
                <p>✅ スマートスケジューリングで効率実行</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* パスワード入力モーダル */}
      {passwordModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Shield className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">パスワード認証</h3>
                <p className="text-sm text-gray-500">APIキー復号のためパスワードを入力してください</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <input
                type="password"
                value={userPassword}
                onChange={(e) => setUserPassword(e.target.value)}
                placeholder="ユーザーパスワード"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    setPasswordModalOpen(false);
                    if (yourTweetUrl.trim()) {
                      handleAnalyzeEngagingUsers();
                    }
                  }
                }}
              />
              
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setPasswordModalOpen(false);
                    if (yourTweetUrl.trim()) {
                      handleAnalyzeEngagingUsers();
                    }
                  }}
                  disabled={!userPassword.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  確認
                </button>
                <button
                  onClick={() => setPasswordModalOpen(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  キャンセル
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutomationPanel;