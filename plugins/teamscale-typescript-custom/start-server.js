#!/usr/bin/env node

const { execSync, fork } = require("node:child_process");
const { join } = require("node:path");
const { existsSync } = require("node:fs");

const serverDir = join(__dirname, "server");
const distServer = join(serverDir, "dist", "server.js");
const nodeModules = join(serverDir, "node_modules");
const tsc = join(nodeModules, ".bin", "tsc");

// Disable TLS verification (matching Python plugin's verify_ssl=False)
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

// Install dependencies if node_modules doesn't exist
if (!existsSync(nodeModules)) {
  execSync("npm install", { cwd: serverDir, stdio: "pipe" });
}

// Only generate and compile if the built server doesn't exist yet
if (!existsSync(distServer)) {
  // Generate the TypeScript API client from the OpenAPI spec
  execSync("./generate-client.sh", { cwd: serverDir, stdio: "pipe" });

  // Compile TypeScript using the locally installed tsc
  execSync(tsc, { cwd: serverDir, stdio: "pipe" });
}

// Run the compiled server
const child = fork(distServer, {
  cwd: serverDir,
  stdio: "inherit",
  env: process.env,
});

child.on("exit", (code) => process.exit(code ?? 0));
