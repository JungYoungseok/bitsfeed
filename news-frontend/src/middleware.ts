import { NextRequest, NextResponse } from "next/server";

export const config = {
  matcher: ["/((?!_next/static|favicon.ico).*)"],
};

export function middleware(request: NextRequest) {
  const log = {
    level: "info",
    timestamp: new Date().toISOString(),
    message: "access log",
    method: request.method,
    url: request.nextUrl.href,
    ip: request.headers.get("x-forwarded-for") ?? "unknown",
    userAgent: request.headers.get("user-agent") ?? "unknown",
  };

  console.log(JSON.stringify(log)); 

  return NextResponse.next();
}
