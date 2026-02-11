/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['i.ytimg.com', 'img.youtube.com'],
    },
    async rewrites() {
        return [
            {
                source: '/api/backend/:path*',
                destination: 'http://localhost:8000/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
