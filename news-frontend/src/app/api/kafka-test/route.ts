import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // Backend API URL (환경변수 또는 기본값 사용)
    const backendUrl = process.env.NEWS_API_URL || 'http://datadog-news-crawler:8000';
    const targetUrl = `${backendUrl}/kafka-test`;

    console.log(`Proxying Kafka test request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    });

    if (!res.ok) {
      console.error(`Kafka test proxy error: ${res.status} ${res.statusText}`);
      return NextResponse.json(
        { 
          error: `Backend service returned ${res.status}`, 
          details: res.statusText 
        },
        { status: res.status }
      );
    }

    const data = await res.json();
    
    // CORS 헤더 추가 (필요한 경우)
    return NextResponse.json(data, { 
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });

  } catch (err) {
    console.error(`Kafka test proxy error:`, err);
    return NextResponse.json(
      { 
        error: `Failed to start Kafka test`, 
        details: err instanceof Error ? err.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

// OPTIONS 메소드 처리 (CORS preflight)
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}