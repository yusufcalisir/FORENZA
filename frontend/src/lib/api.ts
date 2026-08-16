/**
 * Resolves the backend API Base URL based on the runtime environment.
 * - In production (Vercel / external domain): routes to live Render backend `https://forenza-backend.onrender.com`.
 * - In local development: routes to `http://127.0.0.1:8000`.
 */
export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
    return "https://forenza-backend.onrender.com";
  }

  if (process.env.NODE_ENV === "production") {
    return "https://forenza-backend.onrender.com";
  }

  return "http://127.0.0.1:8000";
}
