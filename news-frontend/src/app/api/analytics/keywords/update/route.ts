import { NextResponse } from 'next/server';

export async function POST() {
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  const targetUrl = `${backendUrl}/analytics/keywords/update`;
  
  try {
    console.log(`Proxying update request to: ${targetUrl}`);
    
    const res = await fetch(targetUrl, { 
      method: 'POST',
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`Update proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to update keywords`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 