"""
モデル学習スクリプト

使い方:
    cd backend
    python scripts/train_model.py

※ 十分なデータ（最低6ヶ月分の履歴）が溜まってから実行してください。
"""
import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import pandas as pd
from app.database import SessionLocal
from app.models import Channel, ChannelStats
from ml.predictor import GrowthPredictor
from ml.feature_extractor import FeatureExtractor


def prepare_training_data():
    """
    学習データを準備

    6ヶ月前のデータから特徴量を抽出し、
    現在のデータと比較して実際の成長率を計算
    """
    db = SessionLocal()

    try:
        channels = db.query(Channel).all()

        if not channels:
            print("チャンネルがありません")
            return None

        training_data = []
        six_months_ago = datetime.utcnow() - timedelta(days=180)

        for channel in channels:
            # 6ヶ月前のデータを取得
            old_stats = db.query(ChannelStats).filter(
                ChannelStats.channel_id == channel.id,
                ChannelStats.recorded_at <= six_months_ago
            ).order_by(ChannelStats.recorded_at.desc()).first()

            # 現在のデータを取得
            current_stats = db.query(ChannelStats).filter(
                ChannelStats.channel_id == channel.id
            ).order_by(ChannelStats.recorded_at.desc()).first()

            if not old_stats or not current_stats:
                continue

            # 実際の成長率を計算
            if old_stats.subscriber_count > 0:
                actual_growth = (
                    (current_stats.subscriber_count - old_stats.subscriber_count)
                    / old_stats.subscriber_count
                ) * 100
            else:
                continue

            # 6ヶ月前時点での特徴量を抽出（ここは簡略化）
            # 本来は6ヶ月前の時点でのFeatureExtractorを使うべきだが、
            # 履歴データの構造上、現在の特徴量を使う
            extractor = FeatureExtractor(db)
            features = extractor.extract_features(channel.id)
            features["actual_growth_rate"] = actual_growth
            features["channel_name"] = channel.name

            training_data.append(features)

        if not training_data:
            print("十分な履歴データがありません")
            print("最低6ヶ月間データを収集してから再実行してください")
            return None

        return pd.DataFrame(training_data)

    finally:
        db.close()


def train():
    """モデルを学習"""
    print(f"\n{'='*50}")
    print(f"モデル学習開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 学習データを準備
    print("学習データを準備中...")
    df = prepare_training_data()

    if df is None or len(df) < 10:
        print(f"\nエラー: 学習に必要なデータが不足しています")
        print(f"現在のデータ数: {len(df) if df is not None else 0}")
        print(f"必要なデータ数: 最低10チャンネル分の6ヶ月履歴")
        return

    print(f"学習データ数: {len(df)}")
    print(f"特徴量: {GrowthPredictor.FEATURE_COLUMNS}")

    # モデルを学習
    print("\nモデルを学習中...")
    predictor = GrowthPredictor()
    metrics = predictor.train(df)

    print(f"\n{'='*50}")
    print("学習完了!")
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"R2 Score: {metrics['r2']:.4f}")
    print(f"{'='*50}")

    # 特徴量の重要度を表示
    print("\n特徴量の重要度:")
    importance = predictor.get_feature_importance()
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_importance:
        bar = "=" * int(score / max(importance.values()) * 30)
        print(f"  {name:<30} {bar} ({score:.0f})")

    print(f"\nモデルを保存しました: ml/model.pkl")


if __name__ == "__main__":
    train()
