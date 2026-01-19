"""
管理用APIエンドポイント
データ収集・予測・学習をWebから実行できるようにする
"""
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Channel, ChannelStats, News, TrendData, Prediction
from app.services.youtube_service import YouTubeService
from app.services.news_service import NewsService
from app.services.trends_service import TrendsService
from ml.predictor import GrowthPredictor
from ml.feature_extractor import FeatureExtractor

router = APIRouter()

# ジョブのステータス管理
job_status = {
    "status": "idle",
    "message": "",
    "started_at": None,
    "completed_at": None,
}


def update_status(status: str, message: str):
    global job_status
    job_status["status"] = status
    job_status["message"] = message
    if status == "running":
        job_status["started_at"] = datetime.utcnow().isoformat()
    elif status in ["completed", "error"]:
        job_status["completed_at"] = datetime.utcnow().isoformat()


@router.get("/status")
async def get_job_status():
    """ジョブのステータスを取得"""
    return job_status


@router.post("/collect")
async def run_data_collection(db: Session = Depends(get_db)):
    """データ収集を実行"""
    if job_status["status"] == "running":
        raise HTTPException(status_code=409, detail="別のジョブが実行中です")

    update_status("running", "データ収集を開始...")

    try:
        channels = db.query(Channel).all()

        if not channels:
            update_status("error", "登録されているチャンネルがありません")
            raise HTTPException(status_code=400, detail="チャンネルが登録されていません")

        youtube = YouTubeService()
        news_service = NewsService()
        trends_service = TrendsService()

        collected_count = 0

        for channel in channels:
            try:
                # YouTube統計を収集
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

                # ニュースを収集
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

                # Trendsを収集
                try:
                    trend_score = await trends_service.get_current_trend_score(channel.name)
                    if trend_score is not None:
                        trend = TrendData(
                            channel_id=channel.id,
                            trend_score=trend_score,
                        )
                        db.add(trend)
                except Exception:
                    pass  # Trendsのエラーは無視

                collected_count += 1

            except Exception as e:
                print(f"Error collecting {channel.name}: {e}")

        db.commit()
        message = f"データ収集完了: {collected_count}/{len(channels)} チャンネル"
        update_status("completed", message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        update_status("error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def run_prediction(db: Session = Depends(get_db)):
    """予測を実行"""
    if job_status["status"] == "running":
        raise HTTPException(status_code=409, detail="別のジョブが実行中です")

    update_status("running", "予測を開始...")

    try:
        channels = db.query(Channel).all()

        if not channels:
            update_status("error", "登録されているチャンネルがありません")
            raise HTTPException(status_code=400, detail="チャンネルが登録されていません")

        predictor = GrowthPredictor()
        extractor = FeatureExtractor(db)

        predicted_count = 0

        for channel in channels:
            try:
                features = extractor.extract_features(channel.id)
                result = predictor.predict(features)

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
                predicted_count += 1

            except Exception as e:
                print(f"Error predicting {channel.name}: {e}")

        db.commit()
        message = f"予測完了: {predicted_count}/{len(channels)} チャンネル"
        update_status("completed", message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        update_status("error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def run_training(db: Session = Depends(get_db)):
    """モデル学習を実行"""
    if job_status["status"] == "running":
        raise HTTPException(status_code=409, detail="別のジョブが実行中です")

    update_status("running", "モデル学習を開始...")

    try:
        # 学習には十分なデータが必要
        channels = db.query(Channel).all()
        if len(channels) < 10:
            message = "学習には最低10チャンネルのデータが必要です"
            update_status("error", message)
            raise HTTPException(status_code=400, detail=message)

        # 6ヶ月分の履歴があるかチェック
        # （簡略化: 実際はtrain_model.pyの処理を呼ぶ）
        message = "モデル学習は現在コマンドラインから実行してください: python scripts/train_model.py"
        update_status("completed", message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        update_status("error", str(e))
        raise HTTPException(status_code=500, detail=str(e))
