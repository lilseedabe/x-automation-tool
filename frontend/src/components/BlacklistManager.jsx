/**
 * 🤖 X自動反応ツール - ブラックリスト管理コンポーネント
 * 
 * ブラックリストの表示・編集・管理機能
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, UserX, Plus, Search, X, AlertTriangle } from 'lucide-react';

const BlacklistManager = () => {
  const [blacklist, setBlacklist] = useState([
    {
      id: 1,
      username: 'spam_user',
      reason: 'スパムアカウント',
      blockType: 'both',
      addedDate: '2025-07-20'
    },
    {
      id: 2,
      username: 'bot_account',
      reason: 'ボットアカウント',
      blockType: 'like',
      addedDate: '2025-07-19'
    },
    {
      id: 3,
      username: 'inappropriate_content',
      reason: '不適切なコンテンツ',
      blockType: 'retweet',
      addedDate: '2025-07-18'
    }
  ]);

  const [newUser, setNewUser] = useState({
    username: '',
    reason: '',
    blockType: 'both'
  });

  const [searchTerm, setSearchTerm] = useState('');

  const addToBlacklist = () => {
    if (!newUser.username.trim()) return;

    const newEntry = {
      id: Date.now(),
      username: newUser.username.replace('@', ''),
      reason: newUser.reason || '理由未記載',
      blockType: newUser.blockType,
      addedDate: new Date().toISOString().split('T')[0]
    };

    setBlacklist(prev => [newEntry, ...prev]);
    setNewUser({ username: '', reason: '', blockType: 'both' });
  };

  const removeFromBlacklist = (id) => {
    setBlacklist(prev => prev.filter(item => item.id !== id));
  };

  const filteredBlacklist = blacklist.filter(item =>
    item.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.reason.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getBlockTypeLabel = (type) => {
    switch (type) {
      case 'like': return 'いいねのみ';
      case 'retweet': return 'リツイートのみ';
      case 'both': return '両方';
      default: return type;
    }
  };

  const getBlockTypeColor = (type) => {
    switch (type) {
      case 'like': return 'bg-red-100 text-red-600';
      case 'retweet': return 'bg-green-100 text-green-600';
      case 'both': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto"
      >
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            🚫 ブラックリスト管理
            <span className="text-lg font-normal text-gray-600">
              除外ユーザー・キーワード管理
            </span>
          </h1>
        </div>

        {/* 統計情報 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card bg-red-500 text-white">
            <div className="card-body text-center">
              <UserX size={32} className="mx-auto mb-2" />
              <p className="text-2xl font-bold">{blacklist.length}</p>
              <p className="text-red-100">ブロック中</p>
            </div>
          </div>
          <div className="card bg-orange-500 text-white">
            <div className="card-body text-center">
              <Shield size={32} className="mx-auto mb-2" />
              <p className="text-2xl font-bold">
                {blacklist.filter(item => item.blockType === 'like').length}
              </p>
              <p className="text-orange-100">いいねブロック</p>
            </div>
          </div>
          <div className="card bg-blue-500 text-white">
            <div className="card-body text-center">
              <Shield size={32} className="mx-auto mb-2" />
              <p className="text-2xl font-bold">
                {blacklist.filter(item => item.blockType === 'retweet').length}
              </p>
              <p className="text-blue-100">RTブロック</p>
            </div>
          </div>
          <div className="card bg-gray-500 text-white">
            <div className="card-body text-center">
              <AlertTriangle size={32} className="mx-auto mb-2" />
              <p className="text-2xl font-bold">
                {blacklist.filter(item => item.blockType === 'both').length}
              </p>
              <p className="text-gray-100">完全ブロック</p>
            </div>
          </div>
        </div>

        {/* 新規追加フォーム */}
        <div className="card mb-8">
          <div className="card-header">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Plus size={20} />
              新規ブラックリスト追加
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="form-label">ユーザー名</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="@username"
                  value={newUser.username}
                  onChange={(e) => setNewUser(prev => ({ ...prev, username: e.target.value }))}
                />
              </div>
              <div>
                <label className="form-label">ブロック種別</label>
                <select
                  className="form-select"
                  value={newUser.blockType}
                  onChange={(e) => setNewUser(prev => ({ ...prev, blockType: e.target.value }))}
                >
                  <option value="both">両方</option>
                  <option value="like">いいねのみ</option>
                  <option value="retweet">リツイートのみ</option>
                </select>
              </div>
              <div>
                <label className="form-label">理由</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="ブロック理由"
                  value={newUser.reason}
                  onChange={(e) => setNewUser(prev => ({ ...prev, reason: e.target.value }))}
                />
              </div>
              <div className="flex items-end">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={addToBlacklist}
                  className="w-full btn btn-error flex items-center justify-center gap-2"
                >
                  <Plus size={16} />
                  追加
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* 検索 */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                className="form-input pl-10"
                placeholder="ユーザー名または理由で検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* ブラックリスト一覧 */}
        <div className="space-y-4">
          {filteredBlacklist.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="card hover:shadow-lg transition-all"
            >
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                      <UserX size={24} className="text-red-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">@{item.username}</h3>
                      <p className="text-gray-600">{item.reason}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`badge ${getBlockTypeColor(item.blockType)}`}>
                          {getBlockTypeLabel(item.blockType)}
                        </span>
                        <span className="text-sm text-gray-500">
                          追加日: {item.addedDate}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => removeFromBlacklist(item.id)}
                    className="btn btn-outline btn-sm flex items-center gap-2 text-red-600 hover:bg-red-50"
                  >
                    <X size={14} />
                    削除
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredBlacklist.length === 0 && (
          <div className="text-center py-12">
            <UserX size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              ブラックリストは空です
            </h3>
            <p className="text-gray-500">
              {searchTerm ? '検索条件に一致するユーザーがいません' : '除外するユーザーを追加してください'}
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default BlacklistManager;