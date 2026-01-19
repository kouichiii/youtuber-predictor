import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Channel {
  id: number;
  channel_id: string;
  name: string;
  description: string | null;
  thumbnail_url: string | null;
  created_at: string;
}

export interface YouTubeSearchResult {
  channel_id: string;
  name: string;
  description: string | null;
  thumbnail_url: string | null;
  subscriber_count: number | null;
}

export interface JobStatus {
  status: "idle" | "running" | "completed" | "error";
  message: string;
  progress?: number;
  started_at?: string;
  completed_at?: string;
}

// API Functions
export interface PaginatedChannels {
  channels: Channel[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export async function getChannels(page: number = 1, perPage: number = 50): Promise<PaginatedChannels> {
  const skip = (page - 1) * perPage;
  const response = await api.get<Channel[]>(`/api/channels?skip=${skip}&limit=${perPage}`);

  // 総数を取得するために別リクエスト
  const countResponse = await api.get<{ total: number }>("/api/channels/count");
  const total = countResponse.data.total;

  return {
    channels: response.data,
    total,
    page,
    per_page: perPage,
    total_pages: Math.ceil(total / perPage),
  };
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

export async function deleteChannel(channelId: string): Promise<void> {
  await api.delete(`/api/channels/${channelId}`);
}

export async function runDataCollection(): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/api/admin/collect");
  return response.data;
}

export async function runPrediction(): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/api/admin/predict");
  return response.data;
}

export async function runTraining(): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/api/admin/train");
  return response.data;
}

export async function getJobStatus(): Promise<JobStatus> {
  const response = await api.get<JobStatus>("/api/admin/status");
  return response.data;
}
