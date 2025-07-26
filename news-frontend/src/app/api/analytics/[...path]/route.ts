import { NextRequest, NextResponse } from 'next/server';

interface RouteParams {
  params: Promise<{ path: string[] }>;
}

export async function GET(
  request: NextRequest,
  context: RouteParams
) {
  const params = await context.params;
  const { searchParams } = new URL(request.url);
  
  // 🚀 새로운 Analytics 서비스 URL
  const analyticsUrl = process.env.ANALYTICS_API_URL || 'http://localhost:8001';

  const analyticsPath = params.path.join('/');
  
  // viz 경로는 직접 연결, analytics 경로는 /analytics/ prefix 추가
  const isVizPath = params.path[0] === 'viz';
  const targetUrl = isVizPath 
    ? `${analyticsUrl}/${analyticsPath}?${searchParams.toString()}`
    : `${analyticsUrl}/analytics/${analyticsPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying analytics request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      cache: 'no-store',
      headers: {
        'Accept': isVizPath ? 'text/html' : 'application/json',
      }
    });

    // HTML 응답 (visualization)인 경우
    if (isVizPath || res.headers.get('content-type')?.includes('text/html')) {
      const html = await res.text();
      return new NextResponse(html, {
        status: res.status,
        headers: {
          'Content-Type': 'text/html',
        },
      });
    }

    // JSON 응답 (analytics API)인 경우
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Analytics proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch analytics data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  context: RouteParams
) {
  const params = await context.params;
  const { searchParams } = new URL(request.url);
  
  // 🚀 새로운 Analytics 서비스 URL
  const analyticsUrl = process.env.ANALYTICS_API_URL || 'http://localhost:8001';

  const analyticsPath = params.path.join('/');
  
  // viz 경로는 직접 연결, analytics 경로는 /analytics/ prefix 추가
  const isVizPath = params.path[0] === 'viz';
  const targetUrl = isVizPath 
    ? `${analyticsUrl}/${analyticsPath}?${searchParams.toString()}`
    : `${analyticsUrl}/analytics/${analyticsPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying analytics POST request to: ${targetUrl}`);

    const body = await request.text();

    const res = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body,
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Analytics POST proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to proxy analytics POST request`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 