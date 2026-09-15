import { readFile, writeFile } from 'fs/promises';

import {
    FileSanitizerResult,
    H5PFileBuffer,
    IFileSanitizer
} from '@lumieducation/h5p-server';
import { basename } from 'path';

let DOMPurify: any;
async function getDOMPurify() {
    if (!DOMPurify) {
        try {
            const createDOMPurify = (await import('dompurify')).default;
            const { JSDOM } = await import('jsdom');
            const window = new JSDOM('').window;
            DOMPurify = createDOMPurify(window as any);
        } catch (e: any) {
            console.warn('DOMPurify/JSDOM initialization failed, falling back to basic SVG sanitizer:', e.message);
            DOMPurify = {
                sanitize: (str: string) => str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            };
        }
    }
    return DOMPurify;
}

export default class SvgSanitizer implements IFileSanitizer {
    readonly name: string = 'SVG Sanitizer based on dompurify package';

    async sanitize(
        file: string,
        originalFilename?: string
    ): Promise<FileSanitizerResult> {
        if (!this.isSvgFile(basename(originalFilename ?? file))) {
            return FileSanitizerResult.Ignored;
        }

        const svgString = await readFile(file, 'utf8');
        const sanitizedSvgString = await this.sanitizeSvgString(svgString);
        await writeFile(file, sanitizedSvgString, 'utf8');

        return FileSanitizerResult.Sanitized;
    }

    /**
     * Sanitizes an in-memory SVG buffer. Replaces `file.data` with the
     * sanitized buffer in place.
     */
    async sanitizeBuffer(file: H5PFileBuffer): Promise<FileSanitizerResult> {
        if (!this.isSvgFile(file.name)) {
            return FileSanitizerResult.Ignored;
        }
        if (!file.data) {
            throw new Error(
                'SvgSanitizer.sanitizeBuffer was called without file.data'
            );
        }

        const svgString = file.data.toString('utf8');
        const sanitizedSvgString = await this.sanitizeSvgString(svgString);
        file.data = Buffer.from(sanitizedSvgString, 'utf8');

        return FileSanitizerResult.Sanitized;
    }

    private async sanitizeSvgString(svgString: string): Promise<string> {
        const purify = await getDOMPurify();
        return purify.sanitize(svgString, {
            USE_PROFILES: { svg: true }
        });
    }

    // Case-insensitive so e.g. "image.SVG" is sanitized too, not just "image.svg".
    private isSvgFile(fileName: string): boolean {
        return fileName.toLowerCase().endsWith('.svg');
    }
}
