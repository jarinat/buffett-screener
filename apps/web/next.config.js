/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Environment variables to expose to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Output standalone for Docker optimization
  output: 'standalone',

  // Configure allowed image domains if needed
  images: {
    domains: [],
  },

  // Disable x-powered-by header for security
  poweredByHeader: false,
}

module.exports = nextConfig
