from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stats = relationship("ChannelStats", back_populates="channel", order_by="desc(ChannelStats.recorded_at)")
    predictions = relationship("Prediction", back_populates="channel", order_by="desc(Prediction.created_at)")
    news = relationship("News", back_populates="channel", order_by="desc(News.published_at)")


class ChannelStats(Base):
    __tablename__ = "channel_stats"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    subscriber_count = Column(Integer, nullable=False)
    view_count = Column(Integer, nullable=False)
    video_count = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="stats")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    predicted_growth_rate = Column(Float, nullable=False)  # 半年後の成長率予測 (%)
    confidence_score = Column(Float, nullable=True)  # 予測の信頼度

    # 予測に使用した特徴量
    feature_subscriber_growth_rate = Column(Float, nullable=True)  # 直近の登録者成長率
    feature_view_growth_rate = Column(Float, nullable=True)  # 直近の視聴数成長率
    feature_upload_frequency = Column(Float, nullable=True)  # 投稿頻度
    feature_engagement_rate = Column(Float, nullable=True)  # エンゲージメント率
    feature_trend_score = Column(Float, nullable=True)  # Google Trends スコア
    feature_news_count = Column(Integer, nullable=True)  # ニュース記事数
    feature_news_sentiment = Column(Float, nullable=True)  # ニュースのセンチメント

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="predictions")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    source = Column(String(255), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)  # コラボ, メディア出演, 炎上, その他
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    channel = relationship("Channel", back_populates="news")


class TrendData(Base):
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    trend_score = Column(Integer, nullable=False)  # 0-100
    recorded_at = Column(DateTime, default=datetime.utcnow)
