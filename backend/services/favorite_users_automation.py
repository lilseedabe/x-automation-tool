from backend.database.session import get_db
from backend.database import models
from backend.ai.post_analyzer import analyze_post
from sqlalchemy.orm import Session
from datetime import datetime
import time

def process_favorite_users_actions(user_id):
    """
    お気に入りユーザーの新着ツイートに自動いいね・リポスト（AI判定＋人間らしいタイミング）
    """
    db: Session = next(get_db())
    favorite_users = db.query(models.FavoriteUser).filter_by(owner_id=user_id).all()
    results = []
    for fav_user in favorite_users:
        # 最新ツイート取得（仮: DB or API呼び出し）
        recent_tweet = get_latest_tweet_for_user(fav_user.username)
        if not recent_tweet:
            continue
        # AI分析
        ai_result = analyze_post(recent_tweet["text"])
        action_type = "like" if ai_result["score"] > 0.7 else "retweet"
        # 人間らしい遅延
        time.sleep(ai_result.get("recommended_delay", 2))
        # アクション実行（仮: API呼び出し）
        action_success = execute_action(user_id, fav_user.username, recent_tweet["id"], action_type)
        # processed_tweetsテーブルに記録
        processed = models.ProcessedTweet(
            user_id=user_id,
            tweet_id=recent_tweet["id"],
            action_type=action_type,
            processed_at=datetime.utcnow()
        )
        db.add(processed)
        db.commit()
        results.append({
            "username": fav_user.username,
            "tweet_id": recent_tweet["id"],
            "action_type": action_type,
            "success": action_success
        })
    return results

def get_latest_tweet_for_user(username):
    # TODO: X API呼び出しで最新ツイート取得
    # ここではダミーデータ
    return {"id": "1234567890", "text": "最新ツイート内容"}

def execute_action(user_id, username, tweet_id, action_type):
    # TODO: X API呼び出しでいいね・リポスト実行
    # ここでは常に成功
    return True