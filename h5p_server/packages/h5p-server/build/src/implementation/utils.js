"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generalizedSanitizeFilename = generalizedSanitizeFilename;
const path_1 = __importDefault(require("path"));
/**
 * Sanitizes a filename. Removes invalid characters and shortens to the max
 * length.
 * @param filename
 * @param invalidCharacterRegex
 * @param maxLength
 * @returns the sanitized filename
 */
function generalizedSanitizeFilename(filename, invalidCharacterRegex, maxLength) {
    // First remove all invalid characters.
    // We keep / and \ as the "filename" can be a relative path with
    // directories. We don't use the sanitize-filename package, as it
    // also removes directory separators.
    let cleanedFilename = filename.replace(invalidCharacterRegex, '');
    // Should the filename only contain the extension now (because all
    // characters of the basename were invalid), we add a generic filename.
    let extension = path_1.default.posix.extname(cleanedFilename);
    let basename = path_1.default.posix.basename(cleanedFilename, extension);
    const dirname = path_1.default.posix.dirname(cleanedFilename);
    if (extension === '') {
        extension = basename;
        basename = 'file';
        cleanedFilename = `${dirname}/${basename}${extension}`;
    }
    // Shorten the filename if it is too long.
    const numberOfCharactersToCut = cleanedFilename.length - maxLength;
    if (numberOfCharactersToCut < 0) {
        return cleanedFilename;
    }
    const finalBasenameLength = Math.max(1, basename.length - numberOfCharactersToCut);
    return `${dirname}/${basename.substr(0, finalBasenameLength)}${extension}`;
}
//# sourceMappingURL=utils.js.map