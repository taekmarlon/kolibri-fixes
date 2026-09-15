/**
 * Recursively lists all files (not directories) under dirname. Paths are
 * built by concatenating dirname verbatim (not path.join, which would
 * normalize away any `..` segments) with each file's relative path, since
 * several callers strip the literal `dirname` string off the front of each
 * result.
 */
export declare function getAllFiles(dirname: string): Promise<string[]>;
