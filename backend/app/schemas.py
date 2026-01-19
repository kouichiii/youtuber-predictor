from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Channel Schemas
class ChannelBase(BaseModel):
    channel_id: str
    name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ChannelCreate(BaseModel):
    channel_id: str


class ChannelStatsResponse(BaseModel):
    subscriber_count: int
    view_count: int
    video_count: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    predicted_growth_rate: float
    confidence_score: Optional[float]
    feature_subscriber_growth_rate: Optional[float]
    feature_view_growth_rate: Optional[float]
    feature_upload_frequency: Optional[float]
    feature_engagement_rate: Optional[float]
    feature_trend_score: Optional[float]
    feature_news_count: Optional[int]
    feature_news_sentiment: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelResponse(BaseModel):
    id: int
    channel_id: str
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    latest_stats: Optional[ChannelStatsResponse] = None
    latest_prediction: Optional[PredictionResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelDetailResponse(ChannelResponse):
    stats_history: List[ChannelStatsResponse] = []
    predictions_history: List[PredictionResponse] = []

    class Config:
        from_attributes = True


# News Schemas
class NewsBase(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    published_at: Optional[datetime] = None


class NewsResponse(NewsBase):
    id: int
    channel_id: int
    channel_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    news: List[NewsResponse]
    total: int
    page: int
    per_page: int


# Ranking Schemas
class RankingEntry(BaseModel):
    rank: int
    channel: ChannelResponse
    predicted_growth_rate: float
    confidence_score: Optional[float]


class RankingResponse(BaseModel):
    rankings: List[RankingEntry]
    updated_at: datetime


# Search Schemas
class YouTubeSearchResult(BaseModel):
    channel_id: str
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    subscriber_count: Optional[int]
