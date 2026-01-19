"use client";

import { News } from "@/lib/api";

interface NewsCardProps {
  news: News;
  showChannel?: boolean;
}

const categoryLabels: Record<string, { label: string; color: string }> = {
  collaboration: { label: "コラボ", color: "bg-blue-50 text-blue-600" },
  media: { label: "メディア出演", color: "bg-purple-50 text-purple-600" },
  controversy: { label: "炎上", color: "bg-primary-50 text-primary-600" },
  event: { label: "イベント", color: "bg-green-50 text-green-600" },
  other: { label: "その他", color: "bg-gray-100 text-gray-600" },
};

export default function NewsCard({ news, showChannel = true }: NewsCardProps) {
  const category = categoryLabels[news.category || "other"] || categoryLabels.other;

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return "";
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "今日";
    if (diffDays === 1) return "昨日";
    if (diffDays < 7) return `${diffDays}日前`;

    return date.toLocaleDateString("ja-JP", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <a
      href={news.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block card overflow-hidden group"
    >
      <div className="p-4">
        <div className="flex items-center space-x-2 mb-2.5">
          <span
            className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${category.color}`}
          >
            {category.label}
          </span>
          {news.published_at && (
            <span className="text-xs text-gray-400">{formatDate(news.published_at)}</span>
          )}
        </div>
        <h3 className="font-medium text-gray-900 line-clamp-2 group-hover:text-primary-600 transition-colors">
          {news.title}
        </h3>
        <div className="flex items-center space-x-3 mt-3 text-sm text-gray-400">
          {showChannel && news.channel_name && (
            <span className="flex items-center space-x-1">
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
              </svg>
              <span className="truncate max-w-[120px]">{news.channel_name}</span>
            </span>
          )}
          {news.source && (
            <span className="flex items-center space-x-1">
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.56-.5-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.56.5.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.498-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clipRule="evenodd" />
              </svg>
              <span>{news.source}</span>
            </span>
          )}
        </div>
      </div>
    </a>
  );
}
