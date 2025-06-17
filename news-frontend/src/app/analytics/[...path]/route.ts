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
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  
  // Build the analytics path from the dynamic segments
  const analyticsPath = params.path.join('/');
  const targetUrl = `${backendUrl}/analytics/${analyticsPath}?${searchParams.toString()}`;
  
  try {
    console.log(`Proxying analytics request to: ${targetUrl}`);
    
    const res = await fetch(targetUrl, { 
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });
    
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
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  
  const analyticsPath = params.path.join('/');
  const targetUrl = `${backendUrl}/analytics/${analyticsPath}?${searchParams.toString()}`;
  
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