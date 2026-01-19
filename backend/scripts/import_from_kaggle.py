"""
Kaggleの2024 YouTubeチャンネルデータセットからチャンネルIDを抽出してDBに登録

使い方:
    cd backend
    pip install kagglehub
    python scripts/import_from_kaggle.py

データセット: asaniczka/2024-youtube-channels-1-million
"""
import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import kagglehub

from app.database import SessionLocal
from app.models import Channel, ChannelStats
from app.services.youtube_service import YouTubeService

DATASET_PATH = "maliqr/vtuber-like-views-and-subscriber-data"


def download_dataset():
    """Kaggleからデータセットをダウンロード"""
    print("Kaggleからデータセットをダウンロード中...")
    print(f"データセット: {DATASET_PATH}")
    path = kagglehub.dataset_download(DATASET_PATH)
    print(f"ダウンロード完了: {path}")
    return path


def extract_channel_ids(dataset_path: str, country: str = "JP", limit: int = 10000):
    """
    データセットからユニークなチャンネルIDを抽出

    Args:
        dataset_path: データセットのパス
        country: 対象国コード (JP, US, etc.) - このデータセットでは国フィルタは使用しない
        limit: 最大取得件数
    """
    print(f"\nチャンネルIDを抽出中...")

    # CSVファイルを探す
    csv_files = list(Path(dataset_path).glob("**/*.csv"))
    print(f"見つかったCSVファイル: {len(csv_files)}")

    for f in csv_files:
        print(f"  - {f.name}")

    all_channels = {}

    for csv_file in csv_files:
        print(f"\n読み込み中: {csv_file.name}")
        try:
            # 大きいファイルなので最初の行だけ読んでカラムを確認
            df_sample = pd.read_csv(csv_file, encoding='utf-8', nrows=5)
            print(f"  カラム: {df_sample.columns.tolist()}")

            # チャンネルIDのカラムを探す
            channel_id_col = None
            channel_name_col = None
            subscriber_col = None

            for col in df_sample.columns:
                col_lower = col.lower().replace('_', '').replace(' ', '')

                # チャンネルID
                if 'channelid' in col_lower or col_lower == 'id':
                    channel_id_col = col
                elif 'channel' in col_lower and 'id' in col_lower:
                    channel_id_col = col

                # チャンネル名
                if 'channelname' in col_lower or 'name' in col_lower or 'title' in col_lower:
                    if channel_name_col is None:
                        channel_name_col = col

                # 登録者数（ソート用）
                if 'subscriber' in col_lower or 'sub' in col_lower:
                    subscriber_col = col

            if channel_id_col is None:
                print(f"  チャンネルIDカラムが見つかりません")
                # IDカラムがない場合、最初のカラムを試す
                if len(df_sample.columns) > 0:
                    first_col = df_sample.columns[0]
                    sample_val = str(df_sample[first_col].iloc[0])
                    if sample_val.startswith('UC'):
                        channel_id_col = first_col
                        print(f"  最初のカラムをチャンネルIDとして使用: {channel_id_col}")

                if channel_id_col is None:
                    continue

            print(f"  チャンネルIDカラム: {channel_id_col}")
            if channel_name_col:
                print(f"  チャンネル名カラム: {channel_name_col}")
            if subscriber_col:
                print(f"  登録者数カラム: {subscriber_col}")

            # 全データを読み込み
            print(f"  データ読み込み中...")
            df = pd.read_csv(csv_file, encoding='utf-8', on_bad_lines='skip')
            print(f"  総行数: {len(df)}")

            # 登録者数でソート（降順）
            if subscriber_col and subscriber_col in df.columns:
                # 数値に変換
                df[subscriber_col] = pd.to_numeric(df[subscriber_col], errors='coerce')
                df = df.sort_values(by=subscriber_col, ascending=False)
                print(f"  登録者数でソート完了")

            # ユニークなチャンネルを抽出
            for _, row in df.iterrows():
                channel_id = str(row.get(channel_id_col, '')).strip()

                # UCで始まるIDのみ（YouTube チャンネルID形式）
                if channel_id and channel_id.startswith('UC') and len(channel_id) == 24:
                    if channel_id not in all_channels:
                        name = str(row.get(channel_name_col, 'Unknown')).strip() if channel_name_col else 'Unknown'
                        all_channels[channel_id] = name

                        if len(all_channels) >= limit:
                            break

                        if len(all_channels) % 1000 == 0:
                            print(f"    抽出済み: {len(all_channels)}件")

            print(f"  このファイルから抽出: {len(all_channels)}件")

            if len(all_channels) >= limit:
                break

        except Exception as e:
            print(f"  読み込みエラー: {e}")
            continue

    print(f"\n合計チャンネル数: {len(all_channels)}")
    return all_channels


async def import_to_db(channels: dict, limit: int = None):
    """
    チャンネルをDBに登録

    Args:
        channels: {channel_id: name} の辞書
        limit: 登録上限
    """
    db = SessionLocal()
    youtube = YouTubeService()

    try:
        channel_list = list(channels.items())
        if limit:
            channel_list = channel_list[:limit]

        print(f"\n{'='*50}")
        print(f"DBへの登録を開始")
        print(f"対象: {len(channel_list)}チャンネル")
        print(f"{'='*50}\n")

        imported = 0
        skipped = 0
        errors = 0

        for i, (channel_id, name) in enumerate(channel_list, 1):
            print(f"[{i}/{len(channel_list)}] {channel_id} ({name[:20]}...)", end=" ")

            # 既に登録済みかチェック
            existing = db.query(Channel).filter(Channel.channel_id == channel_id).first()
            if existing:
                print("スキップ (登録済み)")
                skipped += 1
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

                print(f"OK ({info['subscriber_count']:,}人)")
                imported += 1

            except Exception as e:
                print(f"エラー ({e})")
                errors += 1
                db.rollback()

            # API制限対策
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


async def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10000, help="取得するチャンネル数の上限")
    parser.add_argument("--import-limit", type=int, default=None, help="DBに登録する上限（テスト用）")
    parser.add_argument("--country", default="JP", help="優先する国コード")
    args = parser.parse_args()

    # 1. データセットをダウンロード
    dataset_path = download_dataset()

    # 2. チャンネルIDを抽出
    channels = extract_channel_ids(dataset_path, country=args.country, limit=args.limit)

    if not channels:
        print("チャンネルが見つかりませんでした")
        return

    # 3. DBに登録
    await import_to_db(channels, limit=args.import_limit)


if __name__ == "__main__":
    asyncio.run(main())
