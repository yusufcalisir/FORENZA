import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const payload = await req.json();

    // Potential backend endpoints
    const candidates = [
      process.env.BACKEND_INTERNAL_URL,
      process.env.NEXT_PUBLIC_API_URL,
      "http://127.0.0.1:8000",
      "http://localhost:8000",
      "https://forenza-backend.onrender.com",
    ].filter(Boolean) as string[];

    let lastError: any = null;

    for (const baseUrl of candidates) {
      try {
        const cleanBase = baseUrl.replace(/\/+$/, "");
        const targetUrl = `${cleanBase}/api/v1/forensic/terminal/comprehensive`;

        const res = await fetch(targetUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          cache: "no-store",
        });

        if (res.ok) {
          const data = await res.json();
          return NextResponse.json({ ...data, _proxiedVia: cleanBase }, { status: 200 });
        }
      } catch (err) {
        lastError = err;
      }
    }

    return NextResponse.json(
      {
        error: "Failed to connect to FastAPI backend terminal service",
        detail: lastError ? String(lastError) : "All candidate URLs failed",
      },
      { status: 502 }
    );
  } catch (error: any) {
    return NextResponse.json(
      { error: "Invalid recalculation request payload", detail: error?.message },
      { status: 400 }
    );
  }
}
