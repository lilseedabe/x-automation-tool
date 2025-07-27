/**
 * 💾 データ保存方式選択コンポーネント
 * 
 * ユーザーがデータ保存方式を選択
 * ローカル保存 vs シンVPS保存
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Monitor,
  Server,
  Shield,
  Clock,
  Infinity,
  CheckCircle,
  AlertTriangle,
  Info,
  Zap,
  Target,
  Database,
  Globe,
  Lock,
} from 'lucide-react';

const StorageModeSelector = ({ currentMode = 'local', onModeSelect }) => {
  const [selectedMode, setSelectedMode] = useState(currentMode);
  const [selectedRetention, setSelectedRetention] = useState('balanced');

  const storageModes = {
    local: {
      id: 'local',
      name: 'ローカル保存モード',
      description: 'ブラウザのローカルストレージのみ',
      icon: Monitor,
      color: 'green',
      privacy: '最高',
      convenience: '低',
      features: [
        '✅ ブラウザのローカルストレージのみ',
        '✅ サーバーには一切保存されない',
        '✅ 運営者・第三者のアクセス不可',
        '✅ 国際的なデータ移転なし',
        '❌ 継続自動化には手動実行が必要'
      ],
      pros: [
        '最高レベルのプライバシー保護',
        'データ漏洩リスクゼロ',
        '運営者も見ることができない'
      ],
      cons: [
        'ブラウザを閉じると自動化停止',
        '継続利用には手動実行が必要',
        '複数デバイスでの利用不可'
      ],
      recommendedFor: ['プライバシー最重視', '一時利用', '手動実行で十分']
    },
    shin_vps: {
      id: 'shin_vps',
      name: 'シンVPS保存モード',
      description: '運営者ブラインド・継続自動化',
      icon: Server,
      color: 'blue',
      privacy: '高',
      convenience: '最高',
      features: [
        '✅ 24時間継続自動化',
        '✅ 運営者が技術的にアクセス不可',
        '✅ 日本国内サーバー（シンVPS）',
        '✅ RSA-2048 + AES-256暗号化',
        '✅ 柔軟な保持期間設定'
      ],
      pros: [
        '24時間継続自動化',
        'ブラウザを閉じても動作',
        '運営者ブラインド設計',
        '日本国内でデータ管理'
      ],
      cons: [
        'サーバーにデータ保存',
        '一定期間後の再設定必要',
        'インターネット接続必須'
      ],
      recommendedFor: ['継続利用希望', 'ビジネス用途', '24時間自動化']
    }
  };

  const retentionOptions = {
    ultra_private: {
      id: 'ultra_private',
      name: '24時間',
      description: '最高プライバシー',
      icon: Shield,
      color: 'green'
    },
    balanced: {
      id: 'balanced',
      name: '7日間',
      description: 'バランス型（推奨）',
      icon: Target,
      color: 'blue'
    },
    convenient: {
      id: 'convenient',
      name: '30日間',
      description: '利便性重視',
      icon: Zap,
      color: 'orange'
    },
    continuous: {
      id: 'continuous',
      name: '無期限',
      description: '継続利用',
      icon: Infinity,
      color: 'purple'
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

  const handleModeSelect = (modeId, retentionId = null) => {
    setSelectedMode(modeId);
    if (retentionId) {
      setSelectedRetention(retentionId);
    }
    
    if (onModeSelect) {
      onModeSelect({
        storage_mode: modeId,
        retention_mode: modeId === 'shin_vps' ? retentionId || selectedRetention : null,
        config: {
          storage: storageModes[modeId],
          retention: modeId === 'shin_vps' ? retentionOptions[retentionId || selectedRetention] : null
        }
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          データ保存方式を選択してください
        </h2>
        <p className="text-gray-600 max-w-3xl mx-auto">
          プライバシーと利便性のバランスを考慮して、最適なデータ保存方式を選択してください。
        </p>
      </div>

      {/* ストレージモード選択 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.values(storageModes).map((mode) => {
          const IconComponent = mode.icon;
          const isSelected = selectedMode === mode.id;
          
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
              {/* 選択インジケーター */}
              {isSelected && (
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
                  <span className="text-sm font-medium text-gray-700">プライバシー:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.privacy}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">利便性:</span>
                  <p className={`font-bold ${getColorClasses(mode.color, 'text')}`}>
                    {mode.convenience}
                  </p>
                </div>
              </div>

              {/* 特徴 */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900">主な特徴:</h4>
                <ul className="text-xs text-gray-700 space-y-1">
                  {mode.features.slice(0, 3).map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
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

      {/* シンVPS選択時の保持期間設定 */}
      {selectedMode === 'shin_vps' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-blue-50 rounded-xl p-6 border border-blue-200"
        >
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            データ保持期間を選択してください
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.values(retentionOptions).map((option) => {
              const IconComponent = option.icon;
              const isSelected = selectedRetention === option.id;
              
              return (
                <div
                  key={option.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    isSelected 
                      ? `${getColorClasses(option.color, 'border')} ${getColorClasses(option.color, 'bg')}` 
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                  onClick={() => {
                    setSelectedRetention(option.id);
                    handleModeSelect('shin_vps', option.id);
                  }}
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <IconComponent className={`h-4 w-4 ${
                      isSelected ? getColorClasses(option.color, 'text').replace('800', '600') : 'text-gray-600'
                    }`} />
                    <h4 className={`font-medium ${
                      isSelected ? getColorClasses(option.color, 'text') : 'text-gray-900'
                    }`}>
                      {option.name}
                    </h4>
                  </div>
                  <p className={`text-xs ${
                    isSelected ? getColorClasses(option.color, 'text') : 'text-gray-600'
                  }`}>
                    {option.description}
                  </p>
                  {isSelected && (
                    <div className="mt-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-4 p-3 bg-white bg-opacity-50 rounded">
            <p className="text-sm text-blue-800">
              <strong>選択中:</strong> {retentionOptions[selectedRetention].name}で自動削除
              {selectedRetention !== 'continuous' && '（継続利用には再設定が必要）'}
            </p>
          </div>
        </motion.div>
      )}

      {/* 比較表 */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            詳細比較
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">項目</th>
                  <th className="text-center py-3 px-4 font-medium text-green-800">ローカル保存</th>
                  <th className="text-center py-3 px-4 font-medium text-blue-800">シンVPS保存</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">データ保存場所</td>
                  <td className="text-center py-3 px-4 text-green-700">ブラウザのみ</td>
                  <td className="text-center py-3 px-4 text-blue-700">シンVPS（日本）</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">継続自動化</td>
                  <td className="text-center py-3 px-4 text-red-600">×</td>
                  <td className="text-center py-3 px-4 text-green-600">○</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">運営者アクセス</td>
                  <td className="text-center py-3 px-4 text-green-600">不可</td>
                  <td className="text-center py-3 px-4 text-green-600">技術的に不可</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">プライバシーレベル</td>
                  <td className="text-center py-3 px-4 text-green-600">最高</td>
                  <td className="text-center py-3 px-4 text-blue-600">高</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">利便性</td>
                  <td className="text-center py-3 px-4 text-red-600">低</td>
                  <td className="text-center py-3 px-4 text-green-600">高</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900">推奨用途</td>
                  <td className="text-center py-3 px-4 text-green-700 text-xs">プライバシー重視</td>
                  <td className="text-center py-3 px-4 text-blue-700 text-xs">継続利用</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 選択結果表示 */}
      {selectedMode && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-6 rounded-xl border ${getColorClasses(storageModes[selectedMode].color, 'border')} ${getColorClasses(storageModes[selectedMode].color, 'bg')}`}
        >
          <h3 className={`text-lg font-semibold mb-4 ${getColorClasses(storageModes[selectedMode].color, 'text')}`}>
            選択内容の確認
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">保存方式</h4>
              <p className="text-sm text-gray-700">
                {storageModes[selectedMode].name}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {storageModes[selectedMode].description}
              </p>
            </div>
            
            {selectedMode === 'shin_vps' && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">保持期間</h4>
                <p className="text-sm text-gray-700">
                  {retentionOptions[selectedRetention].name}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {retentionOptions[selectedRetention].description}
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 p-3 bg-white bg-opacity-50 rounded">
            <p className="text-sm font-medium text-gray-900">
              💡 {selectedMode === 'local' ? 
                'ローカル保存では手動実行のみ可能です。継続自動化をお望みの場合はシンVPS保存をご検討ください。' :
                `シンVPS保存で${retentionOptions[selectedRetention].name}の保持期間が設定されます。`
              }
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default StorageModeSelector;