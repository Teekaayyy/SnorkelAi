#!/usr/bin/env node
// flatten.js — run from anywhere, flattens all files in its parent directory

const fs = require("fs");
const path = require("path");

const SCRIPT_NAME = path.basename(__filename);
const PARENT_DIR = path.resolve(__dirname, "");
const OUTPUT_FILE = path.join(__dirname, "flattened.txt");

// File extensions to include (add/remove as needed)
const EXCLUDE_EXTENSIONS = new Set([
".exe", ".dll", ".bin", ".jpg", ".jpeg", ".png", ".gif", ".bmp",
".zip", ".tar", ".gz", ".7z", ".pdf", ".docx", ".xlsx"
]);

// Folder names to skip entirely
const EXCLUDE_DIRS = new Set([
  "node_modules", ".git", "dist", "build", ".next",
  "coverage", ".turbo", "out",
]);

function collectFiles(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      if (!EXCLUDE_DIRS.has(entry.name)) {
        collectFiles(fullPath, files);
      }
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (!EXCLUDE_EXTENSIONS.has(ext)) {
        files.push(fullPath);
      }
    }
  }
  return files;
}

function flatten() {
  console.log(`📂 Scanning: ${PARENT_DIR}`);

  const files = collectFiles(PARENT_DIR).filter(
    // Exclude this script and the output file itself
    (f) => f !== __filename && f !== OUTPUT_FILE
  );

  if (files.length === 0) {
    console.log("No matching files found.");
    return;
  }

  const out = fs.createWriteStream(OUTPUT_FILE, { encoding: "utf8" });

  out.write(`// ============================================================\n`);
  out.write(`// Flattened output — ${new Date().toISOString()}\n`);
  out.write(`// Source: ${PARENT_DIR}\n`);
  out.write(`// Total files: ${files.length}\n`);
  out.write(`// ============================================================\n\n`);

  for (const filePath of files) {
    const relativePath = path.relative(PARENT_DIR, filePath);
    const separator = "=".repeat(64);

    out.write(`// ${separator}\n`);
    out.write(`// FILE: ${relativePath}\n`);
    out.write(`// ${separator}\n\n`);

    try {
      const content = fs.readFileSync(filePath, "utf8");
      out.write(content);
      // Ensure newline between files
      if (!content.endsWith("\n")) out.write("\n");
    } catch (err) {
      out.write(`// [ERROR reading file: ${err.message}]\n`);
    }

    out.write("\n\n");
  }

  out.end(() => {
    console.log(`\n✅ Done — ${files.length} files written to:`);
    console.log(`   ${OUTPUT_FILE}`);
  });
}

flatten();