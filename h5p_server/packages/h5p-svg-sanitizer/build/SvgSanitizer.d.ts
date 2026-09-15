import { FileSanitizerResult, H5PFileBuffer, IFileSanitizer } from '@lumieducation/h5p-server';
export default class SvgSanitizer implements IFileSanitizer {
    readonly name: string;
    sanitize(file: string, originalFilename?: string): Promise<FileSanitizerResult>;
    /**
     * Sanitizes an in-memory SVG buffer. Replaces `file.data` with the
     * sanitized buffer in place.
     */
    sanitizeBuffer(file: H5PFileBuffer): Promise<FileSanitizerResult>;
    private sanitizeSvgString;
    private isSvgFile;
}
