'use client';

import { useEffect, useState } from 'react';
import { NewsItem } from '@/types/news';

export default function HomePage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetch(`${apiBaseUrl}/news`)
      .then((res) => res.json())
      .then((data) => {
        setNews(data);
        setLoading(false);
      });
  }, []);

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">📰 Datadog 뉴스 피드</h1>
      <p className="mb-6">
        👉 <a href="/healthcheck" className="text-blue-600 hover:underline">Healthcheck 페이지로 이동</a>
      </p>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="space-y-4">
          {news.map((item, idx) => (
            // no-dd-sa
            <li key={idx} className="p-4 border rounded-lg shadow hover:bg-gray-50">
              <p className="text-sm text-gray-500">{new Date(item.published).toLocaleString()}</p>
              <a
                href={item.link}
                className="text-lg font-semibold text-blue-600 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {item.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
