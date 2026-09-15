import NodeClam from 'clamscan';
import { H5PFileBuffer, IFileMalwareScanner, MalwareScanResult } from '@lumieducation/h5p-server';
export type ClamAVScannerOptions = {
    clamdServiceEnabled: boolean;
};
/**
 * A light wrapper calling the ClamAV scanner to scan files for malware. It
 * utilizes the `clamscan` package.
 *
 * Note: You need to have a ClamAV running somewhere to use this and you must
 * update ClamAVs virus definitions regularly yourself from outside this class.
 */
export default class ClamAVScanner implements IFileMalwareScanner {
    private scanner;
    private readonly options;
    /**
     * We have no public constructor, as we need to initialize the ClamAV
     * scanner asynchronously.
     * @param scanner
     * @param clamdServiceEnabled true if the resolved scanner is the clamd
     * daemon AND a socket/host/port connection to it was actually
     * configured, which together are required for scanning a stream
     * directly; false if it is the clamscan binary, or a clamdscan that
     * would fall back to shelling out to the local binary because no
     * daemon connection was configured, both of which require a file on
     * disk.
     */
    private constructor();
    readonly name: string;
    /**
     * Factory method to create a new instance of ClamAVScanner. You can't use
     * the constructor directly, as we need to initialize the ClamAV scanner
     * asynchronously.
     * @param clamavOptions the options as required by the ClamAV scanner (see
     * https://www.npmjs.com/package/clamscan). This is simply passed through to
     * ClamAV, expect for the parameters `removeInfected`, `quarantineInfected`
     * and `scanRecursively`: these are set to false to make sure the behavior
     * is as @lumieducation/h5p-server expects it.
     */
    static create(clamavOptions?: NodeClam.Options): Promise<ClamAVScanner>;
    /**
     * Gets the ClamAV options from environment variables (CLAMSCAN_* and
     * CLAMDSCAN_*). See the docs for what the options do.
     */
    private static getEnvVarOptions;
    scan(file: string): Promise<{
        result: MalwareScanResult;
        viruses?: string;
    }>;
    /**
     * Scans an in-memory buffer for malware. If the underlying scanner is
     * the clamd daemon, the buffer is streamed directly; otherwise it is
     * written to a temporary file first, as the clamscan binary requires a
     * file on disk.
     */
    scanBuffer(file: H5PFileBuffer): Promise<{
        result: MalwareScanResult;
        viruses?: string;
    }>;
    private scanBufferWithTempFile;
    private buildScanResult;
}
