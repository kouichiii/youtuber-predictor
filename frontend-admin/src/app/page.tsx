"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getChannels, Channel } from "@/lib/api";

export default function DashboardPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getChannels();
        setChannels(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        管理ダッシュボード
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Stats Cards */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">登録チャンネル数</div>
          <div className="text-3xl font-bold text-purple-600 mt-2">
            {loading ? "..." : channels.length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">ステータス</div>
          <div className="text-lg font-medium text-green-600 mt-2">
            正常稼働中
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">公開アプリ</div>
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="text-lg font-medium text-blue-600 hover:underline mt-2 block"
          >
            localhost:3000
          </a>
        </div>
      </div>

      {/* Quick Actions */}
      <h2 className="text-xl font-bold text-gray-900 mb-4">クイックアクション</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          href="/channels"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <h3 className="font-semibold text-lg">チャンネル管理</h3>
          <p className="text-gray-500 text-sm mt-1">
            YouTuberを検索して追加・削除
          </p>
        </Link>

        <Link
          href="/jobs"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <h3 className="font-semibold text-lg">ジョブ実行</h3>
          <p className="text-gray-500 text-sm mt-1">
            データ収集・予測・学習を実行
          </p>
        </Link>
      </div>
    </div>
  );
}
