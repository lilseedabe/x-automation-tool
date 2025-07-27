/**
 * 🔧 自動化モード選択コンポーネント（Render対応版）
 * 
 * Renderデプロイメント時の法的・プライバシーリスクを考慮
 * 手動実行モードのみを推奨・提供
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  User,
  AlertTriangle,
  Info,
  CheckCircle,
  Server,
  Globe,
  Lock,
  Eye,
  Database,
} from 'lucide-react';

const AutomationModeSelector = ({ onModeSelect, currentMode = null }) => {
  const [selectedMode, setSelectedMode] = useState(currentMode || 'manual');
  const [showRenderWarning, setShowRenderWarning] = useState(true);

  // Renderデプロイメント用：手動実行モードのみ推奨
  const recommendedMode = {
    id: 'manual',
    name: '手動実行モード',
    description: 'Render対応・最高プライバシー保護',
    icon: User,
    color: 'green',
    features: [
      '✅ ブラウザのローカルストレージのみに保存',
      '✅ Renderサーバーには一切保存されない',
      '✅ 運営者・Render・第三者のアクセス不可',
      '✅ 国際的なデータ移転なし',
      '✅ プライバシー法令に完全対応',
      '✅ ユーザーが完全にコントロール'
    ],
    benefits: [
      '🛡️ GDPR・個人情報保護法に完全準拠',
      '🌍 データの海外移転リスクなし',
      '🔒 Renderの管理者もアクセス不可',
      '⚖️ 運営者の法的責任を最小化',
      '💻 ユーザーのプライバシーを最大限保護'
    ]
  };

  // 危険なモード（参考表示のみ）
  const riskyModes = [
    {
      id: 'scheduled',
      name: 'スケジュール実行モード',
      description: 'サーバー保存（非推奨）',
      risks: [
        '⚠️ Renderサーバー（アメリカ）に保存',
        '⚠️ Render管理者がアクセス可能',
        '⚠️ アメリカの法律・政府要請の対象',
        '⚠️ 運営者の法的責任が増大',
        '⚠️ プライバシー法令違反のリスク'
      ]
    },
    {
      id: 'continuous',
      name: '継続実行モード',
      description: 'サーバー永続保存（高リスク）',
      risks: [
        '🚨 他人のAPIキーを永続的に保存',
        '🚨 データ保護法の厳格な対象',
        '🚨 国際的なデータ移転規制',
        '🚨 高い法的・運営リスク',
        '🚨 Renderのプライバシーポリシー依存'
      ]
    }
  ];

  const handleModeSelect = (modeId) => {
    if (modeId !== 'manual') {
      alert('Renderデプロイメントでは手動実行モードのみを推奨します。継続自動化は法的リスクが高すぎます。');
      return;
    }
    
    setSelectedMode(modeId);
    if (onModeSelect) {
      onModeSelect(modeId, recommendedMode);
    }
  };

  return (
    <div className="space-y-6">
      {/* Render特有の警告 */}
      {showRenderWarning && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 border border-red-200 rounded-lg p-6"
        >
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-6 w-6 text-red-600 mt-1" />
            <div className="flex-1">
              <h4 className="font-bold text-red-900 text-lg mb-2">
                🚨 Renderデプロイメント時の重要な注意事項
              </h4>
              <div className="space-y-3 text-sm text-red-800">
                <p>
                  <strong>Renderにデプロイする場合、「サーバー保存」は以下を意味します：</strong>
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li><strong>保存場所</strong>：Renderのサーバー（アメリカのデータセンター）</li>
                  <li><strong>アクセス権</strong>：Render社の管理者・エンジニアがアクセス可能</li>
                  <li><strong>法的管轄</strong>：アメリカの法律・政府要請の対象</li>
                  <li><strong>運営者責任</strong>：データ保護法違反・漏洩時の重い責任</li>
                </ul>
                <div className="mt-4 p-3 bg-red-100 rounded border border-red-300">
                  <p className="font-medium">
                    ⚖️ <strong>推奨：手動実行モードのみ提供</strong>
                  </p>
                  <p>
                    他人のAPIキーをRenderに保存することは、法的リスクが非常に高く、
                    GDPR・個人情報保護法等の厳格な規制対象になります。
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowRenderWarning(false)}
                className="mt-4 text-sm text-red-600 hover:text-red-800 underline"
              >
                理解しました（この警告を閉じる）
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* ヘッダー */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Render対応・プライバシー保護モード
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Renderデプロイメントでは、法的リスクとプライバシー保護を考慮し、
          <strong>手動実行モードのみ</strong>を推奨します。
        </p>
      </div>

      {/* 推奨モード（手動実行） */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-xl border-2 border-green-300 bg-green-50"
      >
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-green-100 rounded-lg">
            <Shield className="h-8 w-8 text-green-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <h3 className="text-xl font-bold text-green-900">
                {recommendedMode.name}
              </h3>
              <span className="px-3 py-1 bg-green-200 text-green-800 text-sm font-medium rounded-full">
                推奨
              </span>
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <p className="text-green-800 mb-4">
              {recommendedMode.description}
            </p>

            {/* 特徴 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-green-900 mb-2">技術的特徴</h4>
                <ul className="space-y-1 text-sm text-green-800">
                  {recommendedMode.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-green-900 mb-2">法的・運営メリット</h4>
                <ul className="space-y-1 text-sm text-green-800">
                  {recommendedMode.benefits.map((benefit, index) => (
                    <li key={index}>{benefit}</li>
                  ))}
                </ul>
              </div>
            </div>

            <button
              onClick={() => handleModeSelect('manual')}
              className={`mt-4 px-6 py-3 rounded-lg font-medium transition-colors ${
                selectedMode === 'manual'
                  ? 'bg-green-600 text-white'
                  : 'bg-green-200 text-green-800 hover:bg-green-300'
              }`}
            >
              {selectedMode === 'manual' ? '✓ 選択済み' : 'このモードを選択'}
            </button>
          </div>
        </div>
      </motion.div>

      {/* 危険なモード（警告表示） */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <span>高リスクモード（Renderでは非推奨）</span>
        </h3>
        
        {riskyModes.map((mode) => (
          <motion.div
            key={mode.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-lg border border-red-200 bg-red-50"
          >
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-1" />
              <div className="flex-1">
                <h4 className="font-semibold text-red-900 mb-2">
                  {mode.name}
                </h4>
                <p className="text-sm text-red-800 mb-3">
                  {mode.description}
                </p>
                <div>
                  <h5 className="font-medium text-red-900 mb-1">法的・プライバシーリスク：</h5>
                  <ul className="text-sm text-red-700 space-y-1">
                    {mode.risks.map((risk, index) => (
                      <li key={index}>{risk}</li>
                    ))}
                  </ul>
                </div>
                <div className="mt-3 p-2 bg-red-100 rounded border border-red-300">
                  <p className="text-xs text-red-800">
                    <strong>警告：</strong> このモードはRenderデプロイメントでは推奨されません。
                    高い法的責任とプライバシーリスクを伴います。
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Render特有の説明 */}
      <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-start space-x-3">
          <Info className="h-6 w-6 text-blue-600 mt-1" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-3">
              Renderデプロイメント時の考慮事項
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-blue-800">
              <div>
                <h5 className="font-medium mb-2">技術的制約</h5>
                <ul className="space-y-1">
                  <li>• サーバー = Renderのクラウドサーバー</li>
                  <li>• データセンター = アメリカ</li>
                  <li>• アクセス権 = Render社が保有</li>
                  <li>• 管轄法 = アメリカの法律</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium mb-2">運営者への影響</h5>
                <ul className="space-y-1">
                  <li>• データ保護法の厳格な対象</li>
                  <li>• 国際的なデータ移転規制</li>
                  <li>• プライバシー侵害の法的責任</li>
                  <li>• 高額な罰金・制裁のリスク</li>
                </ul>
              </div>
            </div>
            <div className="mt-4 p-3 bg-blue-100 rounded border border-blue-300">
              <p className="text-sm font-medium text-blue-900">
                💡 <strong>推奨アプローチ</strong>：手動実行モードのみ提供し、
                「継続自動化が必要なユーザーは各自でVPSにセルフホスティング」と案内する
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 選択確認 */}
      {selectedMode === 'manual' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-green-100 rounded-lg border border-green-300"
        >
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <div>
              <p className="font-medium text-green-900">
                ✅ 手動実行モードが選択されました
              </p>
              <p className="text-sm text-green-800">
                Render対応・最高のプライバシー保護・法的安全性を確保できます
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AutomationModeSelector;