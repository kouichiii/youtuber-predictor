from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.schemas import YouTubeSearchResult
from app.services.youtube_service import YouTubeService

router = APIRouter()


@router.get("/youtube", response_model=List[YouTubeSearchResult])
async def search_youtube_channels(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(10, ge=1, le=50)
):
    """YouTubeでチャンネルを検索"""
    youtube_service = YouTubeService()

    try:
        results = await youtube_service.search_channels(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")
