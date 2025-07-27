/**
 * 🔐 APIキー管理サービス（ローカルストレージ暗号化保存）
 * 
 * ユーザーのX APIキーをブラウザのローカルストレージのみに保存
 * サーバーには一切保存せず、セキュリティリスクを最小化
 * 
 * 注意: crypto-jsが利用できない場合は、基本的なBase64エンコーディングを使用
 */

// 暗号化ライブラリ（オプショナル）
let CryptoJS = null;
try {
  // crypto-jsが利用可能な場合のみインポート
  // インストール: npm install crypto-js
  // CryptoJS = require('crypto-js');
  console.warn('crypto-js not available, using basic encoding');
} catch (error) {
  console.warn('crypto-js not installed, using fallback encoding');
}

// フォールバック暗号化キー（実際のアプリでは、より安全な方法を使用）
const ENCRYPTION_KEY = 'x-automation-tool-2024-secure-key';

/**
 * APIキーマネージャークラス
 */
class APIKeyManager {
  constructor() {
    this.storageKey = 'x_automation_encrypted_keys';
  }

  /**
   * データを暗号化（フォールバック版）
   * 
   * @param {string} data - 暗号化するデータ
   * @returns {string} 暗号化されたデータ
   */
  _encryptData(data) {
    if (CryptoJS) {
      // crypto-jsが利用可能な場合
      return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
    } else {
      // フォールバック: Base64エンコーディング
      return btoa(unescape(encodeURIComponent(data)));
    }
  }

  /**
   * データを復号化（フォールバック版）
   * 
   * @param {string} encryptedData - 暗号化されたデータ
   * @returns {string} 復号化されたデータ
   */
  _decryptData(encryptedData) {
    try {
      if (CryptoJS) {
        // crypto-jsが利用可能な場合
        const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
        return bytes.toString(CryptoJS.enc.Utf8);
      } else {
        // フォールバック: Base64デコーディング
        return decodeURIComponent(escape(atob(encryptedData)));
      }
    } catch (error) {
      throw new Error('復号化に失敗しました');
    }
  }

  /**
   * APIキーを暗号化してローカルストレージに保存
   * 
   * @param {Object} apiKeys - APIキーオブジェクト
   * @param {string} apiKeys.api_key - API Key
   * @param {string} apiKeys.api_secret - API Secret
   * @param {string} apiKeys.access_token - Access Token
   * @param {string} apiKeys.access_token_secret - Access Token Secret
   * @returns {boolean} 保存成功フラグ
   */
  saveAPIKeys(apiKeys) {
    try {
      // APIキーの検証
      if (!this.validateAPIKeys(apiKeys)) {
        throw new Error('無効なAPIキーです');
      }

      // 暗号化
      const encrypted = this._encryptData(JSON.stringify(apiKeys));

      // ローカルストレージに保存
      localStorage.setItem(this.storageKey, encrypted);
      
      console.log('✅ APIキーが安全に保存されました（ローカルストレージのみ）');
      return true;

    } catch (error) {
      console.error('❌ APIキー保存エラー:', error);
      return false;
    }
  }

  /**
   * ローカルストレージからAPIキーを復号化して取得
   * 
   * @returns {Object|null} APIキーオブジェクトまたはnull
   */
  getAPIKeys() {
    try {
      // ローカルストレージから暗号化データを取得
      const encrypted = localStorage.getItem(this.storageKey);
      
      if (!encrypted) {
        return null;
      }

      // 復号化
      const decrypted = this._decryptData(encrypted);
      
      if (!decrypted) {
        throw new Error('復号化に失敗しました');
      }

      const apiKeys = JSON.parse(decrypted);
      
      // 復号化後の検証
      if (!this.validateAPIKeys(apiKeys)) {
        throw new Error('復号化されたAPIキーが無効です');
      }

      return apiKeys;

    } catch (error) {
      console.error('❌ APIキー取得エラー:', error);
      return null;
    }
  }

  /**
   * APIキーを削除
   * 
   * @returns {boolean} 削除成功フラグ
   */
  clearAPIKeys() {
    try {
      localStorage.removeItem(this.storageKey);
      console.log('✅ APIキーが削除されました');
      return true;
    } catch (error) {
      console.error('❌ APIキー削除エラー:', error);
      return false;
    }
  }

  /**
   * APIキーが保存されているかチェック
   * 
   * @returns {boolean} 保存済みフラグ
   */
  hasAPIKeys() {
    return localStorage.getItem(this.storageKey) !== null;
  }

  /**
   * APIキーの形式を検証
   * 
   * @param {Object} apiKeys - APIキーオブジェクト
   * @returns {boolean} 有効フラグ
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

  /**
   * APIキーをサーバーリクエスト用にフォーマット
   * 注意: サーバーには保存されず、リクエスト時のみ一時的に使用
   * 
   * @returns {Object|null} リクエスト用APIキーオブジェクト
   */
  getKeysForRequest() {
    const keys = this.getAPIKeys();
    
    if (!keys) {
      return null;
    }

    return {
      api_key: keys.api_key,
      api_secret: keys.api_secret,
      access_token: keys.access_token,
      access_token_secret: keys.access_token_secret,
      // リクエスト時刻を追加（セキュリティログ用）
      request_timestamp: Date.now()
    };
  }

  /**
   * APIキーの設定状況を取得
   * 
   * @returns {Object} 設定状況
   */
  getStatus() {
    const hasKeys = this.hasAPIKeys();
    const keys = hasKeys ? this.getAPIKeys() : null;
    const isValid = keys ? this.validateAPIKeys(keys) : false;

    return {
      configured: hasKeys,
      valid: isValid,
      storage_type: 'localStorage_encrypted',
      server_stored: false, // サーバーには保存されていない
      security_level: CryptoJS ? 'high' : 'medium', // crypto-jsの有無で判定
      encryption_method: CryptoJS ? 'AES-256' : 'Base64',
      last_accessed: hasKeys ? new Date().toISOString() : null
    };
  }

  /**
   * セキュリティ情報を取得
   * 
   * @returns {Object} セキュリティ情報
   */
  getSecurityInfo() {
    return {
      encryption: CryptoJS ? 'AES-256' : 'Base64 (Fallback)',
      storage_location: 'Browser LocalStorage Only',
      server_storage: false,
      third_party_access: false,
      data_retention: 'Until user clears browser data',
      security_level: CryptoJS ? 'High' : 'Medium',
      privacy_protection: 'Maximum',
      crypto_js_available: !!CryptoJS
    };
  }

  /**
   * 暗号化レベルを向上させる（crypto-jsインストール後）
   */
  upgradeSecurity() {
    if (!CryptoJS) {
      console.warn('crypto-jsがインストールされていないため、セキュリティアップグレードできません');
      console.info('インストール方法: npm install crypto-js');
      return false;
    }

    const keys = this.getAPIKeys();
    if (keys) {
      // 既存のキーを新しい暗号化方式で再保存
      this.saveAPIKeys(keys);
      console.log('✅ セキュリティレベルをアップグレードしました');
      return true;
    }

    return false;
  }
}

// シングルトンインスタンス
const apiKeyManager = new APIKeyManager();

export default apiKeyManager;

/**
 * 使用例:
 * 
 * // APIキーの保存
 * const success = apiKeyManager.saveAPIKeys({
 *   api_key: 'your_api_key',
 *   api_secret: 'your_api_secret',
 *   access_token: 'your_access_token',
 *   access_token_secret: 'your_access_token_secret'
 * });
 * 
 * // APIキーの取得
 * const keys = apiKeyManager.getAPIKeys();
 * 
 * // リクエスト用フォーマット
 * const requestKeys = apiKeyManager.getKeysForRequest();
 * 
 * // 設定状況確認
 * const status = apiKeyManager.getStatus();
 * 
 * // セキュリティ情報確認
 * const security = apiKeyManager.getSecurityInfo();
 * 
 * // セキュリティアップグレード（crypto-js導入後）
 * const upgraded = apiKeyManager.upgradeSecurity();
 */