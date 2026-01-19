"use client";

import { useState, useEffect } from "react";
import { getRanking, RankingResponse } from "@/lib/api";
import RankingCard from "@/components/RankingCard";

export default function HomePage() {
  const [ranking, setRanking] = useState<RankingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRanking() {
      try {
        const data = await getRanking(50);
        setRanking(data);
      } catch (err) {
        setError("ランキングの取得に失敗しました");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchRanking();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="card inline-block px-8 py-6">
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="page-title">成長予測ランキング</h1>
        <p className="page-description">
          半年後の登録者増加率を予測し、成長が期待されるYouTuberをランキング
        </p>
        {ranking && (
          <p className="text-xs text-gray-400 mt-2">
            最終更新: {new Date(ranking.updated_at).toLocaleString("ja-JP")}
          </p>
        )}
      </div>

      {ranking && ranking.rankings.length > 0 ? (
        <div className="space-y-3">
          {ranking.rankings.map((entry) => (
            <RankingCard key={entry.channel.channel_id} entry={entry} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="card inline-block px-8 py-6">
            <p className="text-gray-500">まだランキングデータがありません</p>
            <p className="text-gray-400 text-sm mt-2">
              検索ページからYouTuberを追加してください
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
