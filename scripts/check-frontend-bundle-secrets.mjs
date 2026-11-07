import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const SECRET_PATTERNS = [
  { name: 'private-key PEM block', expression: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/ },
  { name: 'service-account private_key field', expression: /"private_key"\s*:\s*"-----BEGIN/ },
  { name: 'AWS access key identifier', expression: /\bAKIA[0-9A-Z]{16}\b/ },
  { name: 'GitHub personal access token', expression: /\bgh[pousr]_[A-Za-z0-9]{20,}\b/ },
  { name: 'Stripe live secret key', expression: /\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b/ },
  { name: 'backend-only credential identifier', expression: /\b(?:DATABENTO_API_KEY|MARKET_DATA_WS_TOKEN|FIREBASE_PRIVATE_KEY|GOOGLE_APPLICATION_CREDENTIALS)\b/ },
];

const SCANNED_EXTENSIONS = new Set(['.js', '.mjs', '.cjs', '.html', '.css', '.json']);

async function collectFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await collectFiles(fullPath));
    else if (entry.isFile() && SCANNED_EXTENSIONS.has(path.extname(entry.name))) files.push(fullPath);
  }
  return files;
}

export async function scanFrontendBundle(directory) {
  const files = await collectFiles(directory);
  if (files.length === 0) throw new Error('No frontend bundle files found to scan.');
  const findings = [];
  for (const file of files) {
    const content = await readFile(file, 'utf8');
    for (const pattern of SECRET_PATTERNS) {
      if (pattern.expression.test(content)) {
        findings.push({ file: path.relative(directory, file), pattern: pattern.name });
      }
    }
  }
  return findings;
}

async function main() {
  const directory = path.resolve(process.argv[2] || 'dist');
  let findings;
  try {
    findings = await scanFrontendBundle(directory);
  } catch (error) {
    process.stderr.write('Frontend bundle scan failed: ' + error.message + '\n');
    process.exitCode = 1;
    return;
  }
  if (findings.length > 0) {
    process.stderr.write('Potential server-side credential material found in frontend bundle:\n');
    for (const finding of findings) {
      process.stderr.write('- ' + finding.file + ': ' + finding.pattern + '\n');
    }
    process.exitCode = 1;
    return;
  }
  const count = (await collectFiles(directory)).length;
  process.stdout.write('Frontend bundle secret scan passed (' + count + ' files checked).\n');
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
