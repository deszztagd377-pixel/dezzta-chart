import assert from 'node:assert/strict';
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

await withBundle({
  'assets/app.js': 'const firebase = { apiKey: "AIzaSyPublicClientConfig", authDomain: "example.firebaseapp.com" };',
}, async (directory) => {
  assert.deepEqual(await scanFrontendBundle(directory), []);
});

await withBundle({
  'assets/app.js': 'const credential = "-----BEGIN PRIVATE KEY-----";',
}, async (directory) => {
  const findings = await scanFrontendBundle(directory);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].pattern, 'private-key PEM block');
  assert.equal(findings[0].file, 'assets/app.js');
});

await withBundle({
  'nested/app.js': 'const tokenName = "DATABENTO_API_KEY";',
}, async (directory) => {
  const findings = await scanFrontendBundle(directory);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].pattern, 'backend-only credential identifier');
});

await assert.rejects(
  () => scanFrontendBundle(path.join(os.tmpdir(), 'dezzta-nonexistent-bundle-directory')),
);
