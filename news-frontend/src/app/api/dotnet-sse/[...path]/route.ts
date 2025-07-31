import { NextRequest } from 'next/server';

interface RouteParams {
  params: Promise<{ path: string[] }>;
}

export async function GET(
  request: NextRequest,
  context: RouteParams
) {
  const params = await context.params;
  const { searchParams } = new URL(request.url);
  
  // .NET Core Sample API URL
  const dotnetUrl = process.env.DOTNET_API_URL || 'http://dotnet-sample:5000';

  const dotnetPath = params.path.join('/');
  const targetUrl = `${dotnetUrl}/api/${dotnetPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying .NET SSE request to: ${targetUrl}`);

    // Create a streaming response for Server-Sent Events
    const response = await fetch(targetUrl, {
      headers: {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Return the streaming response
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control',
      },
    });

  } catch (err) {
    console.error(`DotNet SSE proxy error:`, err);
    return new Response(
      `data: {"error": "Failed to fetch .NET SSE data", "details": "${err instanceof Error ? err.message : 'Unknown error'}"}\n\n`,
      {
        status: 500,
        headers: {
          'Content-Type': 'text/event-stream',
        },
      }
    );
  }
}