from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Channel, ChannelStats, Prediction
from app.schemas import RankingResponse, RankingEntry, ChannelResponse, ChannelStatsResponse, PredictionResponse

router = APIRouter()


@router.get("/", response_model=RankingResponse)
async def get_ranking(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """成長予測ランキングを取得"""
    # Get latest predictions for each channel
    from sqlalchemy import func

    subquery = db.query(
        Prediction.channel_id,
        func.max(Prediction.created_at).label("max_created_at")
    ).group_by(Prediction.channel_id).subquery()

    predictions = db.query(Prediction).join(
        subquery,
        (Prediction.channel_id == subquery.c.channel_id) &
        (Prediction.created_at == subquery.c.max_created_at)
    ).order_by(Prediction.predicted_growth_rate.desc()).limit(limit).all()

    rankings = []
    for idx, prediction in enumerate(predictions, 1):
        channel = db.query(Channel).filter(Channel.id == prediction.channel_id).first()
        if not channel:
            continue

        latest_stats = db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel.id
        ).order_by(ChannelStats.recorded_at.desc()).first()

        channel_response = ChannelResponse(
            id=channel.id,
            channel_id=channel.channel_id,
            name=channel.name,
            description=channel.description,
            thumbnail_url=channel.thumbnail_url,
            created_at=channel.created_at,
            latest_stats=ChannelStatsResponse.model_validate(latest_stats) if latest_stats else None,
            latest_prediction=PredictionResponse.model_validate(prediction)
        )

        rankings.append(RankingEntry(
            rank=idx,
            channel=channel_response,
            predicted_growth_rate=prediction.predicted_growth_rate,
            confidence_score=prediction.confidence_score
        ))

    return RankingResponse(
        rankings=rankings,
        updated_at=datetime.utcnow()
    )
