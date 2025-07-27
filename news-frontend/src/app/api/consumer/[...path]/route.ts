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

  // News Consumer API URL (Kubernetes 서비스명 사용)
  const consumerUrl = process.env.CONSUMER_API_URL || 'http://news-consumer-api:8002';

  const consumerPath = params.path.join('/');
  const targetUrl = `${consumerUrl}/${consumerPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying consumer request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Consumer proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch consumer data`, details: err instanceof Error ? err.message : 'Unknown error' },
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

  // News Consumer API URL (Kubernetes 서비스명 사용)
  const consumerUrl = process.env.CONSUMER_API_URL || 'http://news-consumer-api:8002';

  const consumerPath = params.path.join('/');
  const targetUrl = `${consumerUrl}/${consumerPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying consumer POST request to: ${targetUrl}`);

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
    console.error(`Consumer POST proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to proxy consumer POST request`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 