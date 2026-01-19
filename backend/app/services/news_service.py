from typing import List, Dict, Any, Optional
from datetime import datetime
import feedparser
import re
from urllib.parse import quote


class NewsService:
    """Google News RSSからニュースを取得するサービス"""

    BASE_URL = "https://news.google.com/rss/search"

    # ニュースカテゴリ分類のキーワード
    CATEGORY_KEYWORDS = {
        "collaboration": ["コラボ", "共演", "対談", "ゲスト", "featuring", "feat"],
        "media": ["テレビ", "TV", "ラジオ", "出演", "番組", "雑誌", "インタビュー", "取材"],
        "controversy": ["炎上", "批判", "謝罪", "問題", "騒動", "暴露", "告発"],
        "event": ["イベント", "ライブ", "配信", "発表", "新作", "発売", "リリース"],
    }

    async def fetch_news(
        self,
        query: str,
        language: str = "ja",
        region: str = "JP",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Google News RSSからニュースを取得

        Args:
            query: 検索クエリ（YouTuber名など）
            language: 言語コード
            region: 地域コード
            max_results: 最大取得件数
        """
        encoded_query = quote(query)
        url = f"{self.BASE_URL}?q={encoded_query}&hl={language}&gl={region}&ceid={region}:{language}"

        try:
            feed = feedparser.parse(url)
            news_items = []

            for entry in feed.entries[:max_results]:
                # 公開日時のパース
                published_at = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])

                # ソース名の抽出
                source = None
                if hasattr(entry, "source") and entry.source:
                    source = entry.source.get("title", None)

                # カテゴリの自動分類
                category = self._classify_category(entry.title)

                news_items.append({
                    "title": entry.title,
                    "url": entry.link,
                    "source": source,
                    "published_at": published_at,
                    "category": category,
                    "thumbnail_url": self._extract_thumbnail(entry),
                })

            return news_items
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def _classify_category(self, title: str) -> str:
        """タイトルからニュースカテゴリを分類"""
        title_lower = title.lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return category

        return "other"

    def _extract_thumbnail(self, entry: Any) -> Optional[str]:
        """RSSエントリからサムネイルURLを抽出"""
        # media:content からの抽出を試みる
        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if media.get("url"):
                    return media["url"]

        # enclosure からの抽出を試みる
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get("type", "").startswith("image"):
                    return enclosure.get("url")

        return None

    async def fetch_news_for_channels(
        self,
        channel_names: List[str],
        max_per_channel: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        複数チャンネルのニュースを一括取得

        Args:
            channel_names: チャンネル名のリスト
            max_per_channel: 各チャンネルの最大取得件数
        """
        results = {}

        for name in channel_names:
            news = await self.fetch_news(name, max_results=max_per_channel)
            results[name] = news

        return results
