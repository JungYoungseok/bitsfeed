import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type'); // 'viz' or 'analytics'
  const path = searchParams.get('path') || 'dashboard';
  
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  
  if (!type) {
    return NextResponse.json({ error: 'Missing type parameter' }, { status: 400 });
  }
  
  const targetUrl = `${backendUrl}/${type}/${path}`;
  
  try {
    console.log(`Proxying ${type} request to: ${targetUrl}`);
    
    const res = await fetch(targetUrl, { 
      cache: 'no-store',
      headers: {
        'Accept': 'text/html,application/json',
      }
    });
    
    const contentType = res.headers.get('content-type');
    
    if (contentType?.includes('text/html')) {
      const html = await res.text();
      return new Response(html, {
        status: res.status,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
        },
      });
    } else {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error(`API /${type} proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch ${type} data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type'); // 'viz' or 'analytics'
  const path = searchParams.get('path') || '';
  
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';
  
  if (!type) {
    return NextResponse.json({ error: 'Missing type parameter' }, { status: 400 });
  }
  
  const targetUrl = `${backendUrl}/${type}/${path}`;
  
  try {
    console.log(`Proxying ${type} POST request to: ${targetUrl}`);
    
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
    console.error(`API /${type} POST proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to proxy ${type} POST request`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 