"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import {
  getChannels,
  searchYouTubeChannels,
  addChannel,
  deleteChannel,
  Channel,
  YouTubeSearchResult,
} from "@/lib/api";

export default function ChannelsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<YouTubeSearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [addingChannel, setAddingChannel] = useState<string | null>(null);
  const [deletingChannel, setDeletingChannel] = useState<string | null>(null);

  // ページネーション用
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalChannels, setTotalChannels] = useState(0);
  const perPage = 50;

  // 登録済みチャンネル内検索用
  const [filterQuery, setFilterQuery] = useState("");

  useEffect(() => {
    fetchChannels(currentPage);
  }, [currentPage]);

  async function fetchChannels(page: number = 1) {
    setLoading(true);
    try {
      const data = await getChannels(page, perPage);
      setChannels(data.channels);
      setTotalPages(data.total_pages);
      setTotalChannels(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const results = await searchYouTubeChannels(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error(err);
      alert("検索に失敗しました");
    } finally {
      setSearching(false);
    }
  }

  async function handleAddChannel(channelId: string) {
    setAddingChannel(channelId);
    try {
      await addChannel(channelId);
      await fetchChannels(currentPage);
      setSearchResults((prev) =>
        prev.filter((r) => r.channel_id !== channelId)
      );
    } catch (err: any) {
      if (err.response?.status !== 400) {
        alert("追加に失敗しました");
      }
    } finally {
      setAddingChannel(null);
    }
  }

  async function handleDeleteChannel(channelId: string) {
    if (!confirm("このチャンネルを削除しますか？")) return;

    setDeletingChannel(channelId);
    try {
      await deleteChannel(channelId);
      await fetchChannels(currentPage);
    } catch (err) {
      console.error(err);
      alert("削除に失敗しました");
    } finally {
      setDeletingChannel(null);
    }
  }

  const formatNumber = (num: number | null): string => {
    if (num === null) return "非公開";
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  };

  const registeredIds = new Set(channels.map((c) => c.channel_id));

  // フィルター適用
  const filteredChannels = filterQuery
    ? channels.filter(
        (c) =>
          c.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
          c.channel_id.toLowerCase().includes(filterQuery.toLowerCase())
      )
    : channels;

  // ページネーションUI
  const PaginationControls = () =>
    totalPages > 1 ? (
      <div className="flex items-center justify-center gap-2">
        <button
          onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
          disabled={currentPage === 1}
          className="px-3 py-1 rounded border border-gray-300 text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          前へ
        </button>
        <span className="text-sm text-gray-600">
          {currentPage} / {totalPages} ページ
        </span>
        <button
          onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
          disabled={currentPage === totalPages}
          className="px-3 py-1 rounded border border-gray-300 text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          次へ
        </button>
      </div>
    ) : null;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">チャンネル管理</h1>

      {/* Search Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4">チャンネルを追加</h2>
        <form onSubmit={handleSearch} className="flex gap-4 mb-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="YouTuberを検索..."
            className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
          />
          <button
            type="submit"
            disabled={searching || !searchQuery.trim()}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            {searching ? "検索中..." : "検索"}
          </button>
        </form>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="space-y-3">
            {searchResults.map((result) => (
              <div
                key={result.channel_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  {result.thumbnail_url ? (
                    <Image
                      src={result.thumbnail_url}
                      alt={result.name}
                      width={40}
                      height={40}
                      className="rounded-full"
                    />
                  ) : (
                    <div className="w-10 h-10 bg-gray-200 rounded-full" />
                  )}
                  <div>
                    <div className="font-medium">{result.name}</div>
                    <div className="text-sm text-gray-500">
                      登録者: {formatNumber(result.subscriber_count)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleAddChannel(result.channel_id)}
                  disabled={
                    addingChannel === result.channel_id ||
                    registeredIds.has(result.channel_id)
                  }
                  className={`px-4 py-1 rounded text-sm font-medium transition-colors ${
                    registeredIds.has(result.channel_id)
                      ? "bg-gray-200 text-gray-500 cursor-default"
                      : addingChannel === result.channel_id
                      ? "bg-gray-200 text-gray-500"
                      : "bg-purple-600 text-white hover:bg-purple-700"
                  }`}
                >
                  {registeredIds.has(result.channel_id)
                    ? "登録済み"
                    : addingChannel === result.channel_id
                    ? "追加中..."
                    : "追加"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Registered Channels */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            登録済みチャンネル ({totalChannels}件)
          </h2>
        </div>

        {/* 検索とページネーション（上部） */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-4">
          <input
            type="text"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="チャンネル名・IDで絞り込み..."
            className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
          />
          <PaginationControls />
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">読み込み中...</div>
        ) : channels.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            登録されているチャンネルはありません
          </div>
        ) : filteredChannels.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            該当するチャンネルがありません
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {filteredChannels.map((channel) => (
                <div
                  key={channel.channel_id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {channel.thumbnail_url ? (
                      <Image
                        src={channel.thumbnail_url}
                        alt={channel.name}
                        width={48}
                        height={48}
                        className="rounded-full"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-gray-200 rounded-full" />
                    )}
                    <div>
                      <div className="font-medium">{channel.name}</div>
                      <div className="text-sm text-gray-500">
                        ID: {channel.channel_id}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteChannel(channel.channel_id)}
                    disabled={deletingChannel === channel.channel_id}
                    className="px-4 py-1 rounded text-sm font-medium bg-red-100 text-red-600 hover:bg-red-200 transition-colors disabled:opacity-50"
                  >
                    {deletingChannel === channel.channel_id ? "削除中..." : "削除"}
                  </button>
                </div>
              ))}
            </div>

            {/* ページネーション（下部） */}
            <div className="mt-6">
              <PaginationControls />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
