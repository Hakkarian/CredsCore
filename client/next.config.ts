import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produce a self-contained `.next/standalone` server for the Docker runner stage.
  output: "standalone",
};

export default nextConfig;
