// src/app/api/hello/crawl/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const backendUrl = process.env.NEWS_API_URL || 'http://localhost:8000';

  try {
    // 클라이언트에서 보낸 body를 그대로 백엔드에 전달
    const body = await req.json();

    const res = await fetch(`${backendUrl}/crawl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    // no-dd-sa
    console.error('API /crawl POST error:', err);
    return NextResponse.json({ error: 'Failed to post crawl request' }, { status: 500 });
  }
}
