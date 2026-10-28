import type { NextConfig } from "next";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Image Docker : un serveur Node autonome (voir Dockerfile).
  output: "standalone",
  // Le navigateur parle à l'API via /api sur la même origine que le front :
  // le cookie de session et le jeton CSRF de Django fonctionnent sans CORS.
  // En production, le proxy HTTPS (Caddyfile) envoie /api directement à l'API.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/api/:path*` }];
  },
};

export default nextConfig;
