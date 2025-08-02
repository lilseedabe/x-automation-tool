import React, { useState, useEffect } from "react";
import apiClient from "../utils/api";
import { Star, Trash2, Plus, Bot } from "lucide-react";

const FavoriteUsersManager = () => {
  const [favoriteUsers, setFavoriteUsers] = useState([]);
  const [newUsername, setNewUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFavoriteUsers();
  }, []);

  const fetchFavoriteUsers = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getFavoriteUsers();
      setFavoriteUsers(res);
    } catch (e) {
      setError("お気に入りユーザーの取得に失敗しました");
    }
    setLoading(false);
  };

  const handleAddUser = async () => {
    if (!newUsername.trim()) return;
    setLoading(true);
    try {
      await apiClient.addFavoriteUser(newUsername.trim());
      setNewUsername("");
      fetchFavoriteUsers();
    } catch (e) {
      setError("追加に失敗しました");
    }
    setLoading(false);
  };

  const handleDeleteUser = async (id) => {
    setLoading(true);
    try {
      await apiClient.deleteFavoriteUser(id);
      fetchFavoriteUsers();
    } catch (e) {
      setError("削除に失敗しました");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto mt-8 space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-yellow-100 rounded-lg">
          <Star className="h-6 w-6 text-yellow-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">お気に入りユーザー管理</h2>
          <p className="text-gray-600">
            FreeプランでもAI自動化でお気に入りユーザーの新着ツイートに自動いいね・リポスト
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ユーザー追加</h3>
        <div className="flex space-x-3 mb-4">
          <input
            type="text"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            placeholder="ユーザー名（@なし）"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          />
          <button
            onClick={handleAddUser}
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>追加</span>
          </button>
        </div>
        {error && (
          <div className="p-2 bg-red-50 border border-red-200 rounded-lg mb-2 text-red-800 text-sm">
            {error}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">お気に入りユーザー一覧</h3>
        {loading ? (
          <div className="text-gray-500">読み込み中...</div>
        ) : (
          <ul className="space-y-3">
            {favoriteUsers.length === 0 ? (
              <li className="text-gray-500">お気に入りユーザーが登録されていません</li>
            ) : (
              favoriteUsers.map((user) => (
                <li key={user.id} className="flex items-center justify-between bg-yellow-50 rounded-lg p-3">
                  <span className="font-medium text-yellow-900">@{user.username}</span>
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className="p-2 bg-red-100 rounded hover:bg-red-200"
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                </li>
              ))
            )}
          </ul>
        )}
      </div>

      <div className="bg-gradient-to-r from-yellow-50 to-blue-50 rounded-xl p-6 border border-yellow-200">
        <div className="flex items-start space-x-3">
          <Bot className="h-6 w-6 text-blue-600 mt-1" />
          <div>
            <h4 className="font-medium text-blue-900 mb-2">
              AI自動化エンジン
            </h4>
            <div className="text-sm text-blue-800">
              登録したユーザーの新着ツイートにAI判定で自動いいね・リポストを実行します。人間らしいタイミングで安全に動作します。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FavoriteUsersManager;