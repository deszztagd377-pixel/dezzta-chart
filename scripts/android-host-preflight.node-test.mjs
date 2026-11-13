import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptPath = fileURLToPath(new URL("./android-host-preflight.sh", import.meta.url));

test("Android host preflight is read-only and does not disclose environment values", async () => {
  const source = await readFile(scriptPath, "utf8");
  assert.match(source, /No packages will be installed/);
  assert.match(source, /PRECHECK ONLY/);
  assert.match(source, /"pytest"/);
  assert.match(source, /"cryptography"/);
  assert.doesNotMatch(source, /\b(pkg|apt|apt-get)\s+install\b/);
  assert.doesNotMatch(source, /curl[^\n]*\|\s*(sh|bash)/);
  assert.doesNotMatch(source, /printenv|env\s*$/);
  assert.doesNotMatch(source, /ps\s+aux|ps\s+-ef/);

  const temp = await mkdtemp(join(tmpdir(), "dezzta-android-preflight-"));
  try {
    const bin = join(temp, "bin");
    const home = join(temp, "home");
    await mkdir(bin);
    await mkdir(home);
    const getprop = join(bin, "getprop");
    await writeFile(getprop, '#!/bin/sh\ncase "$1" in\n  ro.product.cpu.abi) echo arm64-v8a ;;\n  ro.build.version.release) echo 15 ;;\nesac\n');
    const chmod = spawnSync("chmod", ["700", getprop]);
    assert.equal(chmod.status, 0);

    const result = spawnSync("sh", [scriptPath], {
      encoding: "utf8",
      env: {
        PATH: bin + ":" + process.env.PATH,
        HOME: home,
        PREFIX: "/data/data/com.termux/files/usr",
        TERMUX_VERSION: "test",
        DEZZTA_PREFLIGHT_SECRET_SENTINEL: "must-never-appear"
      }
    });

    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /arm64-v8a/);
    assert.match(result.stdout, /Android host preflight/);
    assert.match(result.stdout, /PRECHECK ONLY/);
    assert.doesNotMatch(result.stdout, /must-never-appear/);
    assert.doesNotMatch(result.stdout, /DEZZTA_PREFLIGHT_SECRET_SENTINEL/);
  } finally {
    await rm(temp, { recursive: true, force: true });
  }
});
