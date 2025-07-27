/**
 * 🤖 X自動反応ツール - ローディングスピナーコンポーネント
 * 
 * 美しいアニメーション付きローディング表示
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Loader2, Zap, Activity } from 'lucide-react';

const LoadingSpinner = ({ size = 'medium', message = '読み込み中...', fullScreen = false }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const containerClasses = fullScreen 
    ? 'fixed inset-0 bg-white bg-opacity-90 backdrop-blur-sm z-50' 
    : '';

  return (
    <div className={`flex items-center justify-center ${containerClasses}`}>
      <div className="flex flex-col items-center space-y-4">
        {/* メインスピナー */}
        <div className="relative">
          {/* 外側の回転リング */}
          <motion.div
            className="absolute inset-0 border-4 border-blue-100 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            style={{ width: '4rem', height: '4rem' }}
          />
          
          {/* 内側のアクセントリング */}
          <motion.div
            className="absolute inset-1 border-4 border-transparent border-t-blue-600 border-r-blue-600 rounded-full"
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            style={{ width: '3rem', height: '3rem' }}
          />
          
          {/* 中央のAIアイコン */}
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              animate={{ 
                scale: [1, 1.1, 1],
                opacity: [0.7, 1, 0.7] 
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
              className="text-blue-600"
            >
              <Bot className="w-6 h-6" />
            </motion.div>
          </div>
        </div>

        {/* ローディングメッセージ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <p className="text-gray-700 font-medium text-lg mb-2">
            {message}
          </p>
          
          {/* サブメッセージ */}
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="flex items-center justify-center space-x-1 text-sm text-gray-500"
          >
            <Activity className="w-4 h-4" />
            <span>AI システムを初期化中</span>
          </motion.div>
        </motion.div>

        {/* プログレスドット */}
        <div className="flex space-x-2">
          {[0, 1, 2].map((index) => (
            <motion.div
              key={index}
              className="w-2 h-2 bg-blue-600 rounded-full"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: index * 0.2,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        {/* 追加の視覚的要素 */}
        <div className="relative w-32 h-1 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
            animate={{
              x: ['-100%', '100%'],
            }}
            transition={{
              duration: 1.8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{ width: '40%' }}
          />
        </div>

        {/* 機能ヒント */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center max-w-md"
        >
          <div className="grid grid-cols-3 gap-4 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <Zap className="w-3 h-3 text-yellow-500" />
              <span>AI分析</span>
            </div>
            <div className="flex items-center space-x-1">
              <Bot className="w-3 h-3 text-blue-500" />
              <span>自動化</span>
            </div>
            <div className="flex items-center space-x-1">
              <Activity className="w-3 h-3 text-green-500" />
              <span>リアルタイム</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

// シンプルなインラインスピナー
export const SimpleSpinner = ({ className = '' }) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    className={`inline-block ${className}`}
  >
    <Loader2 className="w-4 h-4" />
  </motion.div>
);

// ボタン用スピナー
export const ButtonSpinner = ({ size = 4 }) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    className="inline-block"
  >
    <Loader2 className={`w-${size} h-${size}`} />
  </motion.div>
);

export default LoadingSpinner;