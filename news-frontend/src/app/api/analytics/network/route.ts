import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  
  const targetUrl = `${backendUrl}/analytics/keywords/network?${searchParams.toString()}`;
  
  try {
    console.log(`Proxying network request to: ${targetUrl}`);
    
    const res = await fetch(targetUrl, { 
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Network proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch network data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 