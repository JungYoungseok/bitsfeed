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
  
  // .NET Core Sample API URL
  const dotnetUrl = process.env.DOTNET_API_URL || 'http://dotnet-sample:5000';

  const dotnetPath = params.path.join('/');
  const targetUrl = `${dotnetUrl}/api/${dotnetPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying .NET request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`DotNet proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to fetch .NET data`, details: err instanceof Error ? err.message : 'Unknown error' },
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
  
  const dotnetUrl = process.env.DOTNET_API_URL || 'http://dotnet-sample:5000';

  const dotnetPath = params.path.join('/');
  const targetUrl = `${dotnetUrl}/api/${dotnetPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying .NET POST request to: ${targetUrl}`);

    const body = await request.text();

    const res = await fetch(targetUrl, {
      method: 'POST',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: body,
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`DotNet POST proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to post .NET data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  context: RouteParams
) {
  const params = await context.params;
  const { searchParams } = new URL(request.url);
  
  const dotnetUrl = process.env.DOTNET_API_URL || 'http://dotnet-sample:5000';

  const dotnetPath = params.path.join('/');
  const targetUrl = `${dotnetUrl}/api/${dotnetPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying .NET PUT request to: ${targetUrl}`);

    const body = await request.text();

    const res = await fetch(targetUrl, {
      method: 'PUT',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: body,
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`DotNet PUT proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to update .NET data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  context: RouteParams
) {
  const params = await context.params;
  const { searchParams } = new URL(request.url);
  
  const dotnetUrl = process.env.DOTNET_API_URL || 'http://dotnet-sample:5000';

  const dotnetPath = params.path.join('/');
  const targetUrl = `${dotnetUrl}/api/${dotnetPath}?${searchParams.toString()}`;

  try {
    console.log(`Proxying .NET DELETE request to: ${targetUrl}`);

    const res = await fetch(targetUrl, {
      method: 'DELETE',
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`DotNet DELETE proxy error:`, err);
    return NextResponse.json(
      { error: `Failed to delete .NET data`, details: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 