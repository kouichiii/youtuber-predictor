"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import { getChannel, getNews, ChannelDetail, News } from "@/lib/api";
import FeatureCard from "@/components/FeatureCard";
import StatsChart from "@/components/StatsChart";
import NewsCard from "@/components/NewsCard";

export default function ChannelDetailPage() {
  const params = useParams();
  const channelId = params.channelId as string;

  const [channel, setChannel] = useState<ChannelDetail | null>(null);
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [channelData, newsData] = await Promise.all([
          getChannel(channelId),
          getNews(1, 10, undefined, channelId),
        ]);
        setChannel(channelData);
        setNews(newsData.news);
      } catch (err) {
        setError("データの取得に失敗しました");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [channelId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  if (error || !channel) {
    return (
      <div className="text-center py-12">
        <div className="card inline-block px-8 py-6">
          <p className="text-gray-600">{error || "チャンネルが見つかりません"}</p>
        </div>
      </div>
    );
  }

  const prediction = channel.latest_prediction;
  const stats = channel.latest_stats;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          {channel.thumbnail_url ? (
            <Image
              src={channel.thumbnail_url}
              alt={channel.name}
              width={100}
              height={100}
              className="rounded-full ring-4 ring-gray-100 mx-auto md:mx-0"
            />
          ) : (
            <div className="w-[100px] h-[100px] bg-gray-100 rounded-full flex items-center justify-center ring-4 ring-gray-100 mx-auto md:mx-0">
              <span className="text-gray-400 text-3xl">?</span>
            </div>
          )}
          <div className="flex-grow text-center md:text-left">
            <h1 className="text-2xl font-bold text-gray-900">{channel.name}</h1>
            {channel.description && (
              <p className="text-gray-500 mt-2 line-clamp-2 text-sm">
                {channel.description}
              </p>
            )}
            <div className="flex flex-wrap justify-center md:justify-start items-center gap-4 mt-4 text-sm text-gray-500">
              {stats && (
                <>
                  <span className="flex items-center space-x-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                    </svg>
                    <span>登録者 {stats.subscriber_count.toLocaleString()}</span>
                  </span>
                  <span className="flex items-center space-x-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                    <span>総再生 {stats.view_count.toLocaleString()}</span>
                  </span>
                  <span className="flex items-center space-x-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm3 2h6v4H7V5zm8 8v2h1v-2h-1zm-2-2H7v4h6v-4zm2 0h1V9h-1v2zm1-4V5h-1v2h1zM5 5v2H4V5h1zm0 4H4v2h1V9zm-1 4h1v2H4v-2z" clipRule="evenodd" />
                    </svg>
                    <span>動画数 {stats.video_count.toLocaleString()}</span>
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Prediction Badge */}
          {prediction && (
            <div className="text-center bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl p-6 min-w-[140px]">
              <div className="text-sm text-primary-600 font-medium">
                半年後予測
              </div>
              <div
                className={`text-3xl font-bold mt-1 ${
                  prediction.predicted_growth_rate >= 0
                    ? "text-primary-600"
                    : "text-gray-500"
                }`}
              >
                {prediction.predicted_growth_rate >= 0 ? "+" : ""}
                {prediction.predicted_growth_rate.toFixed(1)}%
              </div>
              {prediction.confidence_score !== null && (
                <div className="mt-2">
                  <div className="w-full h-1.5 bg-white/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${prediction.confidence_score * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-primary-600/70 mt-1">
                    信頼度 {(prediction.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Prediction Features */}
      {prediction && (
        <div>
          <h2 className="section-title">予測に使用した特徴量</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <FeatureCard
              label="登録者成長率（30日）"
              value={
                prediction.feature_subscriber_growth_rate !== null
                  ? prediction.feature_subscriber_growth_rate * 100
                  : null
              }
              unit="%"
              description="直近30日の成長率"
            />
            <FeatureCard
              label="視聴数成長率（30日）"
              value={
                prediction.feature_view_growth_rate !== null
                  ? prediction.feature_view_growth_rate * 100
                  : null
              }
              unit="%"
              description="直近30日の成長率"
            />
            <FeatureCard
              label="投稿頻度"
              value={prediction.feature_upload_frequency}
              unit="本/週"
              description="週あたりの投稿数"
            />
            <FeatureCard
              label="エンゲージメント率"
              value={
                prediction.feature_engagement_rate !== null
                  ? prediction.feature_engagement_rate * 100
                  : null
              }
              unit="%"
              description="視聴数/登録者数"
            />
            <FeatureCard
              label="トレンドスコア"
              value={prediction.feature_trend_score}
              description="Google Trendsでの注目度"
            />
            <FeatureCard
              label="ニュース記事数"
              value={prediction.feature_news_count}
              unit="件"
              description="直近90日のニュース数"
            />
            <FeatureCard
              label="ニュースセンチメント"
              value={
                prediction.feature_news_sentiment !== null
                  ? prediction.feature_news_sentiment * 100
                  : null
              }
              unit="%"
              description="ポジティブニュースの割合"
            />
          </div>
        </div>
      )}

      {/* Stats Charts */}
      {channel.stats_history.length > 0 && (
        <div>
          <h2 className="section-title">統計推移</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card p-4">
              <StatsChart
                data={channel.stats_history}
                dataKey="subscriber_count"
                title="登録者数"
                color="#dc2626"
              />
            </div>
            <div className="card p-4">
              <StatsChart
                data={channel.stats_history}
                dataKey="view_count"
                title="総再生回数"
                color="#f87171"
              />
            </div>
          </div>
        </div>
      )}

      {/* News */}
      {news.length > 0 && (
        <div>
          <h2 className="section-title">関連ニュース</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {news.map((item) => (
              <NewsCard key={item.id} news={item} showChannel={false} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
