"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const promises_1 = require("fs/promises");
const h5p_server_1 = require("@lumieducation/h5p-server");
const path_1 = require("path");

let DOMPurify;
function getDOMPurify() {
    if (!DOMPurify) {
        try {
            const dompurify_1 = __importDefault(require("dompurify"));
            const jsdom_1 = require("jsdom");
            const window = new jsdom_1.JSDOM('').window;
            DOMPurify = (0, dompurify_1.default)(window);
        } catch (e) {
            console.warn('DOMPurify/JSDOM initialization failed, falling back to basic SVG sanitizer:', e.message);
            DOMPurify = {
                sanitize: (str) => str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            };
        }
    }
    return DOMPurify;
}

class SvgSanitizer {
    name = 'SVG Sanitizer based on dompurify package';
    async sanitize(file, originalFilename) {
        if (!this.isSvgFile((0, path_1.basename)(originalFilename ?? file))) {
            return h5p_server_1.FileSanitizerResult.Ignored;
        }
        const svgString = await (0, promises_1.readFile)(file, 'utf8');
        const sanitizedSvgString = this.sanitizeSvgString(svgString);
        await (0, promises_1.writeFile)(file, sanitizedSvgString, 'utf8');
        return h5p_server_1.FileSanitizerResult.Sanitized;
    }
    /**
     * Sanitizes an in-memory SVG buffer. Replaces `file.data` with the
     * sanitized buffer in place.
     */
    async sanitizeBuffer(file) {
        if (!this.isSvgFile(file.name)) {
            return h5p_server_1.FileSanitizerResult.Ignored;
        }
        if (!file.data) {
            throw new Error('SvgSanitizer.sanitizeBuffer was called without file.data');
        }
        const svgString = file.data.toString('utf8');
        const sanitizedSvgString = this.sanitizeSvgString(svgString);
        file.data = Buffer.from(sanitizedSvgString, 'utf8');
        return h5p_server_1.FileSanitizerResult.Sanitized;
    }
    sanitizeSvgString(svgString) {
        return getDOMPurify().sanitize(svgString, {
            USE_PROFILES: { svg: true }
        });
    }
    // Case-insensitive so e.g. "image.SVG" is sanitized too, not just "image.svg".
    isSvgFile(fileName) {
        return fileName.toLowerCase().endsWith('.svg');
    }
}
exports.default = SvgSanitizer;
//# sourceMappingURL=SvgSanitizer.js.map