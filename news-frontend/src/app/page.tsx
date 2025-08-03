"use client";

import { useEffect, useState } from "react";
import { NewsItem } from "@/types/news";
import Image from "next/image";
import Link from "next/link";

export default function HomePage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isKafkaTestRunning, setIsKafkaTestRunning] = useState(false);

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

  const handleKafkaTest = async () => {
    setIsKafkaTestRunning(true);
    try {
      // 프록시 API 호출 (Production 환경 대응)
      const response = await fetch("/api/kafka-test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ Kafka 테스트 시작됨!\n${result.message || 'Producer가 30초간 메시지를 전송합니다.'}\n\n상세 정보:\n- 지속시간: ${result.details?.duration}\n- 간격: ${result.details?.interval}\n- 예상 메시지: ${result.details?.expected_messages}\n\n💡 MySQL 데이터는 별도 페이지에서 확인하세요!`);
      } else {
        alert("❌ Kafka 테스트 시작 실패");
      }
    } catch (error) {
      console.error("Kafka test error:", error);
      alert("❌ 네트워크 오류로 테스트를 시작할 수 없습니다.");
    } finally {
      // 30초 후 버튼 활성화
      setTimeout(() => {
        setIsKafkaTestRunning(false);
      }, 30000);
    }
  };

  return (
    <main className="max-w-3xl mx-auto p-6">
      {/* Header - 타이틀만 깔끔하게 */}
      <div className="flex items-center gap-4 mb-4">
        <Image
          src="/datadog-bits.png"
          alt="Datadog Bits"
          width={40}
          height={40}
        />
        <h1 className="text-3xl font-bold text-purple-700">Datadog 뉴스 피드</h1>
      </div>
      
      {/* Service Buttons - 별도 행에 배치 */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Link
          href="/realtime-test.html"
          target="_blank"
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          🔄 실시간 통신 테스트
        </Link>
        <Link
          href="/api/analytics/viz/dashboard"
          target="_blank"
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          🔍 키워드 분석
        </Link>
        <Link
          href="/api/analytics/viz/simple"
          target="_blank"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          📊 간단 차트
        </Link>
        <Link
          href="/api/consumer/status"
          target="_blank"
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          🔧 Consumer 상태
        </Link>
        <Link
          href="/api/dotnet/health"
          target="_blank"
          className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          🚀 .NET Health
        </Link>
        <Link
          href="/api/dotnet/users"
          target="_blank"
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          👥 .NET Users
        </Link>
        <button
          onClick={handleKafkaTest}
          disabled={isKafkaTestRunning}
          className={`px-4 py-2 text-white rounded-lg transition-colors font-medium text-sm flex items-center gap-2 ${
            isKafkaTestRunning 
              ? 'bg-gray-500 cursor-not-allowed' 
              : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
        >
          {isKafkaTestRunning ? '🔄 테스트 중...' : '🚀 Kafka 테스트'}
        </button>
        <Link
          href="/mysql-data"
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm flex items-center gap-2"
        >
          🗄️ MySQL 데이터 보기
        </Link>
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
          // no-dd-sa
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

            {/* ✅ 한글 요약 */}
            {item.summary_ko && (
              <p className="text-sm text-gray-800 mb-2">
                <strong>요약:</strong> {item.summary_ko}
              </p>
            )}

            {/* ✅ 시장 영향 */}
            {item.impact_ko && (
              <p className="text-sm text-gray-600">
                <strong>시장 영향:</strong> {item.impact_ko}
              </p>
            )}

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
      


      {/* Version info for workflow testing */}
      <div className="mt-8 pt-4 border-t border-gray-200 text-center">
                <p className="text-xs text-gray-500">
          🚀 Datadog News Feed v2024.1.30 | Frontend Service | Build Test 🔧 |
          <span className="ml-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
            ✅ Active
          </span>
        </p>
      </div>
    </main>
  );
}
