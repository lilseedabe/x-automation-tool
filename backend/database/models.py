"""
🗄️ X自動反応ツール - データベースモデル定義
SQLAlchemy + Pydantic 運営者ブラインド設計
"""

from datetime import datetime, timezone, time
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import enum

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, TIMESTAMP, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint,
    LargeBinary, ARRAY, JSON, Time, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, ConfigDict, validator
from pydantic import EmailStr

from .connection import Base

# ===================================================================
# 🏗️ SQLAlchemy Database Models
# ===================================================================

class User(Base):
    """ユーザーアカウントテーブル"""
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # ステータス
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # メタデータ
    registration_ip: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6対応（INET → String）
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # 設定
    timezone: Mapped[str] = mapped_column(String(50), default='Asia/Tokyo')
    language: Mapped[str] = mapped_column(String(10), default='ja')
    
    # リレーション
    api_keys: Mapped[List["UserAPIKey"]] = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    automation_settings: Mapped[Optional["AutomationSettings"]] = relationship("AutomationSettings", back_populates="user", uselist=False)
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    action_queue: Mapped[List["ActionQueue"]] = relationship("ActionQueue", back_populates="user")
    blacklist: Mapped[List["UserBlacklist"]] = relationship("UserBlacklist", back_populates="user")
    activity_logs: Mapped[List["ActivityLog"]] = relationship("ActivityLog", back_populates="user")
    rate_limits: Mapped[List["RateLimit"]] = relationship("RateLimit", back_populates="user")  # 追加
    automation_actions: Mapped[List["AutomationAction"]] = relationship("AutomationAction", back_populates="user")  # 追加
    
    # 制約
    __table_args__ = (
        CheckConstraint("length(username) >= 3", name="username_length_check"),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="email_format_check"),
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_is_active", "is_active"),
    )

class UserAPIKey(Base):
    """X APIキー暗号化保存テーブル（運営者ブラインド）"""
    __tablename__ = "user_api_keys"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 暗号化されたAPIキー（運営者は復号不可）
    encrypted_api_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_api_secret: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_access_token: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_access_token_secret: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    # 暗号化情報
    key_salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encryption_algorithm: Mapped[str] = mapped_column(String(50), default='AES-256-GCM')
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # X API情報
    x_username: Mapped[Optional[str]] = mapped_column(String(50))
    x_user_id: Mapped[Optional[str]] = mapped_column(String(50))
    api_permissions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # ステータス
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_validation: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # 使用統計
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    
    # 制約
    __table_args__ = (
        UniqueConstraint("user_id", name="unique_user_api_key"),
        Index("idx_user_api_keys_user_id", "user_id"),
        Index("idx_user_api_keys_is_active", "is_active"),
        Index("idx_user_api_keys_last_used", "last_used"),
    )

class AutomationMode(str, enum.Enum):
    """自動化モード"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

class AutomationSettings(Base):
    """ユーザー自動化設定テーブル"""
    __tablename__ = "automation_settings"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 基本設定
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    automation_mode: Mapped[AutomationMode] = mapped_column(String(20), default=AutomationMode.CONSERVATIVE)
    
    # いいね設定
    auto_like_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    like_daily_limit: Mapped[int] = mapped_column(Integer, default=100)
    like_hourly_limit: Mapped[int] = mapped_column(Integer, default=20)
    like_min_interval_minutes: Mapped[int] = mapped_column(Integer, default=3)
    like_max_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)
    
    # リポスト設定
    auto_repost_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    repost_daily_limit: Mapped[int] = mapped_column(Integer, default=20)
    repost_hourly_limit: Mapped[int] = mapped_column(Integer, default=5)
    repost_min_interval_minutes: Mapped[int] = mapped_column(Integer, default=10)
    repost_max_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    
    # AI分析設定
    ai_analysis_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_engagement_score: Mapped[int] = mapped_column(Integer, default=50)
    target_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    exclude_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # 安全設定
    enable_blacklist: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_rate_limiting: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_human_like_timing: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # スケジュール設定
    active_hours_start: Mapped[time] = mapped_column(Time, default=time(9, 0))
    active_hours_end: Mapped[time] = mapped_column(Time, default=time(22, 0))
    active_days: Mapped[List[int]] = mapped_column(ARRAY(Integer), default=[1,2,3,4,5,6,7])
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="automation_settings")
    
    # 制約
    __table_args__ = (
        UniqueConstraint("user_id", name="unique_user_automation"),
        Index("idx_automation_settings_user_id", "user_id"),
        Index("idx_automation_settings_is_enabled", "is_enabled"),
    )

class ActionType(str, enum.Enum):
    """アクション種別"""
    LIKE = "like"
    REPOST = "repost"
    REPLY = "reply"

class ActionStatus(str, enum.Enum):
    """アクション状態"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ActionQueue(Base):
    """アクションキューテーブル"""
    __tablename__ = "action_queue"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # アクション詳細
    action_type: Mapped[ActionType] = mapped_column(String(20), nullable=False)
    target_post_id: Mapped[str] = mapped_column(String(50), nullable=False)
    target_user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    target_username: Mapped[Optional[str]] = mapped_column(String(50))
    
    # スケジューリング
    scheduled_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    executed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # ステータス
    status: Mapped[ActionStatus] = mapped_column(String(20), default=ActionStatus.PENDING)
    
    # 結果
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # AI分析結果
    ai_score: Mapped[Optional[int]] = mapped_column(Integer)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="action_queue")
    
    # 制約
    __table_args__ = (
        Index("idx_action_queue_user_id", "user_id"),
        Index("idx_action_queue_status", "status"),
        Index("idx_action_queue_scheduled_at", "scheduled_at"),
        Index("idx_action_queue_action_type", "action_type"),
    )

class BlockType(str, enum.Enum):
    """ブロック種別"""
    USER = "user"
    KEYWORD = "keyword"
    DOMAIN = "domain"

class UserBlacklist(Base):
    """ユーザーブラックリストテーブル"""
    __tablename__ = "user_blacklist"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # ブラックリスト対象
    blocked_user_id: Mapped[Optional[str]] = mapped_column(String(50))
    blocked_username: Mapped[Optional[str]] = mapped_column(String(50))
    blocked_keyword: Mapped[Optional[str]] = mapped_column(String(255))
    
    # 種別と理由
    block_type: Mapped[BlockType] = mapped_column(String(20), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="blacklist")
    
    # 制約
    __table_args__ = (
        Index("idx_user_blacklist_user_id", "user_id"),
        Index("idx_user_blacklist_block_type", "block_type"),
        Index("idx_user_blacklist_blocked_user_id", "blocked_user_id"),
    )

class ActivityLog(Base):
    """活動ログテーブル"""
    __tablename__ = "activity_logs"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # アクション詳細
    action_type: Mapped[ActionType] = mapped_column(String(20), nullable=False)
    target_post_id: Mapped[Optional[str]] = mapped_column(String(50))
    target_user_id: Mapped[Optional[str]] = mapped_column(String(50))
    target_username: Mapped[Optional[str]] = mapped_column(String(50))
    
    # 結果
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # タイミング
    executed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # 分析データ
    ai_score: Mapped[Optional[int]] = mapped_column(Integer)
    engagement_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="activity_logs")
    
    # 制約
    __table_args__ = (
        Index("idx_activity_logs_user_id", "user_id"),
        Index("idx_activity_logs_executed_at", "executed_at"),
        Index("idx_activity_logs_action_type", "action_type"),
        Index("idx_activity_logs_success", "success"),
    )

class AutomationAction(Base):
    """自動化アクションログテーブル（dashboard_router用）"""
    __tablename__ = "automation_actions"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # アクション詳細
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_username: Mapped[Optional[str]] = mapped_column(String(50))
    target_tweet_id: Mapped[Optional[str]] = mapped_column(String(50))
    content_preview: Mapped[Optional[str]] = mapped_column(Text)
    
    # ステータス
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    # カウント
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    retweet_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # エラー情報
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション（追加）
    user: Mapped["User"] = relationship("User", back_populates="automation_actions")
    
    # 制約
    __table_args__ = (
        Index("idx_automation_actions_user_id", "user_id"),
        Index("idx_automation_actions_status", "status"),
        Index("idx_automation_actions_created_at", "created_at"),
        Index("idx_automation_actions_action_type", "action_type"),
    )

# ===================================================================
# お気に入りユーザー・処理済みツイートテーブル追加
# ===================================================================

class FavoriteUser(Base):
    """お気に入りユーザーテーブル"""
    __tablename__ = "favorite_users"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    target_user_id = Column(String(20), nullable=False)
    username = Column(String(15), nullable=False)
    auto_like = Column(Boolean, default=True)
    auto_repost = Column(Boolean, default=False)
    keywords_filter = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_processed = Column(TIMESTAMP(timezone=True))
    is_active = Column(Boolean, default=True)
    __table_args__ = (
        Index('idx_user_target', 'user_id', 'target_user_id'),
        Index('idx_username_lookup', 'username'),
    )

class ProcessedTweet(Base):
    """処理済みツイートテーブル（重複防止用）"""
    __tablename__ = "processed_tweets"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    tweet_id = Column(String(20), nullable=False)
    action_type = Column(String(10), nullable=False)
    processed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ai_confidence = Column(Integer)
    __table_args__ = (
        Index('idx_user_tweet_action', 'user_id', 'tweet_id', 'action_type'),
    )

# ===================================================================
# 🚦 RateLimit Model (新規追加)
# ===================================================================

class RateLimit(Base):
    """レート制限管理テーブル"""
    __tablename__ = "rate_limits"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # エンドポイント情報
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # レート制限設定
    requests_made: Mapped[int] = mapped_column(Integer, default=0)
    requests_limit: Mapped[int] = mapped_column(Integer, default=100)
    
    # ウィンドウ管理
    window_start: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    window_duration: Mapped[int] = mapped_column(Integer, default=3600)  # 秒単位（デフォルト1時間）
    reset_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="rate_limits")
    
    # 制約
    __table_args__ = (
        UniqueConstraint("user_id", "endpoint", name="unique_user_endpoint_rate_limit"),
        Index("idx_rate_limits_user_id", "user_id"),
        Index("idx_rate_limits_endpoint", "endpoint"),
        Index("idx_rate_limits_reset_at", "reset_at"),
        Index("idx_rate_limits_user_endpoint", "user_id", "endpoint"),
    )

# ===================================================================
# 📊 Analytics Models (新規追加)
# ===================================================================

class AutomationAnalytics(Base):
    """自動化分析データテーブル"""
    __tablename__ = "automation_analytics"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 分析期間
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    
    # アクション統計
    total_actions: Mapped[int] = mapped_column(Integer, default=0)
    successful_actions: Mapped[int] = mapped_column(Integer, default=0)
    failed_actions: Mapped[int] = mapped_column(Integer, default=0)
    
    # アクション別統計
    likes_given: Mapped[int] = mapped_column(Integer, default=0)
    retweets_made: Mapped[int] = mapped_column(Integer, default=0)
    replies_sent: Mapped[int] = mapped_column(Integer, default=0)
    follows_made: Mapped[int] = mapped_column(Integer, default=0)
    
    # パフォーマンス指標
    engagement_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5,2), default=0.00)
    success_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5,2), default=0.00)
    average_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 制約
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="unique_user_date_analytics"),
        Index("idx_automation_analytics_user_id", "user_id"),
        Index("idx_automation_analytics_date", "date"),
        Index("idx_automation_analytics_user_date", "user_id", "date"),
    )

class SystemSettings(Base):
    """システム設定テーブル"""
    __tablename__ = "system_settings"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # メタデータ
    value_type: Mapped[str] = mapped_column(String(20), default='string')  # string, int, float, bool, json
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 制約
    __table_args__ = (
        Index("idx_system_settings_key", "key"),
        Index("idx_system_settings_is_public", "is_public"),
    )

class UserSession(Base):
    """ユーザーセッションテーブル"""
    __tablename__ = "user_sessions"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # セッション情報
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    
    # APIキー復号状態（運営者ブラインド維持）
    api_keys_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    api_cache_expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # 有効期限
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    refresh_expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # クライアント情報
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6対応（INET → String）
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # ステータス
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_accessed: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    
    # 制約
    __table_args__ = (
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_session_token", "session_token"),
        Index("idx_user_sessions_expires_at", "expires_at"),
        Index("idx_user_sessions_api_cache_expires", "api_cache_expires_at"),
    )

# ===================================================================
# 📋 Pydantic Response Models
# ===================================================================

class UserBase(BaseModel):
    """ユーザー基本情報"""
    model_config = ConfigDict(from_attributes=True)
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    timezone: str = "Asia/Tokyo"
    language: str = "ja"

class UserCreate(UserBase):
    """ユーザー作成"""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """ユーザー更新"""
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

class UserResponse(UserBase):
    """ユーザーレスポンス"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class APIKeyCreate(BaseModel):
    """APIキー作成"""
    api_key: str = Field(..., description="X API Key")
    api_secret: str = Field(..., description="X API Secret")
    access_token: str = Field(..., description="X Access Token")
    access_token_secret: str = Field(..., description="X Access Token Secret")
    user_password: str = Field(..., description="暗号化用ユーザーパスワード")

class APIKeyResponse(BaseModel):
    """APIキーレスポンス（暗号化済み）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    x_username: Optional[str] = None
    x_user_id: Optional[str] = None
    api_permissions: Optional[List[str]] = None
    is_active: bool
    is_valid: bool
    created_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int
    error_count: int

class AutomationSettingsCreate(BaseModel):
    """自動化設定作成"""
    automation_mode: AutomationMode = AutomationMode.CONSERVATIVE
    auto_like_enabled: bool = True
    like_daily_limit: int = Field(default=100, ge=1, le=1000)
    like_hourly_limit: int = Field(default=20, ge=1, le=100)
    auto_repost_enabled: bool = False
    repost_daily_limit: int = Field(default=20, ge=1, le=100)
    ai_analysis_enabled: bool = True
    minimum_engagement_score: int = Field(default=50, ge=0, le=100)
    target_keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None

class AutomationSettingsResponse(BaseModel):
    """自動化設定レスポンス"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_enabled: bool
    automation_mode: AutomationMode
    auto_like_enabled: bool
    like_daily_limit: int
    like_hourly_limit: int
    auto_repost_enabled: bool
    repost_daily_limit: int
    repost_hourly_limit: int
    ai_analysis_enabled: bool
    minimum_engagement_score: int
    target_keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class ActionQueueResponse(BaseModel):
    """アクションキューレスポンス"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    action_type: ActionType
    target_post_id: str
    target_user_id: str
    target_username: Optional[str] = None
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    status: ActionStatus
    ai_score: Optional[int] = None
    created_at: datetime

class ActivityLogResponse(BaseModel):
    """活動ログレスポンス"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    action_type: ActionType
    target_post_id: Optional[str] = None
    target_user_id: Optional[str] = None
    target_username: Optional[str] = None
    success: bool
    executed_at: datetime
    response_time_ms: Optional[int] = None
    ai_score: Optional[int] = None

class UserStatsResponse(BaseModel):
    """ユーザー統計レスポンス"""
    total_actions: int = 0
    successful_actions: int = 0
    total_likes: int = 0
    total_reposts: int = 0
    success_rate_percent: float = 0.0
    last_action: Optional[datetime] = None

# ===================================================================
# 🚦 Rate Limit Pydantic Models (新規追加)
# ===================================================================

class RateLimitInfo(BaseModel):
    """レート制限情報"""
    model_config = ConfigDict(from_attributes=True)
    
    endpoint: str = Field(..., description="APIエンドポイント")
    requests_made: int = Field(..., description="使用済みリクエスト数")
    requests_limit: int = Field(..., description="制限数")
    remaining: int = Field(..., description="残りリクエスト数")
    reset_at: Optional[datetime] = Field(None, description="リセット時刻")
    window_duration: int = Field(..., description="ウィンドウ期間（秒）")
    percentage_used: float = Field(..., description="使用率（%）")

class RateLimitSummary(BaseModel):
    """レート制限サマリー"""
    user_id: str = Field(..., description="ユーザーID")
    total_endpoints: int = Field(..., description="監視対象エンドポイント数")
    limits: List[RateLimitInfo] = Field(..., description="レート制限詳細")
    overall_status: str = Field(..., description="全体ステータス")
    next_reset: Optional[datetime] = Field(None, description="次のリセット時刻")

class RateLimitUpdateRequest(BaseModel):
    """レート制限更新リクエスト"""
    endpoint: str = Field(..., description="APIエンドポイント")
    requests_limit: int = Field(..., ge=1, description="新しい制限数")

# ===================================================================
# 📊 Analytics Pydantic Models (新規追加)
# ===================================================================

class AutomationAnalyticsResponse(BaseModel):
    """自動化分析レスポンス"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    date: datetime
    total_actions: int
    successful_actions: int
    failed_actions: int
    likes_given: int
    retweets_made: int
    replies_sent: int
    follows_made: int
    engagement_rate: Optional[float] = None
    success_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime
