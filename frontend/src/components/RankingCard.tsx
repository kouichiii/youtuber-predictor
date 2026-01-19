"use client";

import Link from "next/link";
import Image from "next/image";
import { RankingEntry } from "@/lib/api";

interface RankingCardProps {
  entry: RankingEntry;
}

export default function RankingCard({ entry }: RankingCardProps) {
  const { rank, channel, predicted_growth_rate, confidence_score } = entry;

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  };

  const getGrowthColor = (rate: number): string => {
    if (rate >= 50) return "text-primary-600";
    if (rate >= 20) return "text-primary-500";
    if (rate >= 0) return "text-primary-400";
    return "text-gray-500";
  };

  const getRankDisplay = (rank: number) => {
    if (rank === 1) {
      return (
        <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center shadow-sm">
          <span className="text-white font-bold text-lg">1</span>
        </div>
      );
    }
    if (rank === 2) {
      return (
        <div className="w-10 h-10 bg-gradient-to-br from-gray-300 to-gray-400 rounded-full flex items-center justify-center shadow-sm">
          <span className="text-white font-bold text-lg">2</span>
        </div>
      );
    }
    if (rank === 3) {
      return (
        <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-600 rounded-full flex items-center justify-center shadow-sm">
          <span className="text-white font-bold text-lg">3</span>
        </div>
      );
    }
    return (
      <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
        <span className="text-gray-500 font-medium text-lg">{rank}</span>
      </div>
    );
  };

  return (
    <Link href={`/channel/${channel.channel_id}`}>
      <div className="card p-4 flex items-center space-x-4">
        {/* Rank Badge */}
        {getRankDisplay(rank)}

        {/* Channel Thumbnail */}
        <div className="flex-shrink-0">
          {channel.thumbnail_url ? (
            <Image
              src={channel.thumbnail_url}
              alt={channel.name}
              width={56}
              height={56}
              className="rounded-full ring-2 ring-gray-100"
            />
          ) : (
            <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center ring-2 ring-gray-100">
              <span className="text-gray-400 text-xl">?</span>
            </div>
          )}
        </div>

        {/* Channel Info */}
        <div className="flex-grow min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{channel.name}</h3>
          <div className="text-sm text-gray-400 flex items-center space-x-3 mt-0.5">
            {channel.latest_stats && (
              <>
                <span className="flex items-center space-x-1">
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                  </svg>
                  <span>{formatNumber(channel.latest_stats.subscriber_count)}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                  <span>{formatNumber(channel.latest_stats.view_count)}</span>
                </span>
              </>
            )}
          </div>
        </div>

        {/* Prediction */}
        <div className="text-right flex-shrink-0">
          <div className={`text-2xl font-bold ${getGrowthColor(predicted_growth_rate)}`}>
            {predicted_growth_rate >= 0 ? "+" : ""}
            {predicted_growth_rate.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-400 mt-0.5">半年後予測</div>
          {confidence_score !== null && (
            <div className="flex items-center justify-end space-x-1 mt-1">
              <div className="w-12 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-400 rounded-full"
                  style={{ width: `${confidence_score * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">
                {(confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
