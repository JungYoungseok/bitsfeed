"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface MysqlTestData {
  status: string;
  test_message_count: number;
  latest_messages: Array<{
    message_id: string;
    title: string;
    source: string;
    content: string;
    received_at: string;
    test_metadata: string;
  }>;
}

export default function MysqlDataPage() {
  const [mysqlTestData, setMysqlTestData] = useState<MysqlTestData | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // MySQL 테스트 데이터 가져오기 (프록시 API 사용)
  const fetchMysqlData = async () => {
    try {
      setError(null);
      const response = await fetch("/api/mysql-test");
      if (response.ok) {
        const data = await response.json();
        setMysqlTestData(data);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(`HTTP Error: ${response.status} - ${errorData.error || response.statusText}`);
      }
    } catch (error) {
      console.error("MySQL data fetch error:", error);
      setError("네트워크 오류로 데이터를 불러올 수 없습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  // 페이지 로드 시 데이터 가져오기
  useEffect(() => {
    fetchMysqlData();
  }, []);

  // 실시간 새로고침
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchMysqlData, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Kafka 테스트 실행
  const handleKafkaTest = async () => {
    try {
      const response = await fetch("http://localhost:8000/kafka-test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ Kafka 테스트 시작됨!\n${result.message || 'Producer가 30초간 메시지를 전송합니다.'}\n\n상세 정보:\n- 지속시간: ${result.details?.duration}\n- 간격: ${result.details?.interval}\n- 예상 메시지: ${result.details?.expected_messages}`);
        
        // 테스트 시작 후 자동 새로고침 시작
        setAutoRefresh(true);
        fetchMysqlData();
        
        // 35초 후 자동 새로고침 중지
        setTimeout(() => {
          setAutoRefresh(false);
        }, 35000);
        
      } else {
        alert("❌ Kafka 테스트 시작 실패");
      }
    } catch (error) {
      console.error("Kafka test error:", error);
      alert("❌ 네트워크 오류로 테스트를 시작할 수 없습니다.");
    }
  };

  if (isLoading) {
    return (
      <main className="max-w-6xl mx-auto p-6">
        <div className="text-center py-16">
          <div className="text-xl text-gray-600">🔄 MySQL 데이터를 불러오는 중...</div>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-800">🗄️ MySQL 테스트 데이터</h1>
          <Link 
            href="/"
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium text-sm"
          >
            ← 메인으로
          </Link>
        </div>
        <p className="text-gray-600">Kafka 테스트로 생성된 MySQL 레코드를 실시간으로 모니터링합니다.</p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={handleKafkaTest}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center gap-2"
        >
          🚀 새 Kafka 테스트 실행
        </button>
        <button
          onClick={fetchMysqlData}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium flex items-center gap-2"
        >
          🔄 데이터 새로고침
        </button>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-6 py-3 rounded-lg transition-colors font-medium flex items-center gap-2 ${
            autoRefresh 
              ? 'bg-red-500 text-white hover:bg-red-600' 
              : 'bg-green-500 text-white hover:bg-green-600'
          }`}
        >
          {autoRefresh ? '⏸️ 자동 새로고침 중지' : '▶️ 자동 새로고침 시작'}
        </button>
      </div>

      {/* Auto Refresh Status */}
      {autoRefresh && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 text-green-700">
            <span className="animate-pulse">🔄</span>
            <span className="font-medium">실시간 업데이트 중... (3초마다 자동 새로고침)</span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="text-red-700">
            ❌ <strong>오류:</strong> {error}
          </div>
        </div>
      )}

      {/* Data Display */}
      {mysqlTestData ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {mysqlTestData.test_message_count}
              </div>
              <div className="text-sm text-gray-600">총 테스트 메시지</div>
            </div>
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {mysqlTestData.status === 'connected' ? '✅' : '❌'}
              </div>
              <div className="text-sm text-gray-600">MySQL 연결 상태</div>
            </div>
            <div className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {mysqlTestData.latest_messages?.length || 0}
              </div>
              <div className="text-sm text-gray-600">표시된 최신 메시지</div>
            </div>
          </div>

          {/* Latest Messages Table */}
          {mysqlTestData.latest_messages && mysqlTestData.latest_messages.length > 0 && (
            <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
              <div className="bg-gray-100 px-6 py-4 border-b">
                <h2 className="text-xl font-semibold text-gray-700">📊 최신 테스트 메시지</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">메시지 ID</th>
                      <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">제목</th>
                      <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">소스</th>
                      <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">처리 시간</th>
                      <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">메타데이터</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mysqlTestData.latest_messages.map((message, index: number) => (
                      <tr key={index} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                        <td className="px-6 py-4 text-sm text-blue-600 font-mono">
                          {message.message_id}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-800 max-w-md">
                          <div className="truncate" title={message.title}>
                            {message.title}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {message.source}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(message.received_at).toLocaleString('ko-KR')}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <details className="cursor-pointer">
                            <summary className="text-blue-600 hover:text-blue-800">
                              📄 메타데이터
                            </summary>
                            <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                              {JSON.stringify(JSON.parse(message.test_metadata), null, 2)}
                            </pre>
                          </details>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty State */}
          {(!mysqlTestData.latest_messages || mysqlTestData.latest_messages.length === 0) && (
            <div className="bg-white rounded-lg border shadow-sm p-12 text-center">
              <div className="text-gray-500 text-lg mb-4">📭 표시할 테스트 메시지가 없습니다</div>
              <button
                onClick={handleKafkaTest}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                🚀 Kafka 테스트 실행하기
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg border shadow-sm p-12 text-center">
          <div className="text-gray-500 text-lg">데이터를 불러올 수 없습니다</div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-12 pt-6 border-t border-gray-200 text-center">
        <p className="text-xs text-gray-500">
          🗄️ MySQL Test Data Viewer | 
          <span className="ml-2">실시간 Kafka 테스트 레코드 모니터링</span>
        </p>
      </div>
    </main>
  );
}