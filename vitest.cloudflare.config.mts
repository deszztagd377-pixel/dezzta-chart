import { cloudflareTest } from "@cloudflare/vitest-plugin";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    cloudflareTest({
      wrangler: {
        configPath: "./cloudflare/wrangler.jsonc",
      },
      miniflare: {
        bindings: {
          SYNTHETIC_PROOF_TOKEN: "synthetic-proof-test-token-000000000000000000000000",
        },
      },
    }),
  ],
  test: {
    include: ["cloudflare/proof/worker.durable-object.runtime.mjs"],
    testTimeout: 15_000,
    hookTimeout: 15_000,
    fileParallelism: false,
  },
});
