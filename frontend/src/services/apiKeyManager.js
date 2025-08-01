/**
 * 🔐 VPS PostgreSQL完全管理APIキーサービス
 * 
 * すべてのAPIキーはVPS PostgreSQLで運営者ブラインド暗号化管理
 * ローカルストレージは一切使用しない完全サーバーサイド管理
 * 
 * セキュリティ仕様:
 * - AES-256-GCM暗号化
 * - PBKDF2キー導出 (100,000回反復)
 * - 運営者ブラインド設計
 * - セッションベースキャッシュ
 */

/**
 * VPS PostgreSQL完全管理APIキーサービス
 */
class VPSAPIKeyManager {
  constructor() {
    this.baseURL = '/api/auth';
    console.log('🔐 VPS PostgreSQL APIキーマネージャー初期化完了');
  }

  /**
   * サーバーにキャッシュされたAPIキー状態確認
   */
  async checkCachedStatus() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return { has_cached_keys: false, message: 'ログインが必要です' };
      }

      const response = await fetch(`${this.baseURL}/api-keys/cached`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ VPS APIキー状態確認成功:', data);
        return data;
      } else {
        console.warn('⚠️ VPS APIキー状態確認失敗:', response.status);
        return { has_cached_keys: false, message: 'サーバーエラー' };
      }
    } catch (error) {
      console.error('❌ VPS APIキー状態確認エラー:', error);
      return { has_cached_keys: false, message: 'ネットワークエラー' };
    }
  }

  /**
   * APIキーをVPS PostgreSQLに暗号化保存
   */
  async saveAPIKeys(apiKeys, userPassword) {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('ログインが必要です');
      }

      const response = await fetch(`${this.baseURL}/api-keys`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKeys.api_key,
          api_secret: apiKeys.api_secret,
          access_token: apiKeys.access_token,
          access_token_secret: apiKeys.access_token_secret,
          user_password: userPassword
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ VPS APIキー保存成功:', data);
        return { success: true, data };
      } else {
        const errorData = await response.json();
        console.error('❌ VPS APIキー保存失敗:', errorData);
        throw new Error(errorData.detail || 'サーバーエラー');
      }
    } catch (error) {
      console.error('❌ VPS APIキー保存エラー:', error);
      throw error;
    }
  }

  /**
   * VPSからAPIキー状態取得（復号なし）
   */
  async getAPIKeyStatus() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('ログインが必要です');
      }

      const response = await fetch(`${this.baseURL}/api-keys`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ VPS APIキー状態取得成功:', data);
        return data;
      } else if (response.status === 404) {
        console.log('⚠️ APIキーが登録されていません');
        return null;
      } else {
        const errorData = await response.json();
        console.error('❌ VPS APIキー状態取得失敗:', errorData);
        throw new Error(errorData.detail || 'サーバーエラー');
      }
    } catch (error) {
      console.error('❌ VPS APIキー状態取得エラー:', error);
      throw error;
    }
  }

  /**
   * APIキーテスト（キャッシュ優先・VPS管理）
   */
  async testAPIKeys(userPassword) {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('ログインが必要です');
      }

      const response = await fetch(`${this.baseURL}/api-keys/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_password: userPassword
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ VPS APIキーテスト成功:', data);
        return data;
      } else {
        const errorData = await response.json();
        console.error('❌ VPS APIキーテスト失敗:', errorData);
        throw new Error(errorData.detail || 'テストに失敗しました');
      }
    } catch (error) {
      console.error('❌ VPS APIキーテストエラー:', error);
      throw error;
    }
  }

  /**
   * VPS PostgreSQLからAPIキー削除
   */
  async deleteAPIKeys() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('ログインが必要です');
      }

      const response = await fetch(`${this.baseURL}/api-keys`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ VPS APIキー削除成功:', data);
        return { success: true, data };
      } else {
        const errorData = await response.json();
        console.error('❌ VPS APIキー削除失敗:', errorData);
        throw new Error(errorData.detail || '削除に失敗しました');
      }
    } catch (error) {
      console.error('❌ VPS APIキー削除エラー:', error);
      throw error;
    }
  }

  /**
   * APIキーが設定済みかチェック
   */
  async hasAPIKeys() {
    try {
      const status = await this.getAPIKeyStatus();
      return status !== null;
    } catch (error) {
      console.error('❌ APIキー存在確認エラー:', error);
      return false;
    }
  }

  /**
   * APIキー設定の完全な状態を取得
   */
  async getStatus() {
    try {
      const [keyStatus, cachedStatus] = await Promise.all([
        this.getAPIKeyStatus(),
        this.checkCachedStatus()
      ]);

      return {
        configured: keyStatus !== null,
        cached: cachedStatus.has_cached_keys,
        valid: keyStatus?.is_valid || false,
        storage_type: 'VPS_PostgreSQL',
        server_stored: true,
        security_level: 'maximum',
        encryption_method: 'AES-256-GCM + PBKDF2',
        operator_blind: true,
        last_accessed: keyStatus?.last_used || null,
        created_at: keyStatus?.created_at || null,
        usage_count: keyStatus?.usage_count || 0
      };
    } catch (error) {
      console.error('❌ APIキー状態取得エラー:', error);
      return {
        configured: false,
        cached: false,
        valid: false,
        storage_type: 'VPS_PostgreSQL',
        server_stored: true,
        security_level: 'maximum',
        encryption_method: 'AES-256-GCM + PBKDF2',
        operator_blind: true,
        error: error.message
      };
    }
  }

  /**
   * セキュリティ情報を取得
   */
  getSecurityInfo() {
    return {
      encryption: 'AES-256-GCM',
      key_derivation: 'PBKDF2 (100,000 iterations)',
      storage_location: 'VPS PostgreSQL Database',
      server_storage: true,
      operator_blind: true,
      third_party_access: false,
      data_retention: 'Encrypted in PostgreSQL until user deletion',
      security_level: 'Maximum',
      privacy_protection: 'Operator Blind Design',
      cost_efficiency: '月額1,000円での運用',
      local_storage: false,
      browser_dependency: false
    };
  }

  /**
   * APIキーの基本的な形式検証（サーバー送信前チェック）
   */
  validateAPIKeys(apiKeys) {
    if (!apiKeys || typeof apiKeys !== 'object') {
      return false;
    }

    const requiredKeys = [
      'api_key',
      'api_secret', 
      'access_token',
      'access_token_secret'
    ];

    // 必須キーの存在チェック
    for (const key of requiredKeys) {
      if (!apiKeys[key] || typeof apiKeys[key] !== 'string' || apiKeys[key].trim() === '') {
        console.warn(`❌ 必須キーが不足: ${key}`);
        return false;
      }
    }

    // キーの長さチェック（最低限の長さ）
    if (apiKeys.api_key.length < 10 || 
        apiKeys.api_secret.length < 20 ||
        apiKeys.access_token.length < 20 ||
        apiKeys.access_token_secret.length < 20) {
      console.warn('❌ APIキーの長さが不正です');
      return false;
    }

    return true;
  }
}

// メインのVPS PostgreSQL管理マネージャー
const vpsAPIKeyManager = new VPSAPIKeyManager();

// 下位互換性のためのエイリアス
const serverAPIKeyManager = vpsAPIKeyManager;
const apiKeyManager = vpsAPIKeyManager;

export default vpsAPIKeyManager;
export { vpsAPIKeyManager, serverAPIKeyManager, apiKeyManager };

/**
 * VPS PostgreSQL完全管理の使用例:
 * 
 * import { vpsAPIKeyManager } from './services/apiKeyManager';
 * 
 * // APIキーの保存（VPS PostgreSQL）
 * const success = await vpsAPIKeyManager.saveAPIKeys({
 *   api_key: 'your_api_key',
 *   api_secret: 'your_api_secret',
 *   access_token: 'your_access_token',
 *   access_token_secret: 'your_access_token_secret'
 * }, 'user_password');
 * 
 * // APIキー状態確認
 * const status = await vpsAPIKeyManager.getStatus();
 * 
 * // キャッシュ状態確認
 * const cached = await vpsAPIKeyManager.checkCachedStatus();
 * 
 * // APIキーテスト
 * const testResult = await vpsAPIKeyManager.testAPIKeys('user_password');
 * 
 * // セキュリティ情報確認
 * const security = vpsAPIKeyManager.getSecurityInfo();
 */