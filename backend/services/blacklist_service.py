"""
ブラックリスト管理サービス

このモジュールは以下の機能を提供します：
- ユーザーブラックリスト管理
- キーワードフィルタリング
- 自動フィルタリング
- ブラックリスト分析
"""

import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
import re

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# データモデル
# =============================================================================

class BlacklistEntry:
    """ブラックリストエントリ"""
    
    def __init__(self, entry_type: str, value: str, reason: str = "", added_at: datetime = None):
        self.entry_type = entry_type  # "user", "keyword", "domain"
        self.value = value
        self.reason = reason
        self.added_at = added_at or datetime.now()
        self.active = True

class FilterResult:
    """フィルタ結果"""
    
    def __init__(self, is_filtered: bool, reasons: List[str] = None, matched_entries: List[str] = None):
        self.is_filtered = is_filtered
        self.reasons = reasons or []
        self.matched_entries = matched_entries or []

# =============================================================================
# ブラックリスト管理サービスクラス
# =============================================================================

class BlacklistService:
    """
    ブラックリスト管理サービス
    
    ユーザー、キーワード、ドメインのブラックリスト管理を行います。
    """
    
    def __init__(self, data_path: str = "./data"):
        """
        初期化
        
        Args:
            data_path (str): データファイルの保存パス
        """
        self.data_path = Path(data_path)
        
        # データディレクトリ作成
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # デフォルトブラックリストパターン
        self.default_spam_keywords = [
            "スパム", "詐欺", "怪しい", "偽物", "フォロバ100", 
            "相互フォロー", "フォロー返し", "RT拡散", "宣伝",
            "副業", "稼げる", "簡単", "クリック", "URL"
        ]
        
        self.default_inappropriate_keywords = [
            "暴力", "差別", "ヘイト", "誹謗中傷", "個人情報",
            "プライベート", "秘密", "内緒"
        ]
        
        logger.info("BlacklistService初期化完了")
    
    def _get_user_blacklist_file(self, user_id: str) -> Path:
        """ユーザーのブラックリストファイルパスを取得"""
        user_dir = self.data_path / "users" / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "blacklist.json"
    
    def _load_user_blacklist(self, user_id: str) -> Dict[str, Any]:
        """ユーザーのブラックリストを読み込み"""
        blacklist_file = self._get_user_blacklist_file(user_id)
        
        if not blacklist_file.exists():
            return {
                "users": {},
                "keywords": {},
                "domains": {},
                "patterns": {},
                "settings": {
                    "auto_filter": True,
                    "strict_mode": False,
                    "custom_rules": []
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
        
        try:
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"ブラックリスト読み込みエラー: {e}")
            return {"users": {}, "keywords": {}, "domains": {}, "patterns": {}, "settings": {}}
    
    def _save_user_blacklist(self, user_id: str, data: Dict[str, Any]):
        """ユーザーのブラックリストを保存"""
        blacklist_file = self._get_user_blacklist_file(user_id)
        
        try:
            data["metadata"]["updated_at"] = datetime.now().isoformat()
            
            with open(blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"ブラックリスト保存エラー: {e}")
            raise
    
    def add_user_to_blacklist(self, user_id: str, target_user: str, reason: str = "") -> bool:
        """
        ユーザーをブラックリストに追加
        
        Args:
            user_id (str): 操作ユーザーID
            target_user (str): ブラックリスト対象ユーザー
            reason (str): 理由
            
        Returns:
            bool: 追加成功フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            entry = {
                "value": target_user,
                "reason": reason,
                "added_at": datetime.now().isoformat(),
                "active": True
            }
            
            data["users"][target_user] = entry
            self._save_user_blacklist(user_id, data)
            
            logger.info(f"ユーザーブラックリスト追加: {user_id} -> {target_user}")
            return True
            
        except Exception as e:
            logger.error(f"ユーザーブラックリスト追加エラー: {e}")
            return False
    
    def add_keyword_to_blacklist(self, user_id: str, keyword: str, reason: str = "") -> bool:
        """
        キーワードをブラックリストに追加
        
        Args:
            user_id (str): 操作ユーザーID
            keyword (str): ブラックリスト対象キーワード
            reason (str): 理由
            
        Returns:
            bool: 追加成功フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            entry = {
                "value": keyword,
                "reason": reason,
                "added_at": datetime.now().isoformat(),
                "active": True,
                "case_sensitive": False
            }
            
            data["keywords"][keyword.lower()] = entry
            self._save_user_blacklist(user_id, data)
            
            logger.info(f"キーワードブラックリスト追加: {user_id} -> {keyword}")
            return True
            
        except Exception as e:
            logger.error(f"キーワードブラックリスト追加エラー: {e}")
            return False
    
    def add_domain_to_blacklist(self, user_id: str, domain: str, reason: str = "") -> bool:
        """
        ドメインをブラックリストに追加
        
        Args:
            user_id (str): 操作ユーザーID
            domain (str): ブラックリスト対象ドメイン
            reason (str): 理由
            
        Returns:
            bool: 追加成功フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            entry = {
                "value": domain,
                "reason": reason,
                "added_at": datetime.now().isoformat(),
                "active": True
            }
            
            data["domains"][domain.lower()] = entry
            self._save_user_blacklist(user_id, data)
            
            logger.info(f"ドメインブラックリスト追加: {user_id} -> {domain}")
            return True
            
        except Exception as e:
            logger.error(f"ドメインブラックリスト追加エラー: {e}")
            return False
    
    def remove_from_blacklist(self, user_id: str, entry_type: str, value: str) -> bool:
        """
        ブラックリストから削除
        
        Args:
            user_id (str): 操作ユーザーID
            entry_type (str): エントリタイプ ("users", "keywords", "domains")
            value (str): 削除対象値
            
        Returns:
            bool: 削除成功フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            if entry_type in data and value in data[entry_type]:
                del data[entry_type][value]
                self._save_user_blacklist(user_id, data)
                
                logger.info(f"ブラックリスト削除: {user_id} -> {entry_type}:{value}")
                return True
            else:
                logger.warning(f"削除対象が見つかりません: {entry_type}:{value}")
                return False
                
        except Exception as e:
            logger.error(f"ブラックリスト削除エラー: {e}")
            return False
    
    def is_user_blacklisted(self, user_id: str, target_user: str) -> bool:
        """
        ユーザーがブラックリストに登録されているかチェック
        
        Args:
            user_id (str): 操作ユーザーID
            target_user (str): チェック対象ユーザー
            
        Returns:
            bool: ブラックリスト登録フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            return target_user in data.get("users", {})
        except Exception as e:
            logger.error(f"ユーザーブラックリストチェックエラー: {e}")
            return False
    
    def filter_content(self, user_id: str, content: str, author: str = "") -> FilterResult:
        """
        コンテンツフィルタリング
        
        Args:
            user_id (str): 操作ユーザーID
            content (str): フィルタ対象コンテンツ
            author (str): 投稿者
            
        Returns:
            FilterResult: フィルタ結果
        """
        try:
            data = self._load_user_blacklist(user_id)
            reasons = []
            matched_entries = []
            
            # ユーザーチェック
            if author and author in data.get("users", {}):
                reasons.append(f"ブラックリストユーザー: {author}")
                matched_entries.append(f"user:{author}")
            
            # キーワードチェック
            content_lower = content.lower()
            for keyword, entry in data.get("keywords", {}).items():
                if entry.get("active", True) and keyword in content_lower:
                    reasons.append(f"ブラックリストキーワード: {keyword}")
                    matched_entries.append(f"keyword:{keyword}")
            
            # ドメインチェック
            url_pattern = re.compile(r'https?://([^\s/]+)')
            urls = url_pattern.findall(content)
            
            for url in urls:
                domain = url.lower()
                for blacklisted_domain, entry in data.get("domains", {}).items():
                    if entry.get("active", True) and blacklisted_domain in domain:
                        reasons.append(f"ブラックリストドメイン: {blacklisted_domain}")
                        matched_entries.append(f"domain:{blacklisted_domain}")
            
            # デフォルトスパムキーワードチェック（設定に応じて）
            settings = data.get("settings", {})
            if settings.get("auto_filter", True):
                for spam_keyword in self.default_spam_keywords:
                    if spam_keyword in content_lower:
                        reasons.append(f"スパム判定キーワード: {spam_keyword}")
                        matched_entries.append(f"spam:{spam_keyword}")
            
            # 不適切コンテンツチェック（厳格モード）
            if settings.get("strict_mode", False):
                for inappropriate_keyword in self.default_inappropriate_keywords:
                    if inappropriate_keyword in content_lower:
                        reasons.append(f"不適切コンテンツ: {inappropriate_keyword}")
                        matched_entries.append(f"inappropriate:{inappropriate_keyword}")
            
            is_filtered = len(reasons) > 0
            
            if is_filtered:
                logger.info(f"コンテンツフィルタリング実行: {len(reasons)}件の問題検出")
            
            return FilterResult(is_filtered, reasons, matched_entries)
            
        except Exception as e:
            logger.error(f"コンテンツフィルタリングエラー: {e}")
            return FilterResult(False, [f"フィルタリングエラー: {str(e)}"])
    
    def get_blacklist_summary(self, user_id: str) -> Dict[str, Any]:
        """
        ブラックリスト要約取得
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            Dict[str, Any]: ブラックリスト要約
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            # アクティブなエントリをカウント
            active_users = sum(1 for entry in data.get("users", {}).values() if entry.get("active", True))
            active_keywords = sum(1 for entry in data.get("keywords", {}).values() if entry.get("active", True))
            active_domains = sum(1 for entry in data.get("domains", {}).values() if entry.get("active", True))
            
            # 最近追加されたエントリ
            recent_entries = []
            for entry_type in ["users", "keywords", "domains"]:
                for value, entry in data.get(entry_type, {}).items():
                    if entry.get("active", True):
                        recent_entries.append({
                            "type": entry_type,
                            "value": value,
                            "added_at": entry.get("added_at"),
                            "reason": entry.get("reason", "")
                        })
            
            # 追加日時でソート
            recent_entries.sort(key=lambda x: x["added_at"], reverse=True)
            
            summary = {
                "total_entries": active_users + active_keywords + active_domains,
                "breakdown": {
                    "users": active_users,
                    "keywords": active_keywords,
                    "domains": active_domains
                },
                "settings": data.get("settings", {}),
                "recent_entries": recent_entries[:10],  # 最新10件
                "last_updated": data.get("metadata", {}).get("updated_at"),
                "created_at": data.get("metadata", {}).get("created_at")
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"ブラックリスト要約取得エラー: {e}")
            return {"error": f"要約取得エラー: {str(e)}"}
    
    def update_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        ブラックリスト設定更新
        
        Args:
            user_id (str): ユーザーID
            settings (Dict[str, Any]): 更新設定
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            current_settings = data.get("settings", {})
            current_settings.update(settings)
            data["settings"] = current_settings
            
            self._save_user_blacklist(user_id, data)
            
            logger.info(f"ブラックリスト設定更新: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"ブラックリスト設定更新エラー: {e}")
            return False
    
    def export_blacklist(self, user_id: str) -> Dict[str, Any]:
        """
        ブラックリストエクスポート
        
        Args:
            user_id (str): ユーザーID
            
        Returns:
            Dict[str, Any]: エクスポートデータ
        """
        try:
            data = self._load_user_blacklist(user_id)
            
            # エクスポート用データ整形
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "blacklist_data": data,
                "format_version": "1.0"
            }
            
            logger.info(f"ブラックリストエクスポート: {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"ブラックリストエクスポートエラー: {e}")
            return {"error": f"エクスポートエラー: {str(e)}"}
    
    def import_blacklist(self, user_id: str, import_data: Dict[str, Any], merge: bool = True) -> bool:
        """
        ブラックリストインポート
        
        Args:
            user_id (str): ユーザーID
            import_data (Dict[str, Any]): インポートデータ
            merge (bool): マージするかどうか
            
        Returns:
            bool: インポート成功フラグ
        """
        try:
            if merge:
                current_data = self._load_user_blacklist(user_id)
            else:
                current_data = {"users": {}, "keywords": {}, "domains": {}, "patterns": {}, "settings": {}}
            
            # インポートデータをマージ
            imported_blacklist = import_data.get("blacklist_data", {})
            
            for entry_type in ["users", "keywords", "domains"]:
                if entry_type in imported_blacklist:
                    current_data.setdefault(entry_type, {}).update(imported_blacklist[entry_type])
            
            # 設定もマージ
            if "settings" in imported_blacklist:
                current_data.setdefault("settings", {}).update(imported_blacklist["settings"])
            
            self._save_user_blacklist(user_id, current_data)
            
            logger.info(f"ブラックリストインポート完了: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"ブラックリストインポートエラー: {e}")
            return False


# =============================================================================
# ユーティリティ関数
# =============================================================================

def create_default_blacklist(user_id: str, blacklist_service: BlacklistService) -> bool:
    """
    デフォルトブラックリストを作成
    
    Args:
        user_id (str): ユーザーID
        blacklist_service (BlacklistService): ブラックリストサービス
        
    Returns:
        bool: 作成成功フラグ
    """
    try:
        # デフォルトスパムキーワードを追加
        for keyword in blacklist_service.default_spam_keywords[:5]:  # 最初の5個のみ
            blacklist_service.add_keyword_to_blacklist(
                user_id, keyword, "デフォルトスパムキーワード"
            )
        
        # デフォルト設定
        default_settings = {
            "auto_filter": True,
            "strict_mode": False,
            "custom_rules": []
        }
        
        blacklist_service.update_settings(user_id, default_settings)
        
        logger.info(f"デフォルトブラックリスト作成完了: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"デフォルトブラックリスト作成エラー: {e}")
        return False


# =============================================================================
# テスト・デバッグ用
# =============================================================================

if __name__ == "__main__":
    # 基本テスト
    service = BlacklistService("./test_data")
    test_user_id = "test_user_123"
    
    # ユーザー追加テスト
    success = service.add_user_to_blacklist(test_user_id, "spam_user", "スパムアカウント")
    print(f"ユーザー追加: {success}")
    
    # キーワード追加テスト
    success = service.add_keyword_to_blacklist(test_user_id, "スパム", "スパムキーワード")
    print(f"キーワード追加: {success}")
    
    # フィルタリングテスト
    test_content = "これはスパムです。フォロバ100%！"
    filter_result = service.filter_content(test_user_id, test_content, "spam_user")
    
    print(f"フィルタリング結果: {filter_result.is_filtered}")
    print(f"理由: {filter_result.reasons}")
    
    # 要約取得テスト
    summary = service.get_blacklist_summary(test_user_id)
    print(f"ブラックリスト要約: {summary}")