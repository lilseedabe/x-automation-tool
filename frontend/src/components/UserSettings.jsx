/**
 * 🤖 X自動反応ツール - ユーザー設定（統合版）
 * 
 * ローカル保存 vs シンVPS保存の選択機能付き
 * ユーザーのニーズに応じた柔軟な設定
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Key,
  Save,
  Eye,
  EyeOff,
  CheckCircle,
  AlertTriangle,
  Info,
  Shield,
  Clock,
  Target,
  Zap,
  User,
  Bell,
  Lock,
  Trash2,
  RefreshCw,
  ExternalLink,
  HelpCircle,
  Globe,
  Database,
  Monitor,
  Server,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { vpsAPIKeyManager } from '../services/apiKeyManager';

const UserSettings = () => {
  const [activeTab, setActiveTab] = useState('api');
  const [userPassword, setUserPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const [showKeys, setShowKeys] = useState({
    api_key: false,
    api_secret: false,
    access_token: false,
    access_token_secret: false,
  });

  const [apiSettings, setApiSettings] = useState({
    api_key: '',
    api_secret: '',
    access_token: '',
    access_token_secret: '',
  });

  const [automationSettings, setAutomationSettings] = useState({
    max_daily_actions: 30,
    max_users_per_session: 10,
    auto_like_enabled: true,
    auto_retweet_enabled: true,
    safety_mode: true,
    min_delay_minutes: 2,
    max_delay_minutes: 15,
    active_hours_start: 8,
    active_hours_end: 22,
    quality_threshold: 70,
    safety_threshold: 80,
    random_selection: true,
    min_engagement_score: 60,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);

  // コンポーネント初期化時にVPS PostgreSQLからAPIキー状態を読み込み
  useEffect(() => {
    updateVPSAPIKeyStatus();
  }, []);

  const updateVPSAPIKeyStatus = async () => {
    try {
      const status = await vpsAPIKeyManager.getStatus();
      setApiKeyStatus(status);
      console.log('✅ VPS APIキー状態を更新:', status);
    } catch (error) {
      console.error('❌ VPS APIキー状態取得エラー:', error);
      setApiKeyStatus({
        configured: false,
        cached: false,
        valid: false,
        storage_type: 'VPS_PostgreSQL',
        server_stored: true,
        security_level: 'maximum',
        encryption_method: 'AES-256-GCM + PBKDF2',
        operator_blind: true,
        error: error.message
      });
    }
  };

  const toggleShowKey = (keyName) => {
    setShowKeys(prev => ({
      ...prev,
      [keyName]: !prev[keyName]
    }));
  };

  const handleApiSettingChange = (key, value) => {
    setApiSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setSaveStatus(null);

    try {
      // パスワード確認
      if (!userPassword) {
        throw new Error('暗号化のためにユーザーパスワードが必要です');
      }

      // VPS PostgreSQLに暗号化保存
      const result = await vpsAPIKeyManager.saveAPIKeys(apiSettings, userPassword);
      
      if (result.success) {
        setSaveStatus({
          type: 'success',
          message: 'APIキーがVPS PostgreSQLに運営者ブラインド暗号化で保存されました'
        });
        toast.success('VPS PostgreSQL保存完了');
        await updateVPSAPIKeyStatus();
        
        // パスワードをクリア（セキュリティ）
        setUserPassword('');
      } else {
        throw new Error('VPS保存に失敗しました');
      }
      
      // 3秒後にメッセージを消去
      setTimeout(() => setSaveStatus(null), 3000);
      
    } catch (error) {
      console.error('VPS設定保存エラー:', error);
      setSaveStatus({ type: 'error', message: `設定の保存に失敗しました: ${error.message}` });
      toast.error('設定の保存に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setIsSaving(true);
    
    try {
      // パスワード確認
      if (!userPassword) {
        throw new Error('APIキーテストのためにユーザーパスワードが必要です');
      }

      // VPS PostgreSQLのAPIキーでテスト
      const result = await vpsAPIKeyManager.testAPIKeys(userPassword);
      
      if (result.is_valid) {
        setSaveStatus({
          type: 'success',
          message: `X API接続テスト成功！ @${result.x_username} として認証されました`
        });
        toast.success('X API接続テスト成功！');
        await updateVPSAPIKeyStatus();
      } else {
        throw new Error(result.error_message || 'APIキーが無効です');
      }
      
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      console.error('VPS接続テストエラー:', error);
      setSaveStatus({ type: 'error', message: `X API接続テスト失敗: ${error.message}` });
      toast.error('X API接続テスト失敗');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearAPIKeys = async () => {
    if (window.confirm('VPS PostgreSQLからAPIキーを削除しますか？この操作は元に戻せません。')) {
      try {
        setIsSaving(true);
        
        const result = await vpsAPIKeyManager.deleteAPIKeys();
        
        if (result.success) {
          setApiSettings({
            api_key: '',
            api_secret: '',
            access_token: '',
            access_token_secret: '',
          });
          setUserPassword('');
          await updateVPSAPIKeyStatus();
          toast.success('VPS PostgreSQLからAPIキーを削除しました');
        } else {
          throw new Error('削除に失敗しました');
        }
      } catch (error) {
        console.error('VPS APIキー削除エラー:', error);
        toast.error(`削除に失敗しました: ${error.message}`);
      } finally {
        setIsSaving(false);
      }
    }
  };

  const tabs = [
    { id: 'api', name: 'X API設定', icon: Key },
    { id: 'automation', name: '自動化設定', icon: Zap },
    { id: 'privacy', name: 'プライバシー', icon: Shield },
  ];

  const isAPIKeysValid = apiSettings.api_key && apiSettings.api_secret &&
                         apiSettings.access_token && apiSettings.access_token_secret &&
                         apiSettings.api_key.length > 10 && apiSettings.api_secret.length > 20 &&
                         apiSettings.access_token.length > 20 && apiSettings.access_token_secret.length > 20;

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            設定
          </h1>
          <p className="text-gray-600">
            VPS PostgreSQL完全管理でプライバシー最優先
          </p>
        </div>
        
        {activeTab === 'api' && (
          <button
            onClick={handleSaveSettings}
            disabled={isSaving || !isAPIKeysValid}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>保存中...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>VPS PostgreSQL保存</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* 保存ステータス */}
      {saveStatus && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-lg border ${
            saveStatus.type === 'success' 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : 'bg-red-50 border-red-200 text-red-800'
          }`}
        >
          <div className="flex items-center space-x-2">
            {saveStatus.type === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-600" />
            )}
            <span className="font-medium">{saveStatus.message}</span>
          </div>
        </motion.div>
      )}

      {/* VPS PostgreSQL設定表示 */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <Server className="h-5 w-5 text-green-600" />
          <div>
            <h4 className="font-medium text-green-900">VPS PostgreSQL完全管理</h4>
            <p className="text-sm text-green-800 mt-1">
              <strong>保存方式:</strong> 運営者ブラインド暗号化（AES-256-GCM + PBKDF2）
            </p>
            <p className="text-xs text-green-700 mt-1">
              月額1,000円・最高レベルのセキュリティ・完全プライバシー保護
            </p>
          </div>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* X API設定タブ */}
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Key className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    X API認証設定
                  </h3>
                  <p className="text-sm text-gray-500">
                    VPS PostgreSQL完全管理・運営者ブラインド暗号化
                  </p>
                </div>
              </div>

              {/* APIキー状態表示 */}
              {apiKeyStatus && (
                <div className={`p-4 rounded-lg border ${
                  apiKeyStatus.valid 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-yellow-50 border-yellow-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    {apiKeyStatus.valid ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    )}
                    <div>
                      <p className={`font-medium ${
                        apiKeyStatus.valid ? 'text-green-900' : 'text-yellow-900'
                      }`}>
                        {apiKeyStatus.configured ?
                          (apiKeyStatus.cached ? 'APIキー設定済み（キャッシュあり）' : 'APIキー設定済み（復号必要）') :
                          'APIキーが未設定'
                        }
                      </p>
                      <div className="text-xs mt-1 space-x-4">
                        <span>保存方式: VPS PostgreSQL</span>
                        <span>暗号化: {apiKeyStatus.encryption_method}</span>
                        <span>セキュリティ: {apiKeyStatus.security_level}</span>
                        <span>運営者ブラインド: {apiKeyStatus.operator_blind ? '有効' : '無効'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* API取得方法の案内 */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start space-x-3">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900 mb-2">
                      X APIキーの取得方法
                    </h4>
                    <ol className="text-sm text-blue-800 space-y-1">
                      <li>1. <a href="https://developer.twitter.com/" target="_blank" rel="noopener noreferrer" className="underline">X Developer Portal</a> にアクセス</li>
                      <li>2. 新しいアプリケーションを作成</li>
                      <li>3. 「Keys and Tokens」タブで以下の4つのキーを生成</li>
                      <li>4. 下記フォームに入力して保存</li>
                    </ol>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-6">
                {/* API Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key (Consumer Key) <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.api_key ? 'text' : 'password'}
                      value={apiSettings.api_key}
                      onChange={(e) => handleApiSettingChange('api_key', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                      placeholder="your_api_key_here"
                    />
                    <button
                      type="button"
                      onClick={() => toggleShowKey('api_key')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showKeys.api_key ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* API Secret */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key Secret (Consumer Secret) <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.api_secret ? 'text' : 'password'}
                      value={apiSettings.api_secret}
                      onChange={(e) => handleApiSettingChange('api_secret', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                      placeholder="your_api_secret_here"
                    />
                    <button
                      type="button"
                      onClick={() => toggleShowKey('api_secret')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showKeys.api_secret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Access Token */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Token <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.access_token ? 'text' : 'password'}
                      value={apiSettings.access_token}
                      onChange={(e) => handleApiSettingChange('access_token', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                      placeholder="your_access_token_here"
                    />
                    <button
                      type="button"
                      onClick={() => toggleShowKey('access_token')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showKeys.access_token ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Access Token Secret */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Token Secret <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.access_token_secret ? 'text' : 'password'}
                      value={apiSettings.access_token_secret}
                      onChange={(e) => handleApiSettingChange('access_token_secret', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                      placeholder="your_access_token_secret_here"
                    />
                    <button
                      type="button"
                      onClick={() => toggleShowKey('access_token_secret')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showKeys.access_token_secret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* ユーザーパスワード入力 */}
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <Lock className="h-5 w-5 text-yellow-600" />
                  <h4 className="font-medium text-yellow-900">
                    暗号化用パスワード
                  </h4>
                </div>
                <p className="text-sm text-yellow-800 mb-3">
                  APIキーの保存・テストには、ログインパスワードが必要です（運営者ブラインド暗号化）
                </p>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={userPassword}
                    onChange={(e) => setUserPassword(e.target.value)}
                    className="w-full p-3 border border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent pr-10"
                    placeholder="ログインパスワードを入力"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-yellow-600 hover:text-yellow-800"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Groq API情報 */}
              <div className="mt-8 p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-3 mb-3">
                  <Shield className="h-5 w-5 text-green-600" />
                  <h4 className="font-medium text-green-900">
                    Groq AI分析サービス
                  </h4>
                </div>
                <p className="text-sm text-green-800 mb-2">
                  ✅ Groq AIキーは運営側で一括管理されており、設定不要です
                </p>
                <p className="text-xs text-green-700">
                  高度なAI分析機能が追加設定なしで利用できます
                </p>
              </div>

              {/* アクションボタン */}
              <div className="flex space-x-3">
                <button
                  onClick={handleTestConnection}
                  disabled={isSaving || !isAPIKeysValid || !userPassword}
                  className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>VPS接続テスト</span>
                </button>
                
                <button
                  onClick={handleClearAPIKeys}
                  disabled={!apiKeyStatus?.configured || isSaving}
                  className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>VPS APIキー削除</span>
                </button>
              </div>

              {(!isAPIKeysValid || !userPassword) && (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    {!isAPIKeysValid && "4つの必須キーをすべて正しく入力してください"}
                    {!isAPIKeysValid && !userPassword && " また、"}
                    {!userPassword && "ログインパスワードを入力してください"}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* 他のタブ（簡略版） */}
          {activeTab === 'automation' && (
            <div className="text-center py-8">
              <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">自動化設定（実装予定）</p>
            </div>
          )}

          {activeTab === 'privacy' && (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">プライバシー情報（実装予定）</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserSettings;