import { NewsItem } from "@/types/news";

export default async function HomePage() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://datadog-news-crawler-service:8000";

  const res = await fetch(`${apiBaseUrl}/news`, {
    // 중요: SSR fetch로 하기 위해 다음 옵션 필수
    cache: "no-store",
  });

  const news: NewsItem[] = await res.json();

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">📰 Datadog 뉴스 피드</h1>
      <ul className="space-y-4">
        {news.map((item, idx) => (
          <li key={idx} className="p-4 border rounded-lg shadow hover:bg-gray-50">
            <p className="text-sm text-gray-500">
              {new Date(item.published).toLocaleString()}
            </p>
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
    </main>
  );
}