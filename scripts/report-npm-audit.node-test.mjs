import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const reporterPath = fileURLToPath(new URL('./report-npm-audit.mjs', import.meta.url));

async function runReporter(audit, tree = { dependencies: {} }) {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'dezzta-npm-audit-'));
  try {
    const auditPath = path.join(directory, 'audit.json');
    const treePath = path.join(directory, 'tree.json');
    await writeFile(auditPath, JSON.stringify(audit), 'utf8');
    await writeFile(treePath, JSON.stringify(tree), 'utf8');
    return spawnSync(process.execPath, [reporterPath, auditPath, treePath], {
      encoding: 'utf8',
    });
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

const cleanAudit = {
  vulnerabilities: {},
  metadata: { vulnerabilities: { total: 0, critical: 0, high: 0, moderate: 0, low: 0, info: 0 } },
};

test('accepts a complete clean audit and reports the resolved dependency tree', async () => {
  const result = await runReporter(cleanAudit, {
    dependencies: { miniflare: { version: '4.20260730.0', dependencies: { undici: { version: '7.30.1' } } } },
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /total=0 critical=0 high=0/);
  assert.match(result.stdout, /node_modules\/miniflare\/node_modules\/undici@7\.30\.1/);
});

test('blocks HIGH advisories even when the metadata summary is inconsistent', async () => {
  const result = await runReporter({
    vulnerabilities: {
      undici: { severity: 'high', isDirect: false, via: ['test advisory'] },
    },
    metadata: { vulnerabilities: { total: 0, critical: 0, high: 0, moderate: 0, low: 0, info: 0 } },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /BLOCKED/);
});

test('blocks CRITICAL advisories', async () => {
  const result = await runReporter({
    vulnerabilities: {
      example: { severity: 'critical', isDirect: true, via: ['test advisory'] },
    },
    metadata: { vulnerabilities: { total: 1, critical: 1, high: 0, moderate: 0, low: 0, info: 0 } },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /HIGH\/CRITICAL/);
});

test('allows LOW-only advisories while keeping the audit complete', async () => {
  const result = await runReporter({
    vulnerabilities: {
      example: { severity: 'low', isDirect: true, via: ['test advisory'] },
    },
    metadata: { vulnerabilities: { total: 1, critical: 0, high: 0, moderate: 0, low: 1, info: 0 } },
  });
  assert.equal(result.status, 0, result.stderr);
});

test('blocks an npm dependency tree with unresolved problems', async () => {
  const result = await runReporter(cleanAudit, {
    problems: ['missing: undici@7.30.1'],
    dependencies: { undici: { version: '7.30.1' } },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /dependency-tree problems/);
});

test('blocks npm audit transport or registry errors', async () => {
  const result = await runReporter({ ...cleanAudit, error: { code: 'ENETWORK', summary: 'registry unavailable' } });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /registry unavailable/);
});

test('fails closed when the audit summary is missing', async () => {
  const result = await runReporter({ vulnerabilities: {} });
  assert.notEqual(result.status, 0);
});

test('fails closed when the dependency tree is malformed', async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'dezzta-npm-audit-invalid-'));
  try {
    const auditPath = path.join(directory, 'audit.json');
    const treePath = path.join(directory, 'tree.json');
    await writeFile(auditPath, JSON.stringify(cleanAudit), 'utf8');
    await writeFile(treePath, '{invalid', 'utf8');
    const result = spawnSync(process.execPath, [reporterPath, auditPath, treePath], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Unable to read npm dependency tree JSON/);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
