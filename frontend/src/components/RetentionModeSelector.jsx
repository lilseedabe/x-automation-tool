/**
 * 📅 データ保持期間選択コンポーネント
 * 
 * ユーザーが自分のニーズに応じて保持期間を選択
 * プライバシーと利便性のバランスを調整
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  Shield,
  Zap,
  Calendar,
  Infinity,
  AlertTriangle,
  CheckCircle,
  Info,
  Settings,
  Timer,
  Refresh,
  Star,
  Award,
  Target,
} from 'lucide-react';

const RetentionModeSelector = ({ currentMode = 'balanced', onModeSelect }) => {
  const [selectedMode, setSelectedMode] = useState(currentMode);
  const [showComparison, setShowComparison] = useState(false);

  const retentionModes = {
    ultra_private: {
      id: 'ultra_private',
      name: 'ウルトラプライベート',
      description: '24時間で自動削除（最高プライバシー）',
      icon: Shield,
      color: 'green',
      period: '24時間',
      days: 1,
      reentryFrequency: '毎日',
      privacyLevel: '最高',
      convenience: '低',
      useCase: '一時的な利用・テスト目的',
      pros: [
        '✅ 最高レベルのプライバシー保護',
        '✅ データ残存リスクゼロ',
        '✅ 忘れてもすぐ削除される安心感'
      ],
      cons: [
        '❌ 毎日APIキー再設定が必要',
        '❌ 継続利用には不便',
        '❌ 自動化の設定が頻繁にリセット'
      ],
      recommendedFor: ['プライバシー最重視', '一時利用', 'テスト目的', '不定期利用']
    },
    balanced: {
      id: 'balanced',
      name: 'バランス型',
      description: '7日間保持（週単位利用）',
      icon: Target,
      color: 'blue',
      period: '7日間',
      days: 7,
      reentryFrequency: '週1回',
      privacyLevel: '高',
      convenience: '中',
      useCase: '週単位での利用パターン',
      pros: [
        '✅ プライバシーと利便性の良いバランス',
        '✅ 週1回の設定で継続利用可能',
        '✅ 忘れても1週間の猶予あり'
      ],
      cons: [
        '⚠️ 週末に再設定リマインダー',
        '⚠️ 1週間のデータ保持期間'
      ],
      recommendedFor: ['一般的な個人利用', 'バランス重視', '週単位の定期利用', '多くのユーザー推奨']
    },
    convenient: {
      id: 'convenient',
      name: '利便性重視',
      description: '30日間保持（月単位利用）',
      icon: Zap,
      color: 'orange',
      period: '30日間',
      days: 30,
      reentryFrequency: '月1回',
      privacyLevel: '中',
      convenience: '高',
      useCase: '月単位での継続利用',
      pros: [
        '✅ 月1回の設定のみで継続利用',
        '✅ 高い利便性と使いやすさ',
        '✅ 自動化設定の継続性'
      ],
      cons: [
        '⚠️ 30日間のデータ保持',
        '⚠️ 月末に再設定が必要'
      ],
      recommendedFor: ['継続利用希望', '利便性重視', '月単位の利用パターン', 'ライトビジネス']
    },
    continuous: {
      id: 'continuous',
      name: '継続利用',
      description: '手動削除まで保持（最高利便性）',
      icon: Infinity,
      color: 'purple',
      period: '無期限',
      days: '∞',
      reentryFrequency: '不要',
      privacyLevel: '中',
      convenience: '最高',
      useCase: '長期継続利用・ビジネス運用',
      pros: [
        '✅ 一度設定すれば継続利用可能',
        '✅ 最高の利便性',
        '✅ ビジネス利用に最適',
        '✅ APIキー再設定の手間なし'
      ],
      cons: [
        '⚠️ 手動削除まで保持される',
        '⚠️ 削除を忘れるリスク',
        '⚠️ プライバシーレベル中程度'
      ],
      recommendedFor: ['ビジネス利用', '長期継続利用', '自動化メイン', '設定の手間を避けたい']
    }
  };

  const getColorClasses = (color, type = 'bg') => {
    const colors = {
      green: {
        bg: 'bg-green-100',
        border: 'border-green-300',
        text: 'text-green-800',
        button: 'bg-green-600 hover:bg-green-700'
      },
      blue: {
        bg: 'bg-blue-100',
        border: 'border-blue-300',
        text: 'text-blue-800',
        button: 'bg-blue-600 hover:bg-blue-700'
      },
      orange: {
        bg: 'bg-orange-100',
        border: 'border-orange-300',
        text: 'text-orange-800',
        button: 'bg-orange-600 hover:bg-orange-700'
      },
      purple: {
        bg: 'bg-purple-100',
        border: 'border-purple-300',
        text: 'text-purple-800',
        button: 'bg-purple-600 hover:bg-purple-700'
      }
    };
    return colors[color]?.[type] || '';
  };

  const handleModeSelect = (modeId) => {
    setSelectedMode(modeId);
    if (onModeSelect) {
      onModeSelect(modeId, retentionModes[modeId]);
    }
  };

  const getRecommendedMode = () => {
    // 簡単な推奨ロジック（実際のアプリではより詳細な分析）
    return 'balanced'; // 多くのユーザーに適したバランス型を推奨
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          データ保持期間を選択してください
        </h2>
        <p className="text-gray-600 max-w-3xl mx-auto">
          あなたの利用パターンに合わせて、プライバシーと利便性のバランスを調整できます。
          <strong>継続利用の場合は、APIキーの再設定頻度も考慮してください。</strong>
        </p>
      </div>

      {/* 重要な説明 */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info className="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-900">重要：APIキー再設定について</h4>
            <p className="text-sm text-yellow-800 mt-1">
              データが自動削除される場合、<strong>APIキーの再設定が必要</strong>になります。
              継続利用をお望みの場合は、「継続利用」モードまたは「利便性重視」モードを推奨します。
            </p>
          </div>
        </div>
      </div>

      {/* モード選択カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.values(retentionModes).map((mode) => {
          const IconComponent = mode.icon;
          const isSelected = selectedMode === mode.id;
          const isRecommended = mode.id === getRecommendedMode();
          
          return (
            <motion.div
              key={mode.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`relative p-6 rounded-xl border-2 cursor-pointer transition-all ${
                isSelected 
                  ? `${getColorClasses(mode.color, 'border')} ${getColorClasses(mode.color, 'bg')}` 
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
              onClick={() => handleModeSelect(mode.id)}
            >
              {/* 推奨バッジ */}
              {isRecommended && (
                <div className="absolute top-4 right-4">
                  <span className="px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded-full">
                    推奨
                  </span>
                </div>
              )}

              {/* 選択インジケーター */}
              {isSelected && !isRecommended && (
                <div className="absolute top-4 right-4">
                  <CheckCircle className={`h-6 w-6 ${getColorClasses(mode.color, 'text').replace('800', '600')}`} />
                </div>
              )}

              {/* アイコンとタイトル */}
              <div className="flex items-center space-x-3 mb-4">
                <div className={`p-3 rounded-lg ${getColorClasses(mode.color, 'bg')}`}>
                  <IconComponent className={`h-6 w-6 ${getColorClasses(mode.color, 'text').replace('800', '600')}`} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {mode.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {mode.description}
                  </p>
                </div>
              </div>

              {/* 主要指標 */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">保持期間:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.period}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">再設定:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.reentryFrequency}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">プライバシー:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.privacyLevel}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">利便性:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.convenience}
                  </p>
                </div>
              </div>

              {/* メリット・デメリット（簡略版） */}
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-green-700 mb-1">メリット:</p>
                  <p className="text-xs text-green-600">{mode.pros[0]}</p>
                </div>
                {mode.cons.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-red-700 mb-1">注意点:</p>
                    <p className="text-xs text-red-600">{mode.cons[0]}</p>
                  </div>
                )}
              </div>

              {/* 推奨対象 */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-700 mb-1">推奨対象:</p>
                <p className="text-xs text-gray-600">
                  {mode.recommendedFor[0]}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* 詳細比較ボタン */}
      <div className="text-center">
        <button
          onClick={() => setShowComparison(!showComparison)}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Timer className="h-4 w-4" />
          <span>詳細比較表を{showComparison ? '非表示' : '表示'}</span>
        </button>
      </div>

      {/* 詳細比較表 */}
      {showComparison && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
        >
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              詳細比較表
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-900">項目</th>
                    <th className="text-center py-3 px-4 font-medium text-green-800">ウルトラプライベート</th>
                    <th className="text-center py-3 px-4 font-medium text-blue-800">バランス型</th>
                    <th className="text-center py-3 px-4 font-medium text-orange-800">利便性重視</th>
                    <th className="text-center py-3 px-4 font-medium text-purple-800">継続利用</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">保持期間</td>
                    <td className="text-center py-3 px-4 text-green-700">24時間</td>
                    <td className="text-center py-3 px-4 text-blue-700">7日間</td>
                    <td className="text-center py-3 px-4 text-orange-700">30日間</td>
                    <td className="text-center py-3 px-4 text-purple-700">無期限</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">再設定頻度</td>
                    <td className="text-center py-3 px-4 text-green-700">毎日</td>
                    <td className="text-center py-3 px-4 text-blue-700">週1回</td>
                    <td className="text-center py-3 px-4 text-orange-700">月1回</td>
                    <td className="text-center py-3 px-4 text-purple-700">不要</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">プライバシーレベル</td>
                    <td className="text-center py-3 px-4 text-green-700">最高</td>
                    <td className="text-center py-3 px-4 text-blue-700">高</td>
                    <td className="text-center py-3 px-4 text-orange-700">中</td>
                    <td className="text-center py-3 px-4 text-purple-700">中</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">利便性</td>
                    <td className="text-center py-3 px-4 text-red-600">低</td>
                    <td className="text-center py-3 px-4 text-yellow-600">中</td>
                    <td className="text-center py-3 px-4 text-green-600">高</td>
                    <td className="text-center py-3 px-4 text-green-600">最高</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">継続利用しやすさ</td>
                    <td className="text-center py-3 px-4 text-red-600">困難</td>
                    <td className="text-center py-3 px-4 text-yellow-600">普通</td>
                    <td className="text-center py-3 px-4 text-green-600">良好</td>
                    <td className="text-center py-3 px-4 text-green-600">最高</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-gray-900">推奨対象</td>
                    <td className="text-center py-3 px-4 text-green-700 text-xs">一時利用</td>
                    <td className="text-center py-3 px-4 text-blue-700 text-xs">一般利用</td>
                    <td className="text-center py-3 px-4 text-orange-700 text-xs">継続利用</td>
                    <td className="text-center py-3 px-4 text-purple-700 text-xs">ビジネス</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* 選択されたモードの詳細 */}
      {selectedMode && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-6 rounded-xl border ${getColorClasses(retentionModes[selectedMode].color, 'border')} ${getColorClasses(retentionModes[selectedMode].color, 'bg')}`}
        >
          <h3 className={`text-lg font-semibold mb-4 ${getColorClasses(retentionModes[selectedMode].color, 'text')}`}>
            選択中: {retentionModes[selectedMode].name}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">メリット</h4>
              <ul className="text-sm text-gray-700 space-y-1">
                {retentionModes[selectedMode].pros.map((pro, index) => (
                  <li key={index}>{pro}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">注意点</h4>
              <ul className="text-sm text-gray-700 space-y-1">
                {retentionModes[selectedMode].cons.map((con, index) => (
                  <li key={index}>{con}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-4 p-3 bg-white bg-opacity-50 rounded">
            <p className="text-sm font-medium text-gray-900">
              💡 この設定では、<strong>{retentionModes[selectedMode].reentryFrequency}</strong>でAPIキーの再設定が必要になります。
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default RetentionModeSelector;