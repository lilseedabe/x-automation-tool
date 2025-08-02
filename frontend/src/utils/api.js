/**
 * 🔗 X自動反応ツール - APIクライアント（AI分析統合版）
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

  // ===================================================================
  // 🤖 AI分析関連API
  // ===================================================================

  /**
   * 投稿内容をAI分析
   * @param {string} content - 分析対象の投稿内容
   * @param {string} analysisType - 分析タイプ（デフォルト: engagement_prediction）
   * @returns {Promise<Object>} AI分析結果
   */
  async analyzePost(content, analysisType = 'engagement_prediction') {
    return this.post('/api/ai/analyze-post', {
      content,
      analysis_type: analysisType
    });
  }

  /**
   * AI分析サマリーを取得
   * @returns {Promise<Object>} AI分析サマリー
   */
  async getAnalysisSummary() {
    return this.get('/api/ai/analysis-summary');
  }

  /**
   * 複数投稿の一括AI分析
   * @param {Array<string>} posts - 分析対象の投稿配列
   * @returns {Promise<Object>} バッチ分析結果
   */
  async batchAnalyzePosts(posts) {
    return this.post('/api/ai/batch-analyze', posts);
  }

  /**
   * AI分析システムのヘルスチェック
   * @returns {Promise<Object>} AIシステム状態
   */
  async checkAIHealth() {
    return this.get('/api/ai/health');
  }

  // ===================================================================
  // 🧠 高度なAI分析メソッド
  // ===================================================================

  /**
   * センチメント分析専用
   * @param {string} content - 分析対象の投稿内容
   * @returns {Promise<Object>} センチメント分析結果
   */
  async analyzeSentiment(content) {
    return this.analyzePost(content, 'sentiment_analysis');
  }

  /**
   * エンゲージメント予測専用
   * @param {string} content - 分析対象の投稿内容
   * @returns {Promise<Object>} エンゲージメント予測結果
   */
  async predictEngagement(content) {
    return this.analyzePost(content, 'engagement_prediction');
  }

  /**
   * キーワード抽出・最適化提案
   * @param {string} content - 分析対象の投稿内容
   * @returns {Promise<Object>} 最適化提案結果
   */
  async getOptimizationSuggestions(content) {
    return this.analyzePost(content, 'optimization_suggestions');
  }

  /**
   * 投稿リスク分析
   * @param {string} content - 分析対象の投稿内容
   * @returns {Promise<Object>} リスク分析結果
   */
  async analyzePostRisk(content) {
    return this.analyzePost(content, 'risk_assessment');
  }

  // ===================================================================
  // 📊 AI分析統計メソッド
  // ===================================================================

  /**
   * ユーザーのAI分析履歴を取得
   * @param {number} limit - 取得件数制限（デフォルト: 20）
   * @returns {Promise<Object>} 分析履歴
   */
  async getAnalysisHistory(limit = 20) {
    return this.get(`/api/ai/analysis-history?limit=${limit}`);
  }

  /**
   * AI分析トレンドデータを取得
   * @param {string} period - 期間（week, month, year）
   * @returns {Promise<Object>} トレンドデータ
   */
  async getAnalysisTrends(period = 'week') {
    return this.get(`/api/ai/trends?period=${period}`);
  }

  /**
   * 最高スコア投稿を取得
   * @param {number} limit - 取得件数制限（デフォルト: 10）
   * @returns {Promise<Object>} 最高スコア投稿一覧
   */
  async getTopScoringPosts(limit = 10) {
    return this.get(`/api/ai/top-scoring?limit=${limit}`);
  }

  // ===================================================================
  // 🔧 ユーティリティメソッド
  // ===================================================================

  /**
   * AI分析結果をローカルストレージにキャッシュ
   * @param {string} content - 投稿内容
   * @param {Object} analysisResult - 分析結果
   */
  cacheAnalysisResult(content, analysisResult) {
    try {
      const cacheKey = `ai_analysis_${btoa(content).substring(0, 20)}`;
      const cacheData = {
        content,
        result: analysisResult,
        timestamp: Date.now(),
        expires: Date.now() + (24 * 60 * 60 * 1000) // 24時間
      };
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('AI分析結果のキャッシュに失敗:', error);
    }
  }

  /**
   * キャッシュされたAI分析結果を取得
   * @param {string} content - 投稿内容
   * @returns {Object|null} キャッシュされた分析結果
   */
  getCachedAnalysisResult(content) {
    try {
      const cacheKey = `ai_analysis_${btoa(content).substring(0, 20)}`;
      const cacheData = localStorage.getItem(cacheKey);
      
      if (!cacheData) return null;
      
      const parsed = JSON.parse(cacheData);
      
      // 期限切れチェック
      if (Date.now() > parsed.expires) {
        localStorage.removeItem(cacheKey);
        return null;
      }
      
      return parsed.result;
    } catch (error) {
      console.warn('AI分析キャッシュの取得に失敗:', error);
      return null;
    }
  }

  /**
   * AI分析を実行（キャッシュ対応）
   * @param {string} content - 分析対象の投稿内容
   * @param {string} analysisType - 分析タイプ
   * @param {boolean} useCache - キャッシュ使用フラグ
   * @returns {Promise<Object>} AI分析結果
   */
  async analyzePostWithCache(content, analysisType = 'engagement_prediction', useCache = true) {
    // キャッシュチェック
    if (useCache) {
      const cachedResult = this.getCachedAnalysisResult(content);
      if (cachedResult) {
        console.log('🎯 キャッシュからAI分析結果を取得');
        return cachedResult;
      }
    }
    
    // API呼び出し
    const result = await this.analyzePost(content, analysisType);
    
    // キャッシュに保存
    if (useCache && result.success) {
      this.cacheAnalysisResult(content, result);
    }
    
    return result;
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
  getMyRateLimits,
  
  // AI分析メソッド
  analyzePost,
  getAnalysisSummary,
  batchAnalyzePosts,
  checkAIHealth,
  analyzeSentiment,
  predictEngagement,
  getOptimizationSuggestions,
  analyzePostRisk,
  getAnalysisHistory,
  getAnalysisTrends,
  getTopScoringPosts,
  analyzePostWithCache
} = apiClient;

// ===================================================================
// 📋 使用例
// ===================================================================

/*
使用例:

// 基本的なAI分析
const result = await apiClient.analyzePost("AIを活用した自動化ツールを開発中です！");

// キャッシュ対応のAI分析
const cachedResult = await apiClient.analyzePostWithCache("同じ投稿内容", "engagement_prediction", true);

// センチメント分析専用
const sentiment = await apiClient.analyzeSentiment("今日は良い天気ですね！");

// エンゲージメント予測
const engagement = await apiClient.predictEngagement("新機能をリリースしました🚀");

// AI分析サマリー取得
const summary = await apiClient.getAnalysisSummary();

// バッチ分析
const batchResults = await apiClient.batchAnalyzePosts([
  "投稿1の内容",
  "投稿2の内容", 
  "投稿3の内容"
]);

// AIシステムヘルスチェック
const aiHealth = await apiClient.checkAIHealth();

// 分析履歴取得
const history = await apiClient.getAnalysisHistory(10);

// トレンドデータ取得
const trends = await apiClient.getAnalysisTrends('month');

// 最高スコア投稿取得
const topPosts = await apiClient.getTopScoringPosts(5);
*/
