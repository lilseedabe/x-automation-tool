/**
 * 🤖 X自動反応ツール - 投稿入力コンポーネント
 * 
 * AI分析機能付きの投稿作成インターフェース
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Image,
  Calendar,
  Hash,
  AtSign,
  MapPin,
  Smile,
  BarChart3,
  Clock,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  X,
  Plus,
  Minus,
  Bot,
  Heart,
  TrendingUp,
  Users,
  Heart,
  MessageCircle,
  Repeat,
  Eye,
  Settings,
  Lightbulb,
  Timer,
  RefreshCw,
} from 'lucide-react';

const PostInput = ({ onPost, onAnalyze }) => {
  const [content, setContent] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [hashtags, setHashtags] = useState([]);
  const [mentions, setMentions] = useState([]);
  const [location, setLocation] = useState('');
  const [images, setImages] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [showScheduler, setShowScheduler] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  
  const maxLength = 280;
  const remainingChars = maxLength - content.length;

  useEffect(() => {
    // AI提案の模擬データ
    if (content.length > 10) {
      const suggestions = [
        { text: '#AI', type: 'hashtag' },
        { text: '#自動化', type: 'hashtag' },
        { text: '#テクノロジー', type: 'hashtag' },
        { text: '@tech_community', type: 'mention' },
        { text: 'エンゲージメントを高めるため、質問を追加してみてください', type: 'tip' },
        { text: '投稿時間を19:00-21:00に設定すると効果的です', type: 'timing' },
      ];
      setAiSuggestions(suggestions.slice(0, 3));
    } else {
      setAiSuggestions([]);
    }
  }, [content]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    const postData = {
      content: content.trim(),
      scheduledTime: scheduledTime || null,
      hashtags,
      mentions,
      location,
      images,
    };

    if (onPost) {
      await onPost(postData);
    }

    // フォームリセット
    setContent('');
    setScheduledTime('');
    setHashtags([]);
    setMentions([]);
    setLocation('');
    setImages([]);
    setAnalysis(null);
  };

  const handleAnalyze = async () => {
    if (!content.trim()) return;

    setIsAnalyzing(true);
    setShowAnalysis(true);

    try {
      // 模擬的なAI分析
      setTimeout(() => {
        const mockAnalysis = {
          score: Math.floor(Math.random() * 40) + 60, // 60-100の範囲
          sentiment: Math.random() > 0.7 ? 'positive' : Math.random() > 0.3 ? 'neutral' : 'negative',
          engagement_prediction: {
            likes: Math.floor(Math.random() * 500) + 50,
            retweets: Math.floor(Math.random() * 200) + 20,
            replies: Math.floor(Math.random() * 100) + 10,
          },
          suggestions: [
            'ハッシュタグを2-3個追加することをお勧めします',
            '投稿時間を19-21時に設定すると良いでしょう',
            '画像を追加するとエンゲージメントが向上します',
          ],
          keywords: ['AI', '自動化', 'ツール'],
        };
        
        setAnalysis(mockAnalysis);
        setIsAnalyzing(false);

        if (onAnalyze) {
          onAnalyze(mockAnalysis);
        }
      }, 2000);
    } catch (error) {
      console.error('分析エラー:', error);
      setIsAnalyzing(false);
    }
  };

  const addHashtag = (tag) => {
    if (!hashtags.includes(tag)) {
      setHashtags([...hashtags, tag]);
    }
  };

  const removeHashtag = (tag) => {
    setHashtags(hashtags.filter(t => t !== tag));
  };

  const addMention = (mention) => {
    if (!mentions.includes(mention)) {
      setMentions([...mentions, mention]);
    }
  };

  const removeMention = (mention) => {
    setMentions(mentions.filter(m => m !== mention));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    setImages([...images, ...files]);
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const applySuggestion = (suggestion) => {
    if (suggestion.type === 'hashtag') {
      addHashtag(suggestion.text);
    } else if (suggestion.type === 'mention') {
      addMention(suggestion.text);
    } else if (suggestion.type === 'timing') {
      const suggestedTime = new Date();
      suggestedTime.setHours(19, 0, 0, 0);
      setScheduledTime(suggestedTime.toISOString().slice(0, 16));
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  const getSentimentLabel = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'ポジティブ';
      case 'negative': return 'ネガティブ';
      default: return 'ニュートラル';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200">
      <form onSubmit={handleSubmit} className="p-6">
        {/* ヘッダー */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Bot className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                投稿作成
              </h3>
              <p className="text-sm text-gray-500">
                AI分析でパフォーマンスを最適化
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className={`p-2 rounded-lg transition-colors ${
                showSuggestions 
                  ? 'bg-purple-100 text-purple-600' 
                  : 'bg-gray-100 text-gray-600 hover:bg-purple-100 hover:text-purple-600'
              }`}
              title="AI提案を表示"
            >
              <Heart className="h-5 w-5" />
            </button>
            
            <button
              type="button"
              onClick={() => setShowAnalysis(!showAnalysis)}
              className={`p-2 rounded-lg transition-colors ${
                showAnalysis 
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-gray-100 text-gray-600 hover:bg-green-100 hover:text-green-600'
              }`}
              title="AI分析を表示"
            >
              <BarChart3 className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* AI提案パネル */}
        <AnimatePresence>
          {showSuggestions && aiSuggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 p-4 bg-purple-50 rounded-lg border border-purple-200"
            >
              <div className="flex items-center space-x-2 mb-3">
                <Lightbulb className="h-5 w-5 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">
                  AI提案
                </span>
              </div>
              
              <div className="space-y-2">
                {aiSuggestions.map((suggestion, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-2 bg-white rounded border"
                  >
                    <div className="flex items-center space-x-2">
                      {suggestion.type === 'hashtag' && <Hash className="h-4 w-4 text-blue-600" />}
                      {suggestion.type === 'mention' && <AtSign className="h-4 w-4 text-green-600" />}
                      {suggestion.type === 'tip' && <Target className="h-4 w-4 text-purple-600" />}
                      {suggestion.type === 'timing' && <Clock className="h-4 w-4 text-orange-600" />}
                      <span className="text-sm text-gray-700">{suggestion.text}</span>
                    </div>
                    
                    <button
                      type="button"
                      onClick={() => applySuggestion(suggestion)}
                      className="p-1 text-purple-600 hover:bg-purple-100 rounded transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* メインテキストエリア */}
        <div className="relative mb-4">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="今何を共有しますか？"
            className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            maxLength={maxLength}
          />
          
          {/* 文字数カウンター */}
          <div className="absolute bottom-2 right-2 flex items-center space-x-2">
            <span className={`text-sm ${
              remainingChars < 20 ? 'text-red-600' : 
              remainingChars < 50 ? 'text-yellow-600' : 'text-gray-500'
            }`}>
              {remainingChars}
            </span>
            
            <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
              remainingChars < 20 ? 'border-red-600' : 
              remainingChars < 50 ? 'border-yellow-600' : 'border-gray-300'
            }`}>
              <div 
                className={`w-6 h-6 rounded-full ${
                  remainingChars < 20 ? 'bg-red-600' : 
                  remainingChars < 50 ? 'bg-yellow-600' : 'bg-gray-300'
                }`}
                style={{
                  transform: `scale(${Math.max(0.1, (maxLength - remainingChars) / maxLength)})`
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* ハッシュタグとメンション */}
        {(hashtags.length > 0 || mentions.length > 0) && (
          <div className="mb-4 space-y-2">
            {hashtags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {hashtags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    <Hash className="h-3 w-3 mr-1" />
                    {tag.replace('#', '')}
                    <button
                      type="button"
                      onClick={() => removeHashtag(tag)}
                      className="ml-1 hover:text-blue-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
            
            {mentions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {mentions.map((mention, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                  >
                    <AtSign className="h-3 w-3 mr-1" />
                    {mention.replace('@', '')}
                    <button
                      type="button"
                      onClick={() => removeMention(mention)}
                      className="ml-1 hover:text-green-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 画像プレビュー */}
        {images.length > 0 && (
          <div className="mb-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {images.map((image, index) => (
                <div key={index} className="relative">
                  <img
                    src={URL.createObjectURL(image)}
                    alt={`Upload ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-1 right-1 p-1 bg-red-600 text-white rounded-full hover:bg-red-700"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* スケジュール設定 */}
        <AnimatePresence>
          {showScheduler && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200"
            >
              <div className="flex items-center space-x-2 mb-3">
                <Calendar className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">
                  投稿スケジュール
                </span>
              </div>
              
              <input
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="w-full p-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min={new Date().toISOString().slice(0, 16)}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* AI分析結果 */}
        <AnimatePresence>
          {showAnalysis && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4"
            >
              {isAnalyzing ? (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-3">
                    <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />
                    <span className="text-sm font-medium text-blue-900">
                      AI分析中...
                    </span>
                  </div>
                </div>
              ) : analysis ? (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* スコア */}
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getScoreColor(analysis.score)}`}>
                        {analysis.score}
                      </div>
                      <div className="text-sm text-gray-600">総合スコア</div>
                    </div>
                    
                    {/* センチメント */}
                    <div className="text-center">
                      <div className={`text-lg font-semibold ${getSentimentColor(analysis.sentiment)}`}>
                        {getSentimentLabel(analysis.sentiment)}
                      </div>
                      <div className="text-sm text-gray-600">感情分析</div>
                    </div>
                    
                    {/* 予測エンゲージメント */}
                    <div className="text-center">
                      <div className="flex justify-center space-x-3 text-sm">
                        <div className="flex items-center space-x-1">
                          <Heart className="h-4 w-4 text-red-500" />
                          <span>{analysis.engagement_prediction.likes}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Repeat className="h-4 w-4 text-green-500" />
                          <span>{analysis.engagement_prediction.retweets}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="h-4 w-4 text-blue-500" />
                          <span>{analysis.engagement_prediction.replies}</span>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">予測エンゲージメント</div>
                    </div>
                  </div>
                  
                  {/* 提案 */}
                  {analysis.suggestions && analysis.suggestions.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-green-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <Lightbulb className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-green-900">
                          改善提案
                        </span>
                      </div>
                      <ul className="space-y-1">
                        {analysis.suggestions.map((suggestion, index) => (
                          <li key={index} className="text-sm text-green-800 flex items-start">
                            <span className="mr-2">•</span>
                            <span>{suggestion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : null}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ツールバー */}
        <div className="flex items-center justify-between border-t border-gray-200 pt-4">
          <div className="flex items-center space-x-2">
            {/* 画像追加 */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="画像を追加"
            >
              <Image className="h-5 w-5" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleImageUpload}
              className="hidden"
            />
            
            {/* スケジュール */}
            <button
              type="button"
              onClick={() => setShowScheduler(!showScheduler)}
              className={`p-2 rounded-lg transition-colors ${
                showScheduler 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
              }`}
              title="スケジュール設定"
            >
              <Calendar className="h-5 w-5" />
            </button>
            
            {/* 位置情報 */}
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="位置情報を追加"
            >
              <MapPin className="h-5 w-5" />
            </button>
            
            {/* 絵文字 */}
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
              title="絵文字を追加"
            >
              <Smile className="h-5 w-5" />
            </button>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* AI分析ボタン */}
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!content.trim() || isAnalyzing}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Bot className="h-4 w-4" />
              <span>AI分析</span>
            </button>
            
            {/* 投稿ボタン */}
            <button
              type="submit"
              disabled={!content.trim()}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4" />
              <span>{scheduledTime ? 'スケジュール' : '投稿'}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default PostInput;