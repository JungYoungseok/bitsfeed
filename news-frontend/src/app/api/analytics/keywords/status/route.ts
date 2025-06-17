import { NextResponse } from 'next/server';

export async function GET() {
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  const targetUrl = `${backendUrl}/analytics/keywords/status`;
  
  try {
    console.log(`Proxying status request to: ${targetUrl}`);
    
    const res = await fetch(targetUrl, { 
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Status proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch status data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 