import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { publishAndroidPreviewRelease } from './publish-android-preview-release.mjs';
const repository = 'deszztagd377-pixel/dezzta-chart';
const token = 'test-token-value-never-logged';
const commitSha = 'a'.repeat(40);
const json = (value, status = 200) => new Response(JSON.stringify(value), { status });
test('publishes immutable preview APK and SHA-256 sidecar', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dezzta-release-'));
  try {
    const apkPath = join(dir, 'app-debug.apk');
    const bytes = Buffer.from('test-only-apk-binary');
    await writeFile(apkPath, bytes);
    const calls = [];
    const fetchImpl = async (url, options = {}) => {
      const parsed = new URL(url); calls.push({ parsed, options });
      if (parsed.pathname.endsWith('/releases/tags/android-preview-aaaaaaaaaaaa')) return json({ message: 'Not Found' }, 404);
      if (parsed.pathname.endsWith('/releases')) {
        const body = JSON.parse(options.body);
        assert.equal(body.prerelease, true);
        assert.equal(body.draft, false);
        assert.match(body.body, /FRONTEND ONLY/);
        return json({
          html_url: 'https://github.com/deszztagd377-pixel/dezzta-chart/releases/tag/android-preview-aaaaaaaaaaaa',
          upload_url: 'https://uploads.github.com/repos/owner/repo/releases/1/assets{?name,label}',
          prerelease: true, draft: false, assets: [],
        }, 201);
      }
      assert.ok(parsed.pathname.endsWith('/assets'));
      return json({ id: calls.length }, 201);
    };
    const result = await publishAndroidPreviewRelease({ repository, token, commitSha, apkPath, fetchImpl });
    const hash = createHash('sha256').update(bytes).digest('hex');
    assert.equal(result.sha256, hash);
    assert.equal(result.apkUrl, 'https://github.com/deszztagd377-pixel/dezzta-chart/releases/download/android-preview-aaaaaaaaaaaa/dezzta-chart.apk');
    const assets = calls.filter((call) => call.parsed.pathname.endsWith('/assets'));
    assert.equal(assets.length, 2);
    assert.deepEqual(Buffer.from(assets[0].options.body), bytes);
    assert.equal(Buffer.from(assets[1].options.body).toString(), hash + '  dezzta-chart.apk\n');
  } finally { await rm(dir, { recursive: true, force: true }); }
});
test('refuses to replace assets on an existing preview tag', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dezzta-release-'));
  try {
    const apkPath = join(dir, 'app-debug.apk');
    await writeFile(apkPath, Buffer.from('test'));
    let upload = false;
    const fetchImpl = async (url) => {
      if (String(url).includes('/releases/tags/')) return json({
        html_url: 'https://github.com/deszztagd377-pixel/dezzta-chart/releases/tag/android-preview-aaaaaaaaaaaa',
        upload_url: 'https://uploads.github.com/assets{?name,label}',
        prerelease: true, draft: false, assets: [{ name: 'dezzta-chart.apk' }],
      });
      upload = true; return json({});
    };
    await assert.rejects(publishAndroidPreviewRelease({ repository, token, commitSha, apkPath, fetchImpl }), /Immutable preview tag/);
    assert.equal(upload, false);
  } finally { await rm(dir, { recursive: true, force: true }); }
});
test('rejects invalid repository, commit SHA and empty APK before network', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dezzta-release-'));
  try {
    const apkPath = join(dir, 'empty.apk');
    await writeFile(apkPath, Buffer.alloc(0));
    let called = false;
    const fetchImpl = async () => { called = true; return json({}); };
    await assert.rejects(publishAndroidPreviewRelease({ repository: 'bad', token, commitSha, apkPath, fetchImpl }), /GITHUB_REPOSITORY/);
    await assert.rejects(publishAndroidPreviewRelease({ repository, token, commitSha: 'bad', apkPath, fetchImpl }), /GITHUB_SHA/);
    await assert.rejects(publishAndroidPreviewRelease({ repository, token, commitSha, apkPath, fetchImpl }), /empty APK/);
    assert.equal(called, false);
  } finally { await rm(dir, { recursive: true, force: true }); }
});
