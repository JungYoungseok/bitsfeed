"use client";

import { useEffect, useState } from "react";
import { NewsItem } from "@/types/news";
import Image from "next/image";

export default function HomePage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const pageSize = 5;

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("/api/news", { cache: "no-store" });
      const data = await res.json();
      setNews(data);
    };
    fetchData();
  }, []);

  const isHighlighted = (item: NewsItem) => {
    const published = new Date(item.published);
    const today = new Date();
    const isToday = published.toDateString() === today.toDateString();
    const keywords = ["Datadog", "AI", "acquisition"];
    const containsKeyword = keywords.some((k) =>
      item.title.toLowerCase().includes(k.toLowerCase())
    );
    return isToday || containsKeyword;
  };

  const filtered = news.filter((item) =>
    item.title.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(filtered.length / pageSize);
  const paginated = filtered.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <main className="max-w-3xl mx-auto p-6">
      <div className="flex items-center gap-4 mb-6">
        <Image
          src="/datadog-bits.png"
          alt="Datadog Bits"
          width={40}
          height={40}
        />
        <h1 className="text-3xl font-bold text-purple-700">Datadog 뉴스 피드</h1>
      </div>

      <input
        className="p-2 border border-gray-300 rounded w-full mb-4"
        type="text"
        placeholder="키워드로 뉴스 검색 (예: AI)"
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setCurrentPage(1);
        }}
      />

      <ul className="space-y-4">
        {paginated.map((item, idx) => (
          <li
            key={idx}
            className={`p-4 border rounded-xl shadow-md transition hover:shadow-lg ${
              isHighlighted(item)
                ? "bg-purple-100 border-purple-400"
                : "hover:bg-gray-50"
            }`}
          >
            <p className="text-sm text-gray-500">
              {new Date(item.published).toLocaleString()}
            </p>
            <a
              href={item.link}
              className="text-lg font-semibold text-purple-700 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {item.title}
            </a>
          </li>
        ))}
      </ul>

      <div className="flex gap-4 mt-6 justify-center items-center">
        <button
          onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 border rounded text-purple-700 border-purple-400 hover:bg-purple-100 disabled:opacity-40"
        >
          ◀ 이전
        </button>
        <span className="text-sm text-gray-600">
          페이지 {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 border rounded text-purple-700 border-purple-400 hover:bg-purple-100 disabled:opacity-40"
        >
          다음 ▶
        </button>
      </div>
    </main>
  );
}
