from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Channel, ChannelStats, News, TrendData


class FeatureExtractor:
    """チャンネルデータから機械学習用の特徴量を抽出"""

    def __init__(self, db: Session):
        self.db = db

    def extract_features(self, channel_id: int) -> Dict[str, Any]:
        """
        チャンネルの特徴量を抽出

        Args:
            channel_id: チャンネルのDB ID
        """
        channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            return {}

        features = {}

        # 基本統計
        features.update(self._extract_basic_stats(channel_id))

        # 成長率
        features.update(self._extract_growth_rates(channel_id))

        # 投稿頻度・エンゲージメント
        features.update(self._extract_activity_features(channel_id))

        # トレンドスコア
        features.update(self._extract_trend_features(channel_id))

        # ニュース関連
        features.update(self._extract_news_features(channel_id))

        # チャンネル年齢
        features["channel_age_days"] = (datetime.utcnow() - channel.created_at).days

        return features

    def _extract_basic_stats(self, channel_id: int) -> Dict[str, Any]:
        """基本統計の抽出"""
        latest_stats = self.db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel_id
        ).order_by(ChannelStats.recorded_at.desc()).first()

        if not latest_stats:
            return {
                "subscriber_count": None,
                "view_count": None,
                "video_count": None,
            }

        return {
            "subscriber_count": latest_stats.subscriber_count,
            "view_count": latest_stats.view_count,
            "video_count": latest_stats.video_count,
        }

    def _extract_growth_rates(self, channel_id: int) -> Dict[str, Any]:
        """成長率の計算"""
        now = datetime.utcnow()

        # 直近のデータ
        latest_stats = self.db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel_id
        ).order_by(ChannelStats.recorded_at.desc()).first()

        if not latest_stats:
            return {
                "subscriber_growth_rate_30d": None,
                "subscriber_growth_rate_90d": None,
                "view_growth_rate_30d": None,
            }

        # 30日前のデータ
        stats_30d = self.db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel_id,
            ChannelStats.recorded_at <= now - timedelta(days=30)
        ).order_by(ChannelStats.recorded_at.desc()).first()

        # 90日前のデータ
        stats_90d = self.db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel_id,
            ChannelStats.recorded_at <= now - timedelta(days=90)
        ).order_by(ChannelStats.recorded_at.desc()).first()

        result = {
            "subscriber_growth_rate_30d": None,
            "subscriber_growth_rate_90d": None,
            "view_growth_rate_30d": None,
        }

        if stats_30d and stats_30d.subscriber_count > 0:
            result["subscriber_growth_rate_30d"] = (
                (latest_stats.subscriber_count - stats_30d.subscriber_count)
                / stats_30d.subscriber_count
            )
            if stats_30d.view_count > 0:
                result["view_growth_rate_30d"] = (
                    (latest_stats.view_count - stats_30d.view_count)
                    / stats_30d.view_count
                )

        if stats_90d and stats_90d.subscriber_count > 0:
            result["subscriber_growth_rate_90d"] = (
                (latest_stats.subscriber_count - stats_90d.subscriber_count)
                / stats_90d.subscriber_count
            )

        return result

    def _extract_activity_features(self, channel_id: int) -> Dict[str, Any]:
        """投稿頻度とエンゲージメントの抽出"""
        # 直近30日の統計変化から推定
        now = datetime.utcnow()

        stats_list = self.db.query(ChannelStats).filter(
            ChannelStats.channel_id == channel_id,
            ChannelStats.recorded_at >= now - timedelta(days=30)
        ).order_by(ChannelStats.recorded_at).all()

        if len(stats_list) < 2:
            return {
                "upload_frequency": None,
                "avg_views_per_video": None,
                "engagement_rate": None,
            }

        first = stats_list[0]
        last = stats_list[-1]

        # 投稿頻度（動画/週）
        video_diff = last.video_count - first.video_count
        days_diff = (last.recorded_at - first.recorded_at).days or 1
        upload_frequency = (video_diff / days_diff) * 7

        # 平均視聴回数
        avg_views = last.view_count / last.video_count if last.video_count > 0 else 0

        # エンゲージメント率（視聴回数/登録者数）
        engagement_rate = (
            last.view_count / last.subscriber_count
            if last.subscriber_count > 0 else 0
        )

        return {
            "upload_frequency": upload_frequency,
            "avg_views_per_video": avg_views,
            "engagement_rate": engagement_rate,
        }

    def _extract_trend_features(self, channel_id: int) -> Dict[str, Any]:
        """トレンド関連の特徴量"""
        now = datetime.utcnow()

        # 直近のトレンドデータ
        recent_trends = self.db.query(TrendData).filter(
            TrendData.channel_id == channel_id,
            TrendData.recorded_at >= now - timedelta(days=30)
        ).order_by(TrendData.recorded_at).all()

        if not recent_trends:
            return {
                "trend_score": None,
                "trend_direction": None,
                "trend_volatility": None,
            }

        scores = [t.trend_score for t in recent_trends]

        # 現在のスコア
        current_score = scores[-1] if scores else 0

        # トレンドの方向（直近の変化）
        if len(scores) >= 2:
            trend_direction = scores[-1] - scores[0]
        else:
            trend_direction = 0

        # ボラティリティ（標準偏差）
        import numpy as np
        volatility = float(np.std(scores)) if len(scores) > 1 else 0

        return {
            "trend_score": current_score,
            "trend_direction": trend_direction,
            "trend_volatility": volatility,
        }

    def _extract_news_features(self, channel_id: int) -> Dict[str, Any]:
        """ニュース関連の特徴量"""
        now = datetime.utcnow()

        # 直近90日のニュース
        recent_news = self.db.query(News).filter(
            News.channel_id == channel_id,
            News.created_at >= now - timedelta(days=90)
        ).all()

        news_count = len(recent_news)

        if news_count == 0:
            return {
                "news_count": 0,
                "news_positive_ratio": 0,
                "news_negative_ratio": 0,
            }

        # カテゴリ別の集計
        positive_categories = ["collaboration", "media", "event"]
        negative_categories = ["controversy"]

        positive_count = sum(1 for n in recent_news if n.category in positive_categories)
        negative_count = sum(1 for n in recent_news if n.category in negative_categories)

        return {
            "news_count": news_count,
            "news_positive_ratio": positive_count / news_count,
            "news_negative_ratio": negative_count / news_count,
        }
