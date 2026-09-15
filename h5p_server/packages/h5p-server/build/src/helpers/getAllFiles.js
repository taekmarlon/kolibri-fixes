"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAllFiles = getAllFiles;
const promises_1 = require("fs/promises");
const path_1 = require("path");
/**
 * Recursively lists all files (not directories) under dirname. Paths are
 * built by concatenating dirname verbatim (not path.join, which would
 * normalize away any `..` segments) with each file's relative path, since
 * several callers strip the literal `dirname` string off the front of each
 * result.
 */
async function getAllFiles(dirname) {
    const base = dirname.endsWith(path_1.sep) ? dirname : `${dirname}${path_1.sep}`;
    const entries = await (0, promises_1.readdir)(base, { withFileTypes: true });
    const files = await Promise.all(entries.map((entry) => {
        const fullPath = `${base}${entry.name}`;
        return entry.isDirectory() ? getAllFiles(fullPath) : [fullPath];
    }));
    return files.flat();
}
//# sourceMappingURL=getAllFiles.js.map