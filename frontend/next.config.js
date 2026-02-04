/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Proxy API requests to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Transpile packages that need it
  transpilePackages: ['recharts', 'react-leaflet'],

  // Ignore TypeScript errors from src/ during migration
  typescript: {
    ignoreBuildErrors: false,
  },
};

export default nextConfig;
