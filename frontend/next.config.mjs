/** @type {import('next').NextConfig} */

const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

const nextConfig = {
  /**
   * Proxy API calls through Vercel (same origin) so the browser avoids CORS.
   * Requires NEXT_PUBLIC_API_URL at build time (your Railway HTTPS URL).
   */
  async rewrites() {
    if (!backendUrl) {
      return [];
    }
    return [
      {
        source: "/api-proxy/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
