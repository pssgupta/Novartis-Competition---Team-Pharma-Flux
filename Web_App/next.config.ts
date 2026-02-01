import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  outputFileTracingIncludes: {
    "/**/*": ["./Data_Analysis/**/*"],
    "/api/**/*": ["./Data_Analysis/**/*"],
  },
  // Removed experimental.turbo since we fixed it at the package level
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "zod/v3": "zod",
      "react-native-fetch-blob": false,
      "react-native-fs": false,
      "react-native": false,
    };
    return config;
  },
};

export default nextConfig;
