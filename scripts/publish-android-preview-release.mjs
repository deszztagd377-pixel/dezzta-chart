import { createHash } from 'node:crypto';
import { appendFile, readFile } from 'node:fs/promises';
async function readJson(response, context) {
  let payload;
  try { payload = await response.json(); } catch { throw new Error(context + ': non-JSON GitHub API response'); }
  if (!response.ok) throw new Error(context + ': GitHub API HTTP ' + response.status + ': ' + (payload?.message || 'unknown error'));
  return payload;
}
const headersFor = (token) => ({ Accept: 'application/vnd.github+json', Authorization: 'Bearer ' + token, 'X-GitHub-Api-Version': '2022-11-28' });
export async function publishAndroidPreviewRelease({ repository, token, commitSha, apkPath, fetchImpl = fetch }) {
  if (typeof repository !== 'string' || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository)) throw new TypeError('GITHUB_REPOSITORY must be owner/repository.');
  if (typeof token !== 'string' || token.trim().length < 10) throw new TypeError('A GitHub Actions token is required.');
  if (typeof commitSha !== 'string' || !/^[0-9a-f]{40}$/i.test(commitSha)) throw new TypeError('GITHUB_SHA must be a full 40-character commit SHA.');
  const apk = await readFile(apkPath);
  if (!apk.length) throw new Error('Refusing to publish an empty APK.');
  const sha256 = createHash('sha256').update(apk).digest('hex');
  const tag = 'android-preview-' + commitSha.slice(0, 12).toLowerCase();
  const api = 'https://api.github.com/repos/' + repository;
  const headers = headersFor(token);
  let release;
  const existing = await fetchImpl(api + '/releases/tags/' + tag, { headers });
  if (existing.status === 404) {
    const response = await fetchImpl(api + '/releases', {
      method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tag_name: tag, target_commitish: commitSha,
        name: 'DEZZTA CHART Android Preview ' + commitSha.slice(0, 12),
        draft: false, prerelease: true, make_latest: 'false',
        body: 'Automated versioned Android preview. FRONTEND ONLY: this APK does not bundle or supervise the Python backend or Redis. Sample/demo chart content is not live exchange market data. Not a final production release.',
      }),
    });
    release = await readJson(response, 'Create preview release');
  } else {
    release = await readJson(existing, 'Read preview release');
    if (release.prerelease !== true || release.draft === true) throw new Error('Existing tag is not an already-published preview release.');
    if (Array.isArray(release.assets) && release.assets.length) throw new Error('Immutable preview tag already contains assets; use a new commit.');
  }
  if (typeof release.upload_url !== 'string' || typeof release.html_url !== 'string' || !release.html_url.startsWith('https://github.com/')) {
    throw new Error('GitHub release response is missing a trusted upload or release URL.');
  }
  const uploadBase = release.upload_url.split('{?')[0];
  async function upload(name, bytes, contentType) {
    const url = new URL(uploadBase);
    url.searchParams.set('name', name);
    return readJson(await fetchImpl(url, {
      method: 'POST', headers: { ...headers, 'Content-Type': contentType, 'Content-Length': String(bytes.length) }, body: bytes,
    }), 'Upload release asset ' + name);
  }
  await upload('dezzta-chart.apk', apk, 'application/vnd.android.package-archive');
  await upload('dezzta-chart.apk.sha256', Buffer.from(sha256 + '  dezzta-chart.apk\n'), 'text/plain; charset=utf-8');
  return {
    tagName: tag, releaseUrl: release.html_url,
    apkUrl: 'https://github.com/' + repository + '/releases/download/' + tag + '/dezzta-chart.apk',
    sha256,
  };
}
async function main() {
  const result = await publishAndroidPreviewRelease({
    repository: process.env.GITHUB_REPOSITORY, token: process.env.GITHUB_TOKEN,
    commitSha: process.env.GITHUB_SHA, apkPath: process.env.APK_PATH || 'android/app/build/outputs/apk/debug/app-debug.apk',
  });
  const output = ['release_url=' + result.releaseUrl, 'apk_url=' + result.apkUrl, 'sha256=' + result.sha256].join('\n') + '\n';
  if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, output);
  if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY,
    '## Android preview release published\n\nRelease: ' + result.releaseUrl + '\nAPK: ' + result.apkUrl +
    '\nSHA-256: ' + result.sha256 + '\n\nFrontend-only preview; backend/Redis integration remains unverified.\n');
  process.stdout.write('Published preview APK: ' + result.apkUrl + '\nSHA-256: ' + result.sha256 + '\n');
}
if (process.argv[1] && new URL(import.meta.url).pathname === process.argv[1]) {
  main().catch((error) => {
    process.stderr.write('Android preview release failed: ' + (error instanceof Error ? error.message : 'unknown error') + '\n');
    process.exitCode = 1;
  });
}
