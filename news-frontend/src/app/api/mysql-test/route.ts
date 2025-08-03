import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // News Consumer API URL (환경변수 또는 기본값 사용)
    const consumerUrl = process.env.CONSUMER_API_URL || 'http://news-consumer:8002';
    const targetUrl = `${consumerUrl}/mysql-test`;

    console.log(`Proxying MySQL test request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!res.ok) {
      console.error(`MySQL test proxy error: ${res.status} ${res.statusText}`);
      return NextResponse.json(
        { 
          error: `Consumer service returned ${res.status}`, 
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
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });

  } catch (err) {
    console.error(`MySQL test proxy error:`, err);
    return NextResponse.json(
      { 
        error: `Failed to fetch MySQL test data`, 
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
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}