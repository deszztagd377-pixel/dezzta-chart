import { readFileSync } from 'node:fs';

const [auditPath, dependencyTreePath] = process.argv.slice(2);
if (!auditPath) {
  throw new Error('Usage: node report-npm-audit.mjs <audit-json> [npm-ls-json]');
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`Unable to read ${label} JSON: ${error.message}`);
  }
}

const audit = readJson(auditPath, 'npm audit');
const vulnerabilities = audit.vulnerabilities && typeof audit.vulnerabilities === 'object'
  ? audit.vulnerabilities
  : {};
const summary = audit.metadata?.vulnerabilities ?? {};
console.log(
  `[temporary test dependency audit] total=${summary.total ?? Object.keys(vulnerabilities).length}`
  + ` critical=${summary.critical ?? 0} high=${summary.high ?? 0}`
  + ` moderate=${summary.moderate ?? 0} low=${summary.low ?? 0}`,
);

for (const [name, finding] of Object.entries(vulnerabilities)) {
  const via = (finding.via ?? []).map((entry) => {
    if (typeof entry === 'string') return entry;
    const range = entry.range ? ` ${entry.range}` : '';
    return `${entry.name ?? 'unknown'}${range}`;
  }).join('; ');
  console.log(
    `[temporary test dependency audit] ${String(finding.severity ?? 'unknown').toUpperCase()}`
    + ` package=${name} direct=${Boolean(finding.isDirect)}`
    + ` range=${finding.range ?? 'unknown'}`
    + ` fix=${JSON.stringify(finding.fixAvailable ?? null)}`
    + ` via=${via || 'not supplied'}`,
  );
}

if (audit.error) {
  console.log(`[temporary test dependency audit] npm audit error: ${audit.error.summary ?? audit.error.code ?? 'unspecified'}`);
}

if (dependencyTreePath) {
  const tree = readJson(dependencyTreePath, 'npm dependency tree');
  let undiciCount = 0;
  function visit(node, parentPath = '') {
    for (const [name, dependency] of Object.entries(node?.dependencies ?? {})) {
      const dependencyPath = parentPath
        ? `${parentPath}/node_modules/${name}`
        : `node_modules/${name}`;
      if (name === 'undici') {
        undiciCount += 1;
        console.log(
          `[temporary test dependency tree] ${dependencyPath}@${dependency.version ?? 'unknown'}`,
        );
      }
      visit(dependency, dependencyPath);
    }
  }
  visit(tree);
  console.log(`[temporary test dependency tree] undici_instances=${undiciCount}`);
}
