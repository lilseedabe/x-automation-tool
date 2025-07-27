/**
 * 🔒 法的同意モーダル（Render PostgreSQL利用時）
 * 
 * ユーザーからの明確な法的同意を取得
 * データ保存・国際移転のリスクを詳細説明
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  Shield,
  Globe,
  Database,
  Lock,
  Eye,
  CheckCircle,
  X,
  FileText,
  Scale,
  Clock,
  Server,
  MapPin,
} from 'lucide-react';

const LegalConsentModal = ({ isOpen, onClose, onConsent, mode = 'scheduled' }) => {
  const [consents, setConsents] = useState({
    dataStorage: false,
    internationalTransfer: false,
    renderAccess: false,
    legalRisks: false,
    dataRetention: false
  });
  const [retentionDays, setRetentionDays] = useState(1);
  const [userPassword, setUserPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [hasReadAll, setHasReadAll] = useState(false);

  const handleConsentChange = (type, value) => {
    setConsents(prev => ({
      ...prev,
      [type]: value
    }));
  };

  const isAllConsentsGiven = () => {
    return Object.values(consents).every(consent => consent) &&
           userPassword.length >= 8 &&
           userPassword === confirmPassword &&
           hasReadAll;
  };

  const handleSubmit = () => {
    if (!isAllConsentsGiven()) return;

    const consentData = {
      consents,
      retentionDays,
      userPassword,
      timestamp: new Date().toISOString(),
      consentVersion: '1.0',
      ipAddress: 'user_ip', // 実際のアプリでは実IPを取得
      userAgent: navigator.userAgent
    };

    onConsent(consentData);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* ヘッダー */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <Scale className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    法的同意・免責事項
                  </h3>
                  <p className="text-sm text-gray-600">
                    Render PostgreSQL利用時の重要な同意事項
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* 重要な警告 */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-6 w-6 text-red-600 mt-1" />
                <div>
                  <h4 className="font-bold text-red-900 text-lg mb-3">
                    ⚠️ 重要：データ保存場所とリスクについて
                  </h4>
                  <div className="space-y-3 text-sm text-red-800">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <MapPin className="h-4 w-4" />
                          <span className="font-medium">保存場所</span>
                        </div>
                        <p>Render PostgreSQL（アメリカのデータセンター）</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Globe className="h-4 w-4" />
                          <span className="font-medium">法的管轄</span>
                        </div>
                        <p>アメリカ合衆国の法律が適用</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Eye className="h-4 w-4" />
                          <span className="font-medium">第三者アクセス</span>
                        </div>
                        <p>Render社の管理者が技術的にアクセス可能</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Server className="h-4 w-4" />
                          <span className="font-medium">政府要請</span>
                        </div>
                        <p>アメリカ政府による開示要請の可能性</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 技術的保護措置 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-start space-x-3">
                <Lock className="h-6 w-6 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-medium text-blue-900 mb-3">
                    🔒 技術的保護措置
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                    <ul className="space-y-1">
                      <li>✅ AES-256暗号化</li>
                      <li>✅ PBKDF2HMAC鍵導出</li>
                      <li>✅ ユーザー専用パスワード</li>
                    </ul>
                    <ul className="space-y-1">
                      <li>✅ 運営者は復号化不可</li>
                      <li>✅ 自動削除機能</li>
                      <li>✅ ユーザー完全制御</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* 法的同意項目 */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">法的同意事項（すべて必須）</h4>
              
              {/* データ保存同意 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consents.dataStorage}
                    onChange={(e) => handleConsentChange('dataStorage', e.target.checked)}
                    className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      データベース保存への同意
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      私のAPIキーがRender PostgreSQL（アメリカ）に暗号化保存されることに同意します。
                      これは国際的なデータ移転を伴います。
                    </p>
                  </div>
                </label>
              </div>

              {/* 国際データ移転同意 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consents.internationalTransfer}
                    onChange={(e) => handleConsentChange('internationalTransfer', e.target.checked)}
                    className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      国際データ移転への同意
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      私の個人データ（APIキー）が日本国外（アメリカ）に移転されることを理解し、
                      GDPR・個人情報保護法に基づく権利を行使できることに同意します。
                    </p>
                  </div>
                </label>
              </div>

              {/* 第三者アクセスリスク */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consents.renderAccess}
                    onChange={(e) => handleConsentChange('renderAccess', e.target.checked)}
                    className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      第三者アクセスリスクの承諾
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Render社の管理者・エンジニアが技術的にデータにアクセス可能であること、
                      アメリカ政府の要請により開示される可能性があることを理解し承諾します。
                    </p>
                  </div>
                </label>
              </div>

              {/* 法的責任 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consents.legalRisks}
                    onChange={(e) => handleConsentChange('legalRisks', e.target.checked)}
                    className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      法的リスクの理解
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      データ漏洩・不正アクセス等のリスクを理解し、運営者の責任範囲を超える
                      損害については自己責任であることに同意します。
                    </p>
                  </div>
                </label>
              </div>

              {/* データ保持期間 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consents.dataRetention}
                    onChange={(e) => handleConsentChange('dataRetention', e.target.checked)}
                    className="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      データ保持期間の設定
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      指定した期間後にデータが自動削除されることに同意します。
                    </p>
                    <div className="mt-3">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        自動削除期間（推奨：1日）
                      </label>
                      <select
                        value={retentionDays}
                        onChange={(e) => setRetentionDays(parseInt(e.target.value))}
                        className="w-40 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                      >
                        <option value={1}>1日後</option>
                        <option value={3}>3日後</option>
                        <option value={7}>7日後</option>
                        <option value={30}>30日後</option>
                      </select>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* 暗号化パスワード設定 */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-4">暗号化パスワード設定</h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    暗号化パスワード（8文字以上）
                  </label>
                  <input
                    type="password"
                    value={userPassword}
                    onChange={(e) => setUserPassword(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="強力なパスワードを設定してください"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    このパスワードでAPIキーが暗号化されます。忘れると復元できません。
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    パスワード確認
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="同じパスワードを再入力"
                  />
                  {userPassword && confirmPassword && userPassword !== confirmPassword && (
                    <p className="text-xs text-red-600 mt-1">パスワードが一致しません</p>
                  )}
                </div>
              </div>
            </div>

            {/* 最終確認 */}
            <div className="border border-yellow-300 bg-yellow-50 rounded-lg p-4">
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={hasReadAll}
                  onChange={(e) => setHasReadAll(e.target.checked)}
                  className="mt-1 w-4 h-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <p className="font-medium text-yellow-900">
                    最終確認
                  </p>
                  <p className="text-sm text-yellow-800 mt-1">
                    上記のすべての内容を理解し、リスクを承知の上で、
                    自己責任において利用することに同意します。
                  </p>
                </div>
              </label>
            </div>

            {/* アクションボタン */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                キャンセル
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isAllConsentsGiven()}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  isAllConsentsGiven()
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isAllConsentsGiven() ? '同意してデータベース保存を開始' : '全ての項目に同意が必要です'}
              </button>
            </div>

            {/* 代替案の提示 */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-green-900">より安全な代替案</p>
                  <p className="text-sm text-green-800 mt-1">
                    プライバシーを最重視する場合は、
                    <strong>手動実行モード</strong>（ローカルストレージのみ）または
                    <strong>自分専用VPSでのセルフホスティング</strong>を推奨します。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LegalConsentModal;