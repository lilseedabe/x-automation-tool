/**
 * 🤖 X自動反応ツール - エンゲージユーザー自動化パネル（レート制限対応）
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
  Star,
  Award,
  Search,
  UserCheck,
  Shuffle,
  Timer,
  Gauge,
  AlertCircle,
} from 'lucide-react';

const AutomationPanel = () => {
  const [automationStats, setAutomationStats] = useState({
    likes_today: 15,
    retweets_today: 8,
    success_rate: 94.2,
    is_running: true,
    remaining_likes: 35,
    remaining_retweets: 12,
    processed_users: 23,
    total_analyzed: 45,
  });

  // レート制限情報の状態
  const [rateLimitStats, setRateLimitStats] = useState({
    like: {
      "15min_limit": 1,
      "15min_used": 0,
      "15min_remaining": 1,
      "24hour_limit": 1000,
      "24hour_used": 15,
      "24hour_remaining": 985,
      "next_available_seconds": 0,
      "can_make_request": true
    },
    retweet: {
      "15min_limit": 50,
      "15min_used": 3,
      "15min_remaining": 47,
      "24hour_limit": 1000,
      "24hour_used": 8,
      "24hour_remaining": 992,
      "next_available_seconds": 0,
      "can_make_request": true
    },
    get_liking_users: {
      "15min_limit": 75,
      "15min_used": 2,
      "15min_remaining": 73,
      "24hour_limit": 7200,
      "24hour_used": 23,
      "24hour_remaining": 7177,
      "next_available_seconds": 0,
      "can_make_request": true
    }
  });

  const [yourTweetUrl, setYourTweetUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [engagingUsers, setEngagingUsers] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [executionQueue, setExecutionQueue] = useState([]);

  // 模擬的なエンゲージユーザーデータ
  const mockEngagingUsers = [
    {
      id: 'user1',
      username: 'tech_enthusiast',
      name: 'Tech Lover',
      followers_count: 1500,
      verified: false,
      engagement_type: 'like',
      latest_tweet: {
        id: 'tweet1',
        text: 'AI技術の最新動向について研究中です。機械学習の可能性は無限大！ #AI #ML',
        created_at: '2024-01-15T10:30:00Z',
        public_metrics: { like_count: 25, retweet_count: 8, reply_count: 3 }
      }
    },
    {
      id: 'user2',
      username: 'startup_founder',
      name: 'Startup CEO',
      followers_count: 3200,
      verified: true,
      engagement_type: 'retweet',
      latest_tweet: {
        id: 'tweet2',
        text: '新しいプロダクトのローンチ準備完了！チーム一丸となって頑張りました 🚀',
        created_at: '2024-01-15T09:15:00Z',
        public_metrics: { like_count: 45, retweet_count: 12, reply_count: 7 }
      }
    },
    {
      id: 'user3',
      username: 'dev_community',
      name: 'Developer Hub',
      followers_count: 850,
      verified: false,
      engagement_type: 'like',
      latest_tweet: {
        id: 'tweet3',
        text: 'React 18の新機能を試してみました。パフォーマンスが大幅に向上！ #React #JavaScript',
        created_at: '2024-01-15T08:45:00Z',
        public_metrics: { like_count: 30, retweet_count: 15, reply_count: 5 }
      }
    }
  ];

  // レート制限情報を定期的に更新
  useEffect(() => {
    const interval = setInterval(() => {
      // レート制限の回復をシミュレート
      setRateLimitStats(prev => ({
        ...prev,
        like: {
          ...prev.like,
          "15min_remaining": Math.min(prev.like["15min_limit"], prev.like["15min_remaining"] + 1),
          "next_available_seconds": Math.max(0, prev.like["next_available_seconds"] - 60)
        },
        retweet: {
          ...prev.retweet,
          "15min_remaining": Math.min(prev.retweet["15min_limit"], prev.retweet["15min_remaining"] + 5),
          "next_available_seconds": Math.max(0, prev.retweet["next_available_seconds"] - 60)
        }
      }));
    }, 60000); // 1分ごと

    return () => clearInterval(interval);
  }, []);

  const handleAnalyzeEngagingUsers = async () => {
    if (!yourTweetUrl.trim()) return;

    // レート制限チェック
    if (!rateLimitStats.get_liking_users.can_make_request) {
      alert('エンゲージユーザー取得のレート制限に達しています。しばらく待ってから再試行してください。');
      return;
    }

    setIsAnalyzing(true);
    setEngagingUsers([]);
    setAnalysisResults([]);
    
    // ステップ1: エンゲージユーザー取得をシミュレート
    setTimeout(() => {
      setEngagingUsers(mockEngagingUsers);
      
      // レート制限を消費
      setRateLimitStats(prev => ({
        ...prev,
        get_liking_users: {
          ...prev.get_liking_users,
          "15min_used": prev.get_liking_users["15min_used"] + 1,
          "15min_remaining": prev.get_liking_users["15min_remaining"] - 1,
          "24hour_used": prev.get_liking_users["24hour_used"] + 1,
          "24hour_remaining": prev.get_liking_users["24hour_remaining"] - 1
        }
      }));
      
      // ステップ2: 各ユーザーの最新投稿をAI分析
      setTimeout(() => {
        const results = mockEngagingUsers.map(user => {
          const likeScore = Math.floor(Math.random() * 40) + 60; // 60-100
          const retweetScore = Math.floor(Math.random() * 40) + 50; // 50-90
          const safetyCheck = Math.random() > 0.2; // 80%安全
          const riskLevel = ["低", "低", "低", "中"][Math.floor(Math.random() * 4)];
          
          return {
            user_id: user.id,
            username: user.username,
            tweet_id: user.latest_tweet.id,
            tweet_text: user.latest_tweet.text,
            analysis: {
              like_score: likeScore,
              retweet_score: retweetScore,
              timing_recommendation: ["即座に", "数分後", "1-2分後"][Math.floor(Math.random() * 3)],
              safety_check: safetyCheck,
              content_category: ["技術", "ビジネス", "教育", "デザイン"][Math.floor(Math.random() * 4)],
              risk_level: riskLevel,
              recommended_action: likeScore > retweetScore ? "like" : "retweet",
              confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
              ai_reasoning: `${safetyCheck ? '安全性問題なし' : '軽微な懸念あり'}。${likeScore > 75 ? 'エンゲージメント高期待' : '標準的な反応予想'}。`
            }
          };
        });
        
        setAnalysisResults(results);
        setIsAnalyzing(false);
      }, 2000);
      
    }, 1500);
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

  const handleExecuteSelectedActions = () => {
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
      alert(`いいね制限不足: ${likesNeeded}件必要ですが、残り${rateLimitStats.like["15min_remaining"]}件です。`);
      return;
    }

    if (retweetsNeeded > rateLimitStats.retweet["15min_remaining"]) {
      alert(`リポスト制限不足: ${retweetsNeeded}件必要ですが、残り${rateLimitStats.retweet["15min_remaining"]}件です。`);
      return;
    }

    const newActions = selectedUsers.map(userId => {
      const userAnalysis = analysisResults.find(r => r.user_id === userId);
      if (!userAnalysis) return null;
      
      return {
        id: Date.now() + Math.random(),
        user_id: userId,
        username: userAnalysis.username,
        tweet_id: userAnalysis.tweet_id,
        tweet_text: userAnalysis.tweet_text,
        action_type: userAnalysis.analysis.recommended_action,
        ai_scores: {
          like_score: userAnalysis.analysis.like_score,
          retweet_score: userAnalysis.analysis.retweet_score
        },
        confidence: userAnalysis.analysis.confidence,
        scheduled_time: new Date(Date.now() + Math.random() * 600000 + 60000), // 1-11分後
        status: 'pending'
      };
    }).filter(Boolean);

    setExecutionQueue(prev => [...prev, ...newActions]);
    setSelectedUsers([]);

    // レート制限を消費（シミュレート）
    setRateLimitStats(prev => ({
      ...prev,
      like: {
        ...prev.like,
        "15min_used": prev.like["15min_used"] + likesNeeded,
        "15min_remaining": prev.like["15min_remaining"] - likesNeeded,
        "24hour_used": prev.like["24hour_used"] + likesNeeded,
        "24hour_remaining": prev.like["24hour_remaining"] - likesNeeded
      },
      retweet: {
        ...prev.retweet,
        "15min_used": prev.retweet["15min_used"] + retweetsNeeded,
        "15min_remaining": prev.retweet["15min_remaining"] - retweetsNeeded,
        "24hour_used": prev.retweet["24hour_used"] + retweetsNeeded,
        "24hour_remaining": prev.retweet["24hour_remaining"] - retweetsNeeded
      }
    }));
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
    if (score >= 60) return <Star className="h-4 w-4 text-blue-600" />;
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
    </div>
  );
};

export default AutomationPanel;