import path from "node:path";
import { loadEnvConfig } from "@next/env";
import type { NextConfig } from "next";

const frontendDir = process.cwd();
const repoRoot = path.resolve(frontendDir, "..");

loadEnvConfig(frontendDir);
loadEnvConfig(repoRoot);

const nextConfig: NextConfig = {
  output: "standalone",
  reactCompiler: true,
};

export default nextConfig;
