"""
CSVからチャンネルを一括登録するスクリプト

使い方:
    cd backend
    python scripts/import_channels.py

事前準備:
    data/channel_ids.csv に以下の形式でチャンネルIDを用意:
    channel_id,name,url
    UCxxxx,チャンネル名,https://youtube.com/channel/UCxxxx
"""
import sys
import csv
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.database import SessionLocal
from app.models import Channel, ChannelStats
from app.services.youtube_service import YouTubeService


async def resolve_handle_to_id(youtube: YouTubeService, handle: str) -> str:
    """@handle形式をチャンネルIDに変換"""
    # YouTube APIで検索
    try:
        results = await youtube.search_channels(handle, max_results=1)
        if results:
            return results[0]["channel_id"]
    except Exception as e:
        print(f"  ハンドル解決エラー ({handle}): {e}")
    return None


async def import_channels(csv_path: str = "data/channel_ids.csv", limit: int = None):
    """CSVからチャンネルを登録"""
    db = SessionLocal()
    youtube = YouTubeService()

    try:
        # CSV読み込み
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if limit:
            rows = rows[:limit]

        print(f"\n{'='*50}")
        print(f"チャンネル一括登録")
        print(f"CSVファイル: {csv_path}")
        print(f"対象件数: {len(rows)}")
        print(f"{'='*50}\n")

        imported = 0
        skipped = 0
        errors = 0

        for i, row in enumerate(rows, 1):
            channel_id = row.get("channel_id", "").strip()

            if not channel_id:
                continue

            print(f"[{i}/{len(rows)}] {channel_id[:30]}...", end=" ")

            # 既に登録済みかチェック
            existing = db.query(Channel).filter(Channel.channel_id == channel_id).first()
            if existing:
                print("スキップ (登録済み)")
                skipped += 1
                continue

            # @handle形式の場合は解決
            if channel_id.startswith("@"):
                resolved_id = await resolve_handle_to_id(youtube, channel_id)
                if resolved_id:
                    channel_id = resolved_id
                else:
                    print("エラー (ハンドル解決失敗)")
                    errors += 1
                    continue

            # YouTube APIからチャンネル情報を取得
            try:
                info = await youtube.get_channel_info(channel_id)

                if not info:
                    print("エラー (チャンネル取得失敗)")
                    errors += 1
                    continue

                # 登録者1000人未満はスキップ
                if info.get("subscriber_count", 0) < 1000:
                    print(f"スキップ (登録者 {info.get('subscriber_count', 0)}人)")
                    skipped += 1
                    continue

                # チャンネルを作成
                channel = Channel(
                    channel_id=channel_id,
                    name=info["name"],
                    description=info.get("description"),
                    thumbnail_url=info.get("thumbnail_url"),
                )
                db.add(channel)
                db.commit()
                db.refresh(channel)

                # 初期統計を保存
                stats = ChannelStats(
                    channel_id=channel.id,
                    subscriber_count=info["subscriber_count"],
                    view_count=info.get("view_count", 0),
                    video_count=info.get("video_count", 0),
                )
                db.add(stats)
                db.commit()

                print(f"登録完了 ({info['name'][:20]}...)")
                imported += 1

            except Exception as e:
                print(f"エラー ({e})")
                errors += 1
                db.rollback()

            # API制限対策（10リクエストごとに少し待機）
            if i % 10 == 0:
                await asyncio.sleep(0.5)

        print(f"\n{'='*50}")
        print(f"完了!")
        print(f"  登録: {imported}件")
        print(f"  スキップ: {skipped}件")
        print(f"  エラー: {errors}件")
        print(f"{'='*50}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/channel_ids.csv", help="CSVファイルパス")
    parser.add_argument("--limit", type=int, default=None, help="登録上限数")
    args = parser.parse_args()

    asyncio.run(import_channels(args.csv, args.limit))
