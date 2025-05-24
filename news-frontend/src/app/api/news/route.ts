// src/app/api/news/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${backendUrl}/news`, { cache: 'no-store' });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    // no-dd-sa
    console.error('API /news error:', err);
    return NextResponse.json({ error: 'Failed to fetch news' }, { status: 500 });
  }
}
