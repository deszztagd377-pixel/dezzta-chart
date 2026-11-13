import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { scanFrontendBundle } from './check-frontend-bundle-secrets.mjs';

async function withBundle(files, run) {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'dezzta-bundle-scan-'));
  try {
    for (const [name, content] of Object.entries(files)) {
      const target = path.join(directory, name);
      await mkdir(path.dirname(target), { recursive: true });
      await writeFile(target, content, 'utf8');
    }
    await run(directory);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

test('allows public Firebase client configuration', async () => {
  await withBundle({
    'assets/app.js': 'const firebase = { apiKey: "AIzaSyPublicClientConfig", authDomain: "example.firebaseapp.com" };',
  }, async (directory) => {
    assert.deepEqual(await scanFrontendBundle(directory), []);
  });
});

test('detects private key PEM material without returning its contents', async () => {
  await withBundle({
    'assets/app.js': 'const credential = "-----BEGIN PRIVATE KEY-----";',
  }, async (directory) => {
    const findings = await scanFrontendBundle(directory);
    assert.equal(findings.length, 1);
    assert.equal(findings[0].pattern, 'private-key PEM block');
    assert.equal(findings[0].file, 'assets/app.js');
    assert.equal(JSON.stringify(findings).includes('BEGIN PRIVATE KEY'), false);
  });
});

test('detects backend-only credential identifiers', async () => {
  await withBundle({
    'nested/app.js': 'const tokenName = "DATABENTO_API_KEY";',
  }, async (directory) => {
    const findings = await scanFrontendBundle(directory);
    assert.equal(findings.length, 1);
    assert.equal(findings[0].pattern, 'backend-only credential identifier');
  });
});

test('scans TypeScript and TSX source files before bundling', async () => {
  await withBundle({
    'components/Chart.tsx': 'const credential = "ghp_123456789012345678901234";',
  }, async (directory) => {
    const findings = await scanFrontendBundle(directory);
    assert.equal(findings.length, 1);
    assert.equal(findings[0].file, 'components/Chart.tsx');
    assert.equal(findings[0].pattern, 'GitHub personal access token');
  });
});

test('fails closed when the bundle directory does not exist', async () => {
  await assert.rejects(
    () => scanFrontendBundle(path.join(os.tmpdir(), 'dezzta-nonexistent-bundle-directory')),
  );
});
