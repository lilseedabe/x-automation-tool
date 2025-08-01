"""
🚫 X自動反応ツール - ブラックリストサービス
望ましくないユーザーの管理とフィルタリング
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError

from ..database.models import UserBlacklist

logger = logging.getLogger(__name__)

class BlacklistService:
    """ブラックリストサービスクラス"""
    
    async def get_user_blacklist(self, user_id: int, session: AsyncSession) -> List[Dict[str, Any]]:
        """
        ユーザーのブラックリストを取得
        
        Args:
            user_id: ユーザーID
            session: データベースセッション
            
        Returns:
            ブラックリストユーザー一覧
        """
        try:
            query = select(UserBlacklist).where(
                UserBlacklist.user_id == user_id
            ).order_by(UserBlacklist.created_at.desc())
            
            result = await session.execute(query)
            blacklist_entries = result.scalars().all()
            
            blacklist_data = []
            for entry in blacklist_entries:
                blacklist_data.append({
                    "id": entry.id,
                    "username": entry.blocked_username,
                    "reason": entry.reason,
                    "created_at": entry.created_at,
                    "block_type": entry.block_type
                })
            
            logger.info(f"📋 ブラックリスト取得: user_id={user_id}, 件数={len(blacklist_data)}")
            return blacklist_data
            
        except Exception as e:
            logger.error(f"❌ ブラックリスト取得エラー: {str(e)}")
            return []
    
    async def add_to_blacklist(
        self, 
        user_id: int, 
        username: str, 
        reason: Optional[str], 
        session: AsyncSession
    ) -> bool:
        """
        ユーザーをブラックリストに追加
        
        Args:
            user_id: ユーザーID
            username: ブラックリスト対象ユーザー名
            reason: ブラックリスト理由
            session: データベースセッション
            
        Returns:
            追加成功フラグ
        """
        try:
            # 既存エントリをチェック
            existing_query = select(UserBlacklist).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.blocked_username == username.lower()
                )
            )
            
            result = await session.execute(existing_query)
            existing_entry = result.scalar_one_or_none()
            
            if existing_entry:
                # 既存エントリがある場合は再有効化
                existing_entry.is_active = True
                existing_entry.reason = reason or existing_entry.reason
                existing_entry.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"🔄 ブラックリスト再有効化: user_id={user_id}, username={username}")
            else:
                # 新規エントリを作成
                blacklist_entry = UserBlacklist(
                    user_id=user_id,
                    blocked_username=username.lower(),
                    block_type="user",
                    reason=reason or "手動追加",
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(blacklist_entry)
                logger.info(f"➕ ブラックリスト追加: user_id={user_id}, username={username}")
            
            await session.commit()
            return True
            
        except IntegrityError as e:
            await session.rollback()
            logger.warning(f"⚠️ ブラックリスト重複追加試行: user_id={user_id}, username={username}")
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ ブラックリスト追加エラー: {str(e)}")
            return False
    
    async def remove_from_blacklist(
        self, 
        user_id: int, 
        username: str, 
        session: AsyncSession
    ) -> bool:
        """
        ユーザーをブラックリストから削除
        
        Args:
            user_id: ユーザーID
            username: 削除対象ユーザー名
            session: データベースセッション
            
        Returns:
            削除成功フラグ
        """
        try:
            query = select(UserBlacklist).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.blacklisted_username == username.lower()
                )
            )
            
            result = await session.execute(query)
            blacklist_entry = result.scalar_one_or_none()
            
            if blacklist_entry:
                # 論理削除（is_activeをFalseに設定）
                blacklist_entry.is_active = False
                blacklist_entry.updated_at = datetime.now(timezone.utc)
                
                await session.commit()
                logger.info(f"🗑️ ブラックリスト削除: user_id={user_id}, username={username}")
                return True
            else:
                logger.warning(f"⚠️ ブラックリスト削除対象なし: user_id={user_id}, username={username}")
                return False
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ ブラックリスト削除エラー: {str(e)}")
            return False
    
    async def is_blacklisted(
        self, 
        user_id: int, 
        username: str, 
        session: AsyncSession
    ) -> bool:
        """
        ユーザーがブラックリストに登録されているかチェック
        
        Args:
            user_id: ユーザーID
            username: チェック対象ユーザー名
            session: データベースセッション
            
        Returns:
            ブラックリスト登録フラグ
        """
        try:
            query = select(UserBlacklist).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.blacklisted_username == username.lower(),
                    UserBlacklist.is_active == True
                )
            )
            
            result = await session.execute(query)
            blacklist_entry = result.scalar_one_or_none()
            
            is_blocked = blacklist_entry is not None
            
            if is_blocked:
                logger.debug(f"🚫 ブラックリストユーザー検出: {username}")
            
            return is_blocked
            
        except Exception as e:
            logger.error(f"❌ ブラックリストチェックエラー: {str(e)}")
            return False  # エラー時は安全側に倒してブロックしない
    
    async def filter_blacklisted_users(
        self, 
        user_id: int, 
        user_list: List[Dict[str, Any]], 
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        ユーザーリストからブラックリストユーザーを除外
        
        Args:
            user_id: ユーザーID
            user_list: フィルタリング対象ユーザーリスト
            session: データベースセッション
            
        Returns:
            フィルタリング済みユーザーリスト
        """
        try:
            if not user_list:
                return []
            
            # ブラックリストを一括取得
            usernames = [user.get("username", "").lower() for user in user_list if user.get("username")]
            
            if not usernames:
                return user_list
            
            query = select(UserBlacklist.blacklisted_username).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.blacklisted_username.in_(usernames),
                    UserBlacklist.is_active == True
                )
            )
            
            result = await session.execute(query)
            blacklisted_usernames = {row[0] for row in result.fetchall()}
            
            # フィルタリング実行
            filtered_users = []
            blocked_count = 0
            
            for user in user_list:
                username = user.get("username", "").lower()
                if username not in blacklisted_usernames:
                    filtered_users.append(user)
                else:
                    blocked_count += 1
            
            logger.info(f"🔍 ブラックリストフィルタリング: 元={len(user_list)}, 除外={blocked_count}, 結果={len(filtered_users)}")
            return filtered_users
            
        except Exception as e:
            logger.error(f"❌ ブラックリストフィルタリングエラー: {str(e)}")
            return user_list  # エラー時は元のリストを返す
    
    async def add_multiple_to_blacklist(
        self, 
        user_id: int, 
        usernames: List[str], 
        reason: str, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        複数ユーザーを一括でブラックリストに追加
        
        Args:
            user_id: ユーザーID
            usernames: ブラックリスト対象ユーザー名リスト
            reason: ブラックリスト理由
            session: データベースセッション
            
        Returns:
            追加結果統計
        """
        try:
            success_count = 0
            failed_count = 0
            skipped_count = 0
            
            for username in usernames:
                try:
                    # 既存チェック
                    existing_query = select(UserBlacklist).where(
                        and_(
                            UserBlacklist.user_id == user_id,
                            UserBlacklist.blacklisted_username == username.lower()
                        )
                    )
                    
                    result = await session.execute(existing_query)
                    existing_entry = result.scalar_one_or_none()
                    
                    if existing_entry and existing_entry.is_active:
                        skipped_count += 1
                        continue
                    
                    if existing_entry:
                        # 再有効化
                        existing_entry.is_active = True
                        existing_entry.reason = reason
                        existing_entry.updated_at = datetime.now(timezone.utc)
                    else:
                        # 新規追加
                        blacklist_entry = UserBlacklist(
                            user_id=user_id,
                            blacklisted_username=username.lower(),
                            reason=reason,
                            created_at=datetime.now(timezone.utc)
                        )
                        session.add(blacklist_entry)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ 個別ブラックリスト追加失敗: {username} - {str(e)}")
                    failed_count += 1
            
            await session.commit()
            
            logger.info(f"📊 一括ブラックリスト追加完了: 成功={success_count}, 失敗={failed_count}, スキップ={skipped_count}")
            
            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "total_processed": len(usernames)
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 一括ブラックリスト追加エラー: {str(e)}")
            return {
                "success_count": 0,
                "failed_count": len(usernames),
                "skipped_count": 0,
                "total_processed": len(usernames),
                "error": str(e)
            }
    
    async def get_blacklist_statistics(self, user_id: int, session: AsyncSession) -> Dict[str, Any]:
        """
        ブラックリスト統計情報を取得
        
        Args:
            user_id: ユーザーID
            session: データベースセッション
            
        Returns:
            統計情報
        """
        try:
            # 全エントリ数
            total_query = select(UserBlacklist).where(UserBlacklist.user_id == user_id)
            total_result = await session.execute(total_query)
            total_count = len(total_result.scalars().all())
            
            # アクティブエントリ数
            active_query = select(UserBlacklist).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.is_active == True
                )
            )
            active_result = await session.execute(active_query)
            active_count = len(active_result.scalars().all())
            
            # 最新エントリ
            latest_query = select(UserBlacklist).where(
                and_(
                    UserBlacklist.user_id == user_id,
                    UserBlacklist.is_active == True
                )
            ).order_by(UserBlacklist.created_at.desc()).limit(5)
            
            latest_result = await session.execute(latest_query)
            latest_entries = latest_result.scalars().all()
            
            recent_additions = []
            for entry in latest_entries:
                recent_additions.append({
                    "username": entry.blacklisted_username,
                    "reason": entry.reason,
                    "created_at": entry.created_at
                })
            
            statistics = {
                "total_count": total_count,
                "active_count": active_count,
                "inactive_count": total_count - active_count,
                "recent_additions": recent_additions,
                "last_updated": datetime.now(timezone.utc)
            }
            
            logger.info(f"📊 ブラックリスト統計: user_id={user_id}, アクティブ={active_count}")
            return statistics
            
        except Exception as e:
            logger.error(f"❌ ブラックリスト統計取得エラー: {str(e)}")
            return {
                "total_count": 0,
                "active_count": 0,
                "inactive_count": 0,
                "recent_additions": [],
                "error": str(e)
            }

# グローバルサービスインスタンス
blacklist_service = BlacklistService()