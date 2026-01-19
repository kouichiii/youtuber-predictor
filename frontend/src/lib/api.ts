import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface ChannelStats {
  subscriber_count: number;
  view_count: number;
  video_count: number;
  recorded_at: string;
}

export interface Prediction {
  predicted_growth_rate: number;
  confidence_score: number | null;
  feature_subscriber_growth_rate: number | null;
  feature_view_growth_rate: number | null;
  feature_upload_frequency: number | null;
  feature_engagement_rate: number | null;
  feature_trend_score: number | null;
  feature_news_count: number | null;
  feature_news_sentiment: number | null;
  created_at: string;
}

export interface Channel {
  id: number;
  channel_id: string;
  name: string;
  description: string | null;
  thumbnail_url: string | null;
  latest_stats: ChannelStats | null;
  latest_prediction: Prediction | null;
  created_at: string;
}

export interface ChannelDetail extends Channel {
  stats_history: ChannelStats[];
  predictions_history: Prediction[];
}

export interface News {
  id: number;
  channel_id: number;
  channel_name: string | null;
  title: string;
  url: string;
  source: string | null;
  thumbnail_url: string | null;
  category: string | null;
  published_at: string | null;
  created_at: string;
}

export interface NewsListResponse {
  news: News[];
  total: number;
  page: number;
  per_page: number;
}

export interface RankingEntry {
  rank: number;
  channel: Channel;
  predicted_growth_rate: number;
  confidence_score: number | null;
}

export interface RankingResponse {
  rankings: RankingEntry[];
  updated_at: string;
}

export interface YouTubeSearchResult {
  channel_id: string;
  name: string;
  description: string | null;
  thumbnail_url: string | null;
  subscriber_count: number | null;
}

// API Functions
export async function getRanking(limit: number = 50): Promise<RankingResponse> {
  const response = await api.get<RankingResponse>(`/api/ranking?limit=${limit}`);
  return response.data;
}

export async function getChannel(channelId: string): Promise<ChannelDetail> {
  const response = await api.get<ChannelDetail>(`/api/channels/${channelId}`);
  return response.data;
}

export async function getNews(
  page: number = 1,
  perPage: number = 20,
  category?: string,
  channelId?: string
): Promise<NewsListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: perPage.toString(),
  });
  if (category) params.append("category", category);
  if (channelId) params.append("channel_id", channelId);

  const response = await api.get<NewsListResponse>(`/api/news?${params}`);
  return response.data;
}

export async function searchYouTubeChannels(
  query: string,
  limit: number = 10
): Promise<YouTubeSearchResult[]> {
  const response = await api.get<YouTubeSearchResult[]>(
    `/api/search/youtube?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  return response.data;
}

export async function addChannel(channelId: string): Promise<Channel> {
  const response = await api.post<Channel>("/api/channels", {
    channel_id: channelId,
  });
  return response.data;
}
