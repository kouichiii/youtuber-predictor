from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from app.config import settings


class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = None
        if self.api_key:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)

    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """チャンネル情報を取得"""
        if not self.youtube:
            raise Exception("YouTube API key not configured")

        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()

            if not response.get("items"):
                return None

            item = response["items"][0]
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})

            return {
                "channel_id": channel_id,
                "name": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "subscriber_count": int(statistics.get("subscriberCount", 0)),
                "view_count": int(statistics.get("viewCount", 0)),
                "video_count": int(statistics.get("videoCount", 0)),
            }
        except Exception as e:
            print(f"Error fetching channel info: {e}")
            return None

    async def search_channels(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """チャンネルを検索"""
        if not self.youtube:
            raise Exception("YouTube API key not configured")

        try:
            # Search for channels
            search_request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results
            )
            search_response = search_request.execute()

            results = []
            channel_ids = []

            for item in search_response.get("items", []):
                channel_id = item["snippet"]["channelId"]
                channel_ids.append(channel_id)

            if not channel_ids:
                return []

            # Get detailed channel info including subscriber counts
            channels_request = self.youtube.channels().list(
                part="snippet,statistics",
                id=",".join(channel_ids)
            )
            channels_response = channels_request.execute()

            for item in channels_response.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})

                # Filter: only include channels with 1000+ subscribers
                subscriber_count = int(statistics.get("subscriberCount", 0))
                if subscriber_count >= 1000:
                    results.append({
                        "channel_id": item["id"],
                        "name": snippet.get("title", ""),
                        "description": snippet.get("description", "")[:200] if snippet.get("description") else None,
                        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                        "subscriber_count": subscriber_count
                    })

            return results
        except Exception as e:
            print(f"Error searching channels: {e}")
            raise

    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """チャンネルの動画一覧を取得"""
        if not self.youtube:
            raise Exception("YouTube API key not configured")

        try:
            request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                order="date",
                maxResults=max_results
            )
            response = request.execute()

            video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

            if not video_ids:
                return []

            # Get video statistics
            videos_request = self.youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids)
            )
            videos_response = videos_request.execute()

            videos = []
            for item in videos_response.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})

                videos.append({
                    "video_id": item["id"],
                    "title": snippet.get("title", ""),
                    "published_at": snippet.get("publishedAt"),
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                })

            return videos
        except Exception as e:
            print(f"Error fetching channel videos: {e}")
            return []
