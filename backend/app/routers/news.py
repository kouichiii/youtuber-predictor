from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import News, Channel
from app.schemas import NewsResponse, NewsListResponse

router = APIRouter()


@router.get("/", response_model=NewsListResponse)
async def get_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    channel_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """ニュース一覧を取得"""
    query = db.query(News).join(Channel)

    if category:
        query = query.filter(News.category == category)

    if channel_id:
        query = query.filter(Channel.channel_id == channel_id)

    total = query.count()
    news_items = query.order_by(News.published_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    news_responses = []
    for news in news_items:
        channel = db.query(Channel).filter(Channel.id == news.channel_id).first()
        news_responses.append(NewsResponse(
            id=news.id,
            channel_id=news.channel_id,
            channel_name=channel.name if channel else None,
            title=news.title,
            url=news.url,
            source=news.source,
            thumbnail_url=news.thumbnail_url,
            category=news.category,
            published_at=news.published_at,
            created_at=news.created_at
        ))

    return NewsListResponse(
        news=news_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/categories")
async def get_news_categories():
    """利用可能なニュースカテゴリを取得"""
    return {
        "categories": [
            {"id": "collaboration", "name": "コラボ"},
            {"id": "media", "name": "メディア出演"},
            {"id": "controversy", "name": "炎上"},
            {"id": "event", "name": "イベント"},
            {"id": "other", "name": "その他"}
        ]
    }
