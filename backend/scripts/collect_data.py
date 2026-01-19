"""
GitHub Actions用データ収集スクリプト
YouTube API と Google News からデータを収集する

使い方:
    cd backend
    YOUTUBE_API_KEY=xxx python scripts/collect_data.py
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Channel, ChannelStats, News
from app.services.youtube_service import YouTubeService
from app.services.news_service import NewsService


async def collect_youtube_stats(db, youtube: YouTubeService, channel) -> bool:
    """YouTube統計を収集"""
    try:
        info = await youtube.get_channel_info(channel.channel_id)
        if info:
            channel.name = info["name"]
            channel.description = info.get("description")
            channel.thumbnail_url = info.get("thumbnail_url")
            channel.updated_at = datetime.utcnow()

            stats = ChannelStats(
                channel_id=channel.id,
                subscriber_count=info["subscriber_count"],
                view_count=info.get("view_count", 0),
                video_count=info.get("video_count", 0),
            )
            db.add(stats)
            return True
    except Exception as e:
        print(f"  YouTube error: {e}")
    return False


async def collect_news(db, news_service: NewsService, channel) -> int:
    """ニュースを収集"""
    added = 0
    try:
        news_items = await news_service.fetch_news(channel.name, max_results=10)
        for item in news_items:
            existing = db.query(News).filter(
                News.channel_id == channel.id,
                News.url == item["url"]
            ).first()
            if not existing:
                news = News(
                    channel_id=channel.id,
                    title=item["title"],
                    url=item["url"],
                    source=item.get("source"),
                    thumbnail_url=item.get("thumbnail_url"),
                    category=item.get("category", "other"),
                    published_at=item.get("published_at"),
                )
                db.add(news)
                added += 1
    except Exception as e:
        print(f"  News error: {e}")
    return added


async def main():
    print("=" * 50)
    print("データ収集開始")
    print(f"時刻: {datetime.now().isoformat()}")
    print("=" * 50)

    db = SessionLocal()
    youtube = YouTubeService()
    news_service = NewsService()

    try:
        channels = db.query(Channel).all()
        print(f"\n対象チャンネル数: {len(channels)}")

        if not channels:
            print("登録されているチャンネルがありません")
            return

        youtube_success = 0
        news_added = 0

        for i, channel in enumerate(channels, 1):
            print(f"\n[{i}/{len(channels)}] {channel.name}")

            # YouTube統計
            if await collect_youtube_stats(db, youtube, channel):
                youtube_success += 1
                print("  ✓ YouTube stats collected")

            # ニュース
            count = await collect_news(db, news_service, channel)
            if count > 0:
                news_added += count
                print(f"  ✓ {count} news articles added")

            # API制限対策
            if i % 10 == 0:
                await asyncio.sleep(1)

        db.commit()

        print("\n" + "=" * 50)
        print("収集完了")
        print(f"  YouTube統計: {youtube_success}/{len(channels)} チャンネル")
        print(f"  ニュース追加: {news_added} 件")
        print("=" * 50)

    except Exception as e:
        print(f"\nエラー: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
