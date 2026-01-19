from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import channels, news, ranking, search, admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YouTuber Growth Predictor API",
    description="YouTuberの成長予測を行うAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["ranking"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "YouTuber Growth Predictor API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
