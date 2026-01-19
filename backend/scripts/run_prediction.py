"""
予測実行スクリプト

使い方:
    cd backend
    python scripts/run_prediction.py

DBに保存されたデータを使って、全チャンネルの成長予測を実行します。
"""
import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.database import SessionLocal
from app.models import Channel, Prediction
from ml.predictor import GrowthPredictor
from ml.feature_extractor import FeatureExtractor


def run_predictions():
    """全チャンネルの予測を実行"""
    db = SessionLocal()

    try:
        channels = db.query(Channel).all()

        if not channels:
            print("登録されているチャンネルがありません。")
            return

        print(f"\n{'='*50}")
        print(f"予測実行開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"対象チャンネル数: {len(channels)}")
        print(f"{'='*50}\n")

        predictor = GrowthPredictor()
        extractor = FeatureExtractor(db)

        results = []

        for i, channel in enumerate(channels, 1):
            print(f"[{i}/{len(channels)}] {channel.name}")

            # 特徴量を抽出
            features = extractor.extract_features(channel.id)

            # 予測実行
            result = predictor.predict(features)

            # 予測結果を保存
            prediction = Prediction(
                channel_id=channel.id,
                predicted_growth_rate=result["predicted_growth_rate"],
                confidence_score=result["confidence_score"],
                feature_subscriber_growth_rate=features.get("subscriber_growth_rate_30d"),
                feature_view_growth_rate=features.get("view_growth_rate_30d"),
                feature_upload_frequency=features.get("upload_frequency"),
                feature_engagement_rate=features.get("engagement_rate"),
                feature_trend_score=features.get("trend_score"),
                feature_news_count=features.get("news_count"),
                feature_news_sentiment=features.get("news_positive_ratio"),
            )
            db.add(prediction)

            growth = result["predicted_growth_rate"]
            confidence = result["confidence_score"]
            sign = "+" if growth >= 0 else ""
            print(f"    予測成長率: {sign}{growth:.1f}% (信頼度: {confidence*100:.0f}%)")

            results.append({
                "name": channel.name,
                "growth": growth,
                "confidence": confidence
            })

        db.commit()

        # ランキング表示
        print(f"\n{'='*50}")
        print("成長予測ランキング")
        print(f"{'='*50}")

        results.sort(key=lambda x: x["growth"], reverse=True)
        for i, r in enumerate(results[:10], 1):
            sign = "+" if r["growth"] >= 0 else ""
            print(f"{i:2}. {r['name'][:20]:<20} {sign}{r['growth']:>6.1f}%")

        print(f"\n予測完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    finally:
        db.close()


if __name__ == "__main__":
    run_predictions()
