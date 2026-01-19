from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import pandas as pd
import time
import random


class TrendsService:
    """Google Trendsからトレンドデータを取得するサービス"""

    def __init__(self):
        self.pytrends = TrendReq(hl="ja-JP", tz=540, retries=2, backoff_factor=0.5)
        self._last_request_time = 0
        self._min_request_interval = 2.0  # 最低2秒間隔

    def _rate_limit(self):
        """レート制限：リクエスト間隔を確保"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            sleep_time = self._min_request_interval - elapsed + random.uniform(0.5, 1.5)
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    async def get_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str = "today 3-m",
        geo: str = "JP"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        キーワードの検索トレンドを取得

        Args:
            keywords: 検索キーワードのリスト（最大5つ）
            timeframe: 期間 (例: "today 3-m", "today 12-m", "2023-01-01 2024-01-01")
            geo: 地域コード
        """
        try:
            # pytrendsは一度に最大5キーワードまで
            keywords = keywords[:5]

            self._rate_limit()
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
            df = self.pytrends.interest_over_time()

            if df.empty:
                return {keyword: [] for keyword in keywords}

            result = {}
            for keyword in keywords:
                if keyword in df.columns:
                    data = []
                    for date, row in df.iterrows():
                        data.append({
                            "date": date.isoformat(),
                            "value": int(row[keyword])
                        })
                    result[keyword] = data
                else:
                    result[keyword] = []

            return result
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return {keyword: [] for keyword in keywords}

    async def get_current_trend_score(
        self,
        keyword: str,
        geo: str = "JP"
    ) -> Optional[int]:
        """
        キーワードの現在のトレンドスコアを取得（0-100）

        Args:
            keyword: 検索キーワード
            geo: 地域コード
        """
        try:
            self._rate_limit()
            self.pytrends.build_payload([keyword], cat=0, timeframe="now 7-d", geo=geo)
            df = self.pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                return None

            # 最新のスコアを返す
            return int(df[keyword].iloc[-1])
        except Exception as e:
            # 429エラーの場合はスキップ（ログを減らす）
            if "429" in str(e):
                return None
            print(f"Error fetching current trend score: {e}")
            return None

    async def get_related_queries(
        self,
        keyword: str,
        geo: str = "JP"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        関連する検索クエリを取得

        Args:
            keyword: 検索キーワード
            geo: 地域コード
        """
        try:
            self._rate_limit()
            self.pytrends.build_payload([keyword], cat=0, timeframe="today 3-m", geo=geo)
            related = self.pytrends.related_queries()

            result = {
                "top": [],
                "rising": []
            }

            if keyword in related:
                keyword_data = related[keyword]

                if keyword_data.get("top") is not None and not keyword_data["top"].empty:
                    for _, row in keyword_data["top"].head(10).iterrows():
                        result["top"].append({
                            "query": row["query"],
                            "value": int(row["value"])
                        })

                if keyword_data.get("rising") is not None and not keyword_data["rising"].empty:
                    for _, row in keyword_data["rising"].head(10).iterrows():
                        result["rising"].append({
                            "query": row["query"],
                            "value": str(row["value"])  # Can be "Breakout" or percentage
                        })

            return result
        except Exception as e:
            print(f"Error fetching related queries: {e}")
            return {"top": [], "rising": []}

    async def calculate_trend_features(
        self,
        keyword: str,
        geo: str = "JP"
    ) -> Dict[str, Any]:
        """
        機械学習用のトレンド特徴量を計算

        Args:
            keyword: 検索キーワード
            geo: 地域コード
        """
        try:
            # 過去3ヶ月のトレンドデータを取得
            self._rate_limit()
            self.pytrends.build_payload([keyword], cat=0, timeframe="today 3-m", geo=geo)
            df = self.pytrends.interest_over_time()

            if df.empty or keyword not in df.columns:
                return {
                    "current_score": None,
                    "avg_score": None,
                    "max_score": None,
                    "trend_direction": None,
                    "volatility": None
                }

            values = df[keyword].values

            # 特徴量の計算
            current_score = int(values[-1])
            avg_score = float(values.mean())
            max_score = int(values.max())

            # トレンドの方向性（直近2週間 vs その前の2週間）
            if len(values) >= 4:
                recent = values[-2:].mean()
                previous = values[-4:-2].mean()
                trend_direction = float(recent - previous)
            else:
                trend_direction = 0.0

            # ボラティリティ（標準偏差）
            volatility = float(values.std())

            return {
                "current_score": current_score,
                "avg_score": avg_score,
                "max_score": max_score,
                "trend_direction": trend_direction,
                "volatility": volatility
            }
        except Exception as e:
            print(f"Error calculating trend features: {e}")
            return {
                "current_score": None,
                "avg_score": None,
                "max_score": None,
                "trend_direction": None,
                "volatility": None
            }
