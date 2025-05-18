// src/app/api/hello/crawl/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${backendUrl}/hello`, { cache: 'no-store' });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    console.error('API /hello error:', err);
    return NextResponse.json({ error: 'Failed to get hello from News API' }, { status: 500 });
  }
}
