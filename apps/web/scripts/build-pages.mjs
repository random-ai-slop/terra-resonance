import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const basePath = process.env.TERRA_BASE_PATH ?? '/terra-resonance';
if (basePath && !/^\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*$/.test(basePath)) {
  throw new Error('TERRA_BASE_PATH must be empty or a slash-prefixed path without a trailing slash.');
}
// Keep a failed build from accidentally republishing an older export.
rmSync(path.join(root, 'dist'), { recursive: true, force: true });
const build = spawnSync(process.execPath, ['node_modules/vinext/dist/cli.js', 'build'], {
  cwd: root,
  env: { ...process.env, TERRA_DEPLOY_TARGET: 'pages', TERRA_BASE_PATH: basePath },
  stdio: 'inherit',
});
if (build.error) throw build.error;
if (build.status !== 0) process.exit(build.status ?? 1);
// Vinext physically prefixes exports. Pages itself mounts this directory at basePath.
const source = path.join(root, 'dist/client', basePath.replace(/^\//, ''));
const destination = path.join(root, 'dist/pages');
for (const required of ['index.html', 'data/prem-modes.json', 'data/lessons.json']) {
  if (!existsSync(path.join(source, required))) throw new Error(`Missing Pages export: ${required}`);
}
mkdirSync(destination, { recursive: true });
cpSync(source, destination, { recursive: true });
writeFileSync(path.join(destination, '.nojekyll'), '');
const html = readFileSync(path.join(destination, 'index.html'), 'utf8');
for (const match of html.matchAll(/(?:src|href)="([^"#?]+)(?:[?#][^"]*)?"/g)) {
  const url = match[1];
  if (!url.startsWith('/') || url.startsWith('//')) continue;
  if (!url.startsWith(`${basePath}/`)) throw new Error(`Asset escapes Pages base path: ${url}`);
  const relative = url.slice(basePath.length + 1);
  if (relative && !existsSync(path.join(destination, relative))) throw new Error(`Missing static asset: ${url}`);
}
writeFileSync(path.join(destination, 'deployment.json'), JSON.stringify({
  base_path: basePath,
  source_commit: process.env.GITHUB_SHA ?? null,
  package_version: JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8')).version,
}, null, 2) + '\n');
console.log(`Pages export ready: ${destination} (mount ${basePath || '/'})`);
