"use client";

import { useState, useEffect } from "react";
import { getNews, NewsListResponse } from "@/lib/api";
import NewsCard from "@/components/NewsCard";

const categories = [
  { id: "", label: "すべて" },
  { id: "collaboration", label: "コラボ" },
  { id: "media", label: "メディア出演" },
  { id: "controversy", label: "炎上" },
  { id: "event", label: "イベント" },
  { id: "other", label: "その他" },
];

export default function NewsPage() {
  const [newsData, setNewsData] = useState<NewsListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [page, setPage] = useState(1);
  const perPage = 20;

  useEffect(() => {
    async function fetchNews() {
      setLoading(true);
      try {
        const data = await getNews(
          page,
          perPage,
          selectedCategory || undefined
        );
        setNewsData(data);
      } catch (err) {
        setError("ニュースの取得に失敗しました");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchNews();
  }, [page, selectedCategory]);

  const handleCategoryChange = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setPage(1);
  };

  const totalPages = newsData ? Math.ceil(newsData.total / perPage) : 0;

  return (
    <div>
      <div className="mb-6">
        <h1 className="page-title">ニュース一覧</h1>
        <p className="page-description">
          YouTuberに関する最新ニュースをカテゴリ別に表示
        </p>
      </div>

      {/* Category Filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => handleCategoryChange(category.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
              selectedCategory === category.id
                ? "bg-primary-600 text-white shadow-sm"
                : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center items-center min-h-[30vh]">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary-600 border-t-transparent"></div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="card inline-block px-8 py-6">
            <p className="text-gray-600">{error}</p>
          </div>
        </div>
      ) : newsData && newsData.news.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {newsData.news.map((news) => (
              <NewsCard key={news.id} news={news} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-4 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-5 py-2.5 rounded-full bg-white shadow-card text-gray-700 font-medium text-sm
                         disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-card-hover transition-all duration-200"
              >
                前へ
              </button>
              <span className="text-gray-500 text-sm">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-5 py-2.5 rounded-full bg-white shadow-card text-gray-700 font-medium text-sm
                         disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-card-hover transition-all duration-200"
              >
                次へ
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <div className="card inline-block px-8 py-6">
            <p className="text-gray-500">ニュースがありません</p>
          </div>
        </div>
      )}
    </div>
  );
}
