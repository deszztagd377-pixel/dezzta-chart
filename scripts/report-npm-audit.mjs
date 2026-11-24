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
if (!audit || typeof audit !== 'object' || Array.isArray(audit)) {
  throw new Error('Invalid npm audit JSON: expected an object.');
}

const vulnerabilities = audit.vulnerabilities;
const summary = audit.metadata?.vulnerabilities;
const severityNames = ['critical', 'high', 'moderate', 'low', 'info'];
const observed = Object.fromEntries(severityNames.map((severity) => [severity, 0]));
let malformedFindings = false;

if (!vulnerabilities || typeof vulnerabilities !== 'object' || Array.isArray(vulnerabilities)) {
  console.error('[temporary test dependency audit] BLOCKED: vulnerability map is missing or malformed.');
  process.exitCode = 1;
} else {
  for (const [name, finding] of Object.entries(vulnerabilities)) {
    const severity = String(finding?.severity ?? '').toLowerCase();
    if (!severityNames.includes(severity)) {
      malformedFindings = true;
    } else {
      observed[severity] += 1;
    }
    const via = (finding?.via ?? []).map((entry) => {
      if (typeof entry === 'string') return entry;
      const range = entry.range ? ` ${entry.range}` : '';
      return `${entry.name ?? 'unknown'}${range}`;
    }).join('; ');
    console.log(
      `[temporary test dependency audit] ${severity.toUpperCase() || 'UNKNOWN'}`
      + ` package=${name} direct=${Boolean(finding?.isDirect)}`
      + ` range=${finding?.range ?? 'unknown'}`
      + ` fix=${JSON.stringify(finding?.fixAvailable ?? null)}`
      + ` via=${via || 'not supplied'}`,
    );
  }
}

if (!summary || typeof summary !== 'object' || Array.isArray(summary)) {
  console.error('[temporary test dependency audit] BLOCKED: npm audit severity summary is missing.');
  process.exitCode = 1;
} else {
  for (const severity of severityNames) {
    const value = summary[severity];
    if (!Number.isSafeInteger(value) || value < 0) {
      console.error(`[temporary test dependency audit] BLOCKED: invalid ${severity} count in audit summary.`);
      process.exitCode = 1;
    }
  }
  const total = summary.total;
  const severityTotal = severityNames.reduce((sum, severity) => sum + (Number.isSafeInteger(summary[severity]) ? summary[severity] : 0), 0);
  if (!Number.isSafeInteger(total) || total < 0 || total !== severityTotal) {
    console.error('[temporary test dependency audit] BLOCKED: audit total does not match severity counts.');
    process.exitCode = 1;
  }
}

if (malformedFindings) {
  console.error('[temporary test dependency audit] BLOCKED: one or more findings have an unknown severity.');
  process.exitCode = 1;
}

const summaryCritical = Number.isSafeInteger(summary?.critical) ? summary.critical : 0;
const summaryHigh = Number.isSafeInteger(summary?.high) ? summary.high : 0;
const blockingAdvisories = Math.max(summaryCritical, observed.critical)
  + Math.max(summaryHigh, observed.high);
console.log(
  `[temporary test dependency audit] total=${summary?.total ?? 'unknown'}`
  + ` critical=${summary?.critical ?? 'unknown'} high=${summary?.high ?? 'unknown'}`
  + ` moderate=${summary?.moderate ?? 'unknown'} low=${summary?.low ?? 'unknown'}`,
);

if (audit.error) {
  console.error(`[temporary test dependency audit] BLOCKED: npm audit error: ${audit.error.summary ?? audit.error.code ?? 'unspecified'}`);
  process.exitCode = 1;
}

if (blockingAdvisories > 0) {
  console.error(
    `[temporary test dependency audit] BLOCKED: ${blockingAdvisories} HIGH/CRITICAL advisories remain.`,
  );
  process.exitCode = 1;
}

if (dependencyTreePath) {
  const tree = readJson(dependencyTreePath, 'npm dependency tree');
  if (!tree || typeof tree !== 'object' || Array.isArray(tree)) {
    throw new Error('Invalid npm dependency tree JSON: expected an object.');
  }
  if (tree.problems !== undefined && !Array.isArray(tree.problems)) {
    throw new Error('Invalid npm dependency tree JSON: problems must be an array.');
  }
  const problems = tree.problems ?? [];
  const undiciProblems = problems.filter((problem) => (
    typeof problem === 'string' ? problem : JSON.stringify(problem)
  ).toLowerCase().includes('undici'));
  if (undiciProblems.length > 0) {
    console.error(
      '[temporary test dependency tree] BLOCKED: npm ls reported Undici-specific problems: '
      + JSON.stringify(undiciProblems),
    );
    process.exitCode = 1;
  } else if (tree.error || problems.length > 0) {
    console.log(
      '[temporary test dependency tree] Non-Undici npm ls diagnostics ignored for this scoped check: '
      + JSON.stringify({ error: tree.error ?? null, problems }),
    );
  }
  if (!tree.dependencies || typeof tree.dependencies !== 'object' || Array.isArray(tree.dependencies)) {
    throw new Error('Invalid npm dependency tree JSON: root dependencies are missing.');
  }
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
  if (undiciCount === 0) {
    console.error('[temporary test dependency tree] BLOCKED: no resolved Undici package was found.');
    process.exitCode = 1;
  }
}
