from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Channel, ChannelStats, Prediction
from app.schemas import ChannelResponse, ChannelDetailResponse, ChannelCreate, ChannelStatsResponse, PredictionResponse

router = APIRouter()


@router.get("/count")
async def get_channels_count(db: Session = Depends(get_db)):
    """登録済みチャンネルの総数を取得"""
    total = db.query(Channel).count()
    return {"total": total}


@router.get("/", response_model=List[ChannelResponse])
async def get_channels(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """登録済みチャンネル一覧を取得"""
    channels = db.query(Channel).offset(skip).limit(limit).all()

    result = []
    for channel in channels:
        latest_stats = db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel.id
        ).order_by(ChannelStats.recorded_at.desc()).first()

        latest_prediction = db.query(Prediction).filter(
            Prediction.channel_id == channel.id
        ).order_by(Prediction.created_at.desc()).first()

        channel_data = ChannelResponse(
            id=channel.id,
            channel_id=channel.channel_id,
            name=channel.name,
            description=channel.description,
            thumbnail_url=channel.thumbnail_url,
            created_at=channel.created_at,
            latest_stats=ChannelStatsResponse.model_validate(latest_stats) if latest_stats else None,
            latest_prediction=PredictionResponse.model_validate(latest_prediction) if latest_prediction else None
        )
        result.append(channel_data)

    return result


@router.get("/{channel_id}", response_model=ChannelDetailResponse)
async def get_channel(channel_id: str, db: Session = Depends(get_db)):
    """チャンネル詳細を取得"""
    channel = db.query(Channel).filter(Channel.channel_id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    stats_history = db.query(ChannelStats).filter(
        ChannelStats.channel_id == channel.id
    ).order_by(ChannelStats.recorded_at.desc()).limit(180).all()

    predictions_history = db.query(Prediction).filter(
        Prediction.channel_id == channel.id
    ).order_by(Prediction.created_at.desc()).limit(30).all()

    latest_stats = stats_history[0] if stats_history else None
    latest_prediction = predictions_history[0] if predictions_history else None

    return ChannelDetailResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        name=channel.name,
        description=channel.description,
        thumbnail_url=channel.thumbnail_url,
        created_at=channel.created_at,
        latest_stats=ChannelStatsResponse.model_validate(latest_stats) if latest_stats else None,
        latest_prediction=PredictionResponse.model_validate(latest_prediction) if latest_prediction else None,
        stats_history=[ChannelStatsResponse.model_validate(s) for s in stats_history],
        predictions_history=[PredictionResponse.model_validate(p) for p in predictions_history]
    )


@router.post("/", response_model=ChannelResponse)
async def add_channel(channel_data: ChannelCreate, db: Session = Depends(get_db)):
    """新しいチャンネルを追加"""
    from app.services.youtube_service import YouTubeService

    # Check if channel already exists
    existing = db.query(Channel).filter(Channel.channel_id == channel_data.channel_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel already registered")

    # Fetch channel info from YouTube API
    youtube_service = YouTubeService()
    channel_info = await youtube_service.get_channel_info(channel_data.channel_id)

    if not channel_info:
        raise HTTPException(status_code=404, detail="Channel not found on YouTube")

    # Create channel
    channel = Channel(
        channel_id=channel_data.channel_id,
        name=channel_info["name"],
        description=channel_info.get("description"),
        thumbnail_url=channel_info.get("thumbnail_url")
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)

    # Add initial stats
    if channel_info.get("subscriber_count") is not None:
        stats = ChannelStats(
            channel_id=channel.id,
            subscriber_count=channel_info["subscriber_count"],
            view_count=channel_info.get("view_count", 0),
            video_count=channel_info.get("video_count", 0)
        )
        db.add(stats)
        db.commit()

    return ChannelResponse(
        id=channel.id,
        channel_id=channel.channel_id,
        name=channel.name,
        description=channel.description,
        thumbnail_url=channel.thumbnail_url,
        created_at=channel.created_at,
        latest_stats=None,
        latest_prediction=None
    )


@router.delete("/{channel_id}")
async def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    """チャンネルを削除"""
    channel = db.query(Channel).filter(Channel.channel_id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    db.delete(channel)
    db.commit()
    return {"message": "Channel deleted successfully"}
