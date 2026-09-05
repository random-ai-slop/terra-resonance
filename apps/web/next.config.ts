import type { NextConfig } from 'next';

const basePath = process.env.TERRA_BASE_PATH ?? '';
if (basePath && !/^\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*$/.test(basePath)) {
  throw new Error('TERRA_BASE_PATH must be empty or a path such as /terra-resonance without a trailing slash.');
}

const nextConfig: NextConfig = {
  output: 'export',
  basePath,
  trailingSlash: true,
  env: { NEXT_PUBLIC_BASE_PATH: basePath },
};

export default nextConfig;
