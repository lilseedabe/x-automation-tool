/**
 * 🤖 X自動反応ツール - AI分析コンポーネント
 * 
 * Groq AIによる投稿分析機能
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, BarChart3, TrendingUp, AlertTriangle, CheckCircle, 
  Clock, Zap, Target, Star, ThumbsUp, MessageCircle, 
  RotateCcw, Eye, Shield, Activity 
} from 'lucide-react';

const AIAnalysis = ({ post, onAnalysisComplete }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (post) {
      analyzePost(post);
    }
  }, [post]);

  const analyzePost = async (postContent) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('認証が必要です');
      }

      // 実際のGroq AI分析API呼び出し
      const response = await fetch('/api/ai/analyze-post', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: postContent,
          analysis_type: 'engagement_prediction'
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const analysisResult = await response.json();
      
      setAnalysis(analysisResult);
      setLoading(false);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(analysisResult);
      }
      
    } catch (err) {
      console.error('AI分析エラー:', err);
      
      // フォールバック：エラー時は基本的な分析を提供
      const fallbackAnalysis = {
        overall_score: 70,
        engagement_prediction: {
          likes: postContent?.length > 100 ? 150 : 75,
          retweets: postContent?.length > 100 ? 50 : 25,
          replies: postContent?.length > 100 ? 20 : 10,
        },
        sentiment: {
          positive: 0.6,
          neutral: 0.3,
          negative: 0.1,
        },
        keywords: extractBasicKeywords(postContent),
        recommendations: generateBasicRecommendations(postContent),
        risk_assessment: 'low',
        note: 'AI分析が利用できないため、基本的な分析を表示しています'
      };
      
      setAnalysis(fallbackAnalysis);
      setLoading(false);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(fallbackAnalysis);
      }
    }
  };

  // 基本的なキーワード抽出
  const extractBasicKeywords = (content) => {
    if (!content) return ['投稿'];
    
    const commonWords = ['AI', '自動化', 'テクノロジー', '効率化', 'ビジネス', 'マーケティング'];
    const foundWords = commonWords.filter(word =>
      content.toLowerCase().includes(word.toLowerCase())
    );
    
    return foundWords.length > 0 ? foundWords : ['一般'];
  };

  // 基本的な推奨事項生成
  const generateBasicRecommendations = (content) => {
    const recommendations = [];
    
    if (!content) {
      recommendations.push('投稿内容を入力してください');
      return recommendations;
    }
    
    if (content.length < 50) {
      recommendations.push('投稿をもう少し詳しく書くとエンゲージメントが向上します');
    }
    
    if (!content.includes('#')) {
      recommendations.push('関連するハッシュタグを追加することをお勧めします');
    }
    
    if (content.length > 280) {
      recommendations.push('投稿が長すぎる可能性があります。簡潔にまとめることを検討してください');
    }
    
    recommendations.push('投稿時間を19-21時に設定すると良いでしょう');
    
    return recommendations;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return '優秀';
    if (score >= 60) return '良好';
    if (score >= 40) return '普通';
    return '要改善';
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
      >
        <div className="flex items-center justify-center space-x-3 mb-4">
          <Bot className="h-6 w-6 text-blue-600 animate-pulse" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI分析中...
          </h3>
        </div>
        
        <div className="space-y-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="h-5 w-5 text-blue-600 animate-pulse" />
              <span className="text-sm font-medium text-blue-900">
                エンゲージメント予測
              </span>
            </div>
            <div className="h-2 bg-blue-200 rounded-full animate-pulse"></div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="h-5 w-5 text-green-600 animate-pulse" />
              <span className="text-sm font-medium text-green-900">
                センチメント分析
              </span>
            </div>
            <div className="h-2 bg-green-200 rounded-full animate-pulse"></div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="h-5 w-5 text-purple-600 animate-pulse" />
              <span className="text-sm font-medium text-purple-900">
                最適化提案生成
              </span>
            </div>
            <div className="h-2 bg-purple-200 rounded-full animate-pulse"></div>
          </div>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg p-6 border border-red-200"
      >
        <div className="flex items-center space-x-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-red-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            分析エラー
          </h3>
        </div>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => analyzePost(post)}
          className="btn btn-outline flex items-center space-x-2"
        >
          <RotateCcw className="h-4 w-4" />
          <span>再試行</span>
        </button>
      </motion.div>
    );
  }

  if (!analysis) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
    >
      <div className="flex items-center space-x-3 mb-6">
        <Bot className="h-6 w-6 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">
          AI分析結果
        </h3>
        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
          完了
        </span>
      </div>

      {/* 総合スコア */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">総合スコア</span>
          <span className={`text-2xl font-bold ${getScoreColor(analysis.overall_score)}`}>
            {analysis.overall_score}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${analysis.overall_score}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`h-3 rounded-full ${
              analysis.overall_score >= 80 ? 'bg-green-500' :
              analysis.overall_score >= 60 ? 'bg-blue-500' :
              analysis.overall_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
          ></motion.div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {getScoreLabel(analysis.overall_score)}
        </p>
      </div>

      {/* エンゲージメント予測 */}
      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
          エンゲージメント予測
        </h4>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <ThumbsUp className="h-6 w-6 text-red-500 mx-auto mb-2" />
            <p className="text-lg font-semibold text-gray-900">
              {analysis.engagement_prediction.likes.toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">いいね</p>
          </div>
          <div className="text-center">
            <RotateCcw className="h-6 w-6 text-green-500 mx-auto mb-2" />
            <p className="text-lg font-semibold text-gray-900">
              {analysis.engagement_prediction.retweets.toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">リツイート</p>
          </div>
          <div className="text-center">
            <MessageCircle className="h-6 w-6 text-blue-500 mx-auto mb-2" />
            <p className="text-lg font-semibold text-gray-900">
              {analysis.engagement_prediction.replies.toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">返信</p>
          </div>
        </div>
      </div>

      {/* センチメント分析 */}
      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
          <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
          センチメント分析
        </h4>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">ポジティブ</span>
            <span className="text-sm font-medium text-green-600">
              {(analysis.sentiment.positive * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${analysis.sentiment.positive * 100}%` }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="h-2 bg-green-500 rounded-full"
            ></motion.div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">ニュートラル</span>
            <span className="text-sm font-medium text-blue-600">
              {(analysis.sentiment.neutral * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${analysis.sentiment.neutral * 100}%` }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="h-2 bg-blue-500 rounded-full"
            ></motion.div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">ネガティブ</span>
            <span className="text-sm font-medium text-red-600">
              {(analysis.sentiment.negative * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${analysis.sentiment.negative * 100}%` }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="h-2 bg-red-500 rounded-full"
            ></motion.div>
          </div>
        </div>
      </div>

      {/* キーワード */}
      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
          <Target className="h-5 w-5 mr-2 text-purple-600" />
          検出されたキーワード
        </h4>
        <div className="flex flex-wrap gap-2">
          {analysis.keywords.map((keyword, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
            >
              {keyword}
            </motion.span>
          ))}
        </div>
      </div>

      {/* 推奨事項 */}
      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
          <Star className="h-5 w-5 mr-2 text-yellow-600" />
          最適化の推奨事項
        </h4>
        <ul className="space-y-2">
          {analysis.recommendations.map((rec, index) => (
            <motion.li
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-2 text-sm text-gray-700"
            >
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span>{rec}</span>
            </motion.li>
          ))}
        </ul>
      </div>

      {/* リスク評価 */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
        <div className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-green-600" />
          <span className="text-sm font-medium text-gray-900">リスク評価</span>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          analysis.risk_assessment === 'low' ? 'bg-green-100 text-green-800' :
          analysis.risk_assessment === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {analysis.risk_assessment === 'low' ? '低' :
           analysis.risk_assessment === 'medium' ? '中' : '高'}
        </span>
      </div>

      {/* AI分析の注記（フォールバック時） */}
      {analysis.note && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-yellow-800">{analysis.note}</p>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default AIAnalysis;