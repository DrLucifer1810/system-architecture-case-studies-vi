/**
 * Cloudflare Pages Functions Middleware
 * Demonstrates Zero-Trust Edge Routing, Header Sanitization, and Dynamic Reverse Proxying.
 * Ensures the frontend client never directly accesses internal microservice domains or IPs.
 */

interface Env {
  CORE_API_ORIGIN: string;       // e.g. "https://core-api-internal.svc.cluster.local"
  MARKETING_API_ORIGIN: string;  // e.g. "https://mkt-api-internal.svc.cluster.local"
  EDGE_SHARED_SECRET: string;    // Mutual edge-to-origin authentication secret
}

// Hop-by-hop headers to strip before proxying upstream
const HOP_BY_HOP_HEADERS = [
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "cf-connecting-ip",
  "cf-ipcountry",
];

export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // Pass static assets and client-side single page app routes through directly
  if (!url.pathname.startsWith("/api/")) {
    return next();
  }

  // Determine target microservice based on API route namespace
  let targetOrigin = env.CORE_API_ORIGIN || "https://internal-gateway.local";
  if (url.pathname.startsWith("/api/v1/marketing/")) {
    targetOrigin = env.MARKETING_API_ORIGIN || targetOrigin;
  }

  // Construct upstream target URL
  const upstreamUrl = new URL(url.pathname + url.search, targetOrigin);

  // Clone headers and sanitize hop-by-hop or client-spoofed metadata
  const upstreamHeaders = new Headers(request.headers);
  for (const header of HOP_BY_HOP_HEADERS) {
    upstreamHeaders.delete(header);
  }

  // Inject secure edge validation header for origin mutual trust
  if (env.EDGE_SHARED_SECRET) {
    upstreamHeaders.set("X-Edge-Auth-Secret", env.EDGE_SHARED_SECRET);
  }

  // Ensure origin host matches target service
  upstreamHeaders.set("Host", upstreamUrl.host);
  upstreamHeaders.set("X-Forwarded-Host", url.host);
  upstreamHeaders.set("X-Forwarded-Proto", url.protocol.replace(":", ""));

  try {
    const upstreamResponse = await fetch(upstreamUrl.toString(), {
      method: request.method,
      headers: upstreamHeaders,
      body: request.body,
      redirect: "manual",
    });

    // Return response back to client with sanitized security headers
    const clientHeaders = new Headers(upstreamResponse.headers);
    clientHeaders.set("X-Content-Type-Options", "nosniff");
    clientHeaders.set("X-Frame-Options", "DENY");

    return new Response(upstreamResponse.body, {
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
      headers: clientHeaders,
    });
  } catch (err) {
    return new Response(
      JSON.stringify({
        error: "EDGE_BAD_GATEWAY",
        message: "Upstream internal microservice unavailable",
        timestamp: Date.now(),
      }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
};