/**
 * 🔗 X自動反応ツール - APIクライアント
 * 
 * バックエンドAPIとの通信を管理
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'
);

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // 認証ヘッダーを取得
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && token !== 'null' ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }

  // APIリクエストの基本処理
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getAuthHeaders(),
      ...options
    };

    console.log(`🔗 API Request: ${options.method || 'GET'} ${url}`);
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          detail: `HTTP ${response.status}: ${response.statusText}` 
        }));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const data = await response.json();
      console.log(`✅ API Response: ${endpoint}`, data);
      return data;
    } catch (error) {
      console.error(`❌ API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // GET リクエスト
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  // POST リクエスト
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // PUT リクエスト
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // DELETE リクエスト
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // ===================================================================
  // 🔐 認証関連API
  // ===================================================================

  async login(credentials) {
    return this.post('/api/auth/login', credentials);
  }

  async logout() {
    return this.post('/api/auth/logout');
  }

  async register(userData) {
    return this.post('/api/auth/register', userData);
  }

  async getCurrentUser() {
    return this.get('/api/auth/me');
  }

  async changePassword(passwordData) {
    return this.post('/api/auth/change-password', passwordData);
  }

  // ===================================================================
  // 📊 ダッシュボード関連API
  // ===================================================================

  async getDashboardStats() {
    return this.get('/api/dashboard/stats');
  }

  // ===================================================================
  // 🤖 自動化関連API
  // ===================================================================

  async analyzeEngagingUsers(tweetUrl, userPassword) {
    return this.post('/api/automation/analyze-engaging-users', {
      tweet_url: tweetUrl,
      user_password: userPassword
    });
  }

  async executeActions(selectedActions, userPassword) {
    return this.post('/api/automation/execute-actions', {
      selected_actions: selectedActions,
      user_password: userPassword
    });
  }

  async getActionQueue() {
    return this.get('/api/automation/action-queue');
  }

  async createPost(content, userPassword, scheduleTime = null) {
    return this.post('/api/automation/post', {
      content,
      user_password: userPassword,
      schedule_time: scheduleTime
    });
  }

  // ===================================================================
  // 🚫 ブラックリスト関連API
  // ===================================================================

  async getBlacklist() {
    return this.get('/api/automation/blacklist');
  }

  async addToBlacklist(username, reason = null) {
    return this.post('/api/automation/blacklist', {
      username,
      reason
    });
  }

  async removeFromBlacklist(username) {
    return this.delete(`/api/automation/blacklist/${username}`);
  }

  // ===================================================================
  // 🔑 APIキー管理関連API
  // ===================================================================

  async storeApiKeys(apiKeyData) {
    return this.post('/api/auth/api-keys', apiKeyData);
  }

  async getApiKeyStatus() {
    return this.get('/api/auth/api-keys');
  }

  async testApiKeys(userPassword) {
    return this.post('/api/auth/api-keys/test', {
      user_password: userPassword
    });
  }

  async deleteApiKeys() {
    return this.delete('/api/auth/api-keys');
  }

  // ===================================================================
  // ⚙️ 自動化設定関連API
  // ===================================================================

  async getAutomationSettings() {
    return this.get('/api/auth/automation');
  }

  async updateAutomationSettings(settingsData) {
    return this.put('/api/auth/automation', settingsData);
  }

  async toggleAutomation(enabled) {
    return this.post('/api/auth/automation/toggle', { enabled });
  }

  // ===================================================================
  // 🏥 システム関連API
  // ===================================================================

  async getSystemInfo() {
    return this.get('/api/system/info');
  }

  async healthCheck() {
    return this.get('/health');
  }

  // ===================================================================
  // 📈 レート制限関連API
  // ===================================================================

  async getMyRateLimits() {
    return this.get('/api/rate-limits/my');
  }
}

// シングルトンインスタンスを作成
const apiClient = new APIClient();

// 🔧 修正: デフォルトエクスポート
export default apiClient;

// 🔧 修正: named export として 'api' を追加（エラー解決）
export const api = apiClient;

// 個別のAPI関数もエクスポート（後方互換性）
export const {
  login,
  logout,
  register,
  getCurrentUser,
  changePassword,
  getDashboardStats,
  analyzeEngagingUsers,
  executeActions,
  getActionQueue,
  createPost,
  getBlacklist,
  addToBlacklist,
  removeFromBlacklist,
  storeApiKeys,
  getApiKeyStatus,
  testApiKeys,
  deleteApiKeys,
  getAutomationSettings,
  updateAutomationSettings,
  toggleAutomation,
  getSystemInfo,
  healthCheck,
  getMyRateLimits
} = apiClient;
