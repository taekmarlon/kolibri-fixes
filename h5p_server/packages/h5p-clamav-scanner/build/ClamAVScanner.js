"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const clamscan_1 = __importDefault(require("clamscan"));
const stream_1 = require("stream");
const tmp_promise_1 = require("tmp-promise");
const promises_1 = require("fs/promises");
const path_1 = require("path");
const ts_deepmerge_1 = require("ts-deepmerge");
const h5p_server_1 = require("@lumieducation/h5p-server");
const helpers_1 = require("./helpers");
const log = new h5p_server_1.Logger('ClamAVScanner');
/**
 * A light wrapper calling the ClamAV scanner to scan files for malware. It
 * utilizes the `clamscan` package.
 *
 * Note: You need to have a ClamAV running somewhere to use this and you must
 * update ClamAVs virus definitions regularly yourself from outside this class.
 */
class ClamAVScanner {
    scanner;
    options;
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
    constructor(scanner, options) {
        this.scanner = scanner;
        this.options = options;
        log.debug('initialize');
    }
    name = 'ClamAV virus scanner';
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
    static async create(clamavOptions) {
        const envVarOptions = ClamAVScanner.getEnvVarOptions();
        // Because of how the clamscan package checks for the presence of the
        // properties in the options object (Object.prototype.hasOwnProperty:
        // "The hasOwnProperty() method returns true if the specified property
        // is a direct property of the object — even if the value is null or
        // undefined."), we have to remove undefined properties from the
        // options.
        const clamScanOptions = (0, helpers_1.removeUndefinedAttributesAndEmptyObjects)((0, ts_deepmerge_1.merge)({
            removeInfected: false,
            quarantineInfected: false,
            scanRecursively: false
        }, clamavOptions ?? {}, envVarOptions ?? {}));
        log.debug('Initializing ClamAV scanner with options:', clamScanOptions);
        const clamScan = await new clamscan_1.default().init(clamScanOptions);
        log.debug('ClamAV scanner initialized. Version:', await clamScan.getVersion());
        // clamscan resolves during init() which binary/daemon it actually
        // ended up using (it can fall back from the configured preference,
        // e.g. if a socket/host/port is misconfigured or a binary isn't
        // found). Reading that resolved value back instead of re-deriving it
        // from the input options ourselves means we never get out of sync
        // with clamscan's own fallback logic.
        //
        // Note: clamscan's own default `this.scanner` is 'clamdscan' even
        // when no socket/host/port was configured at all (it then shells out
        // to the local clamdscan binary instead of talking to a daemon). In
        // that case `scanStream` is not usable (it requires an actual
        // socket/host/port connection), so we additionally require that a
        // daemon connection was actually configured before treating the
        // scanner as stream-capable.
        const resolvedSettings = clamScan.settings;
        const clamdServiceEnabled = clamScan
            .scanner === 'clamdscan' &&
            !!(resolvedSettings.clamdscan.socket ||
                resolvedSettings.clamdscan.port ||
                resolvedSettings.clamdscan.host);
        return new ClamAVScanner(clamScan, { clamdServiceEnabled });
    }
    /**
     * Gets the ClamAV options from environment variables (CLAMSCAN_* and
     * CLAMDSCAN_*). See the docs for what the options do.
     */
    static getEnvVarOptions() {
        // general configuration
        const scanLog = process.env.CLAMSCAN_SCAN_LOG;
        const debugMode = process.env.CLAMSCAN_DEBUG_MODE
            ? process.env.CLAMSCAN_DEBUG_MODE === 'true'
            : undefined;
        const preference = process.env.CLAMSCAN_PREFERENCE;
        // configuration for clamscan (binary)
        const clamscanPath = process.env.CLAMSCAN_PATH;
        const clamscanDb = process.env.CLAMSCAN_DB;
        const clamscanScanArchives = process.env.CLAMSCAN_SCAN_ARCHIVES
            ? process.env.CLAMSCAN_SCAN_ARCHIVES === 'true'
            : undefined;
        const clamscanActive = process.env.CLAMSCAN_ACTIVE
            ? process.env.CLAMSCAN_ACTIVE === 'true'
            : undefined;
        // configuration for clamdscan (daemon with UNIX socket / TCP)
        const clamdscanSocket = process.env.CLAMDSCAN_SOCKET;
        const clamdscanHost = process.env.CLAMDSCAN_HOST;
        const clamdscanPort = process.env.CLAMDSCAN_PORT
            ? Number.parseInt(process.env.CLAMDSCAN_PORT, 10)
            : undefined;
        const clamdscanTimeout = process.env.CLAMDSCAN_TIMEOUT
            ? Number.parseInt(process.env.CLAMDSCAN_TIMEOUT, 10)
            : undefined;
        const clamdscanLocalFallback = process.env.CLAMDSCAN_LOCAL_FALLBACK
            ? process.env.CLAMDSCAN_LOCAL_FALLBACK === 'true'
            : undefined;
        const clamdscanPath = process.env.CLAMDSCAN_PATH;
        const clamdscanConfigFile = process.env.CLAMDSCAN_CONFIG_FILE;
        const clamdscanMultiscan = process.env.CLAMDSCAN_MULTISCAN
            ? process.env.CLAMDSCAN_MULTISCAN === 'true'
            : undefined;
        const clamdscanReloadDb = process.env.CLAMDSCAN_RELOAD_DB
            ? process.env.CLAMDSCAN_RELOAD_DB === 'true'
            : undefined;
        const scanLogOptions = {
            clamscan: {
                path: clamscanPath,
                db: clamscanDb,
                scanArchives: clamscanScanArchives,
                active: clamscanActive
            },
            clamdscan: {
                socket: clamdscanSocket,
                host: clamdscanHost,
                port: clamdscanPort,
                timeout: clamdscanTimeout,
                localFallback: clamdscanLocalFallback,
                path: clamdscanPath,
                configFile: clamdscanConfigFile,
                multiscan: clamdscanMultiscan,
                reloadDb: clamdscanReloadDb
            },
            preference,
            debugMode,
            scanLog
        };
        return scanLogOptions;
    }
    async scan(file) {
        const fileName = (0, path_1.basename)(file);
        log.debug('Scanning uploaded file', fileName, 'with malware scanner', this.name);
        try {
            const scanResponse = await this.scanner.scanFile(file);
            return this.buildScanResult(scanResponse, fileName);
        }
        catch (error) {
            log.error('Error while scanning file', fileName, error);
            return { result: h5p_server_1.MalwareScanResult.NotScanned };
        }
    }
    /**
     * Scans an in-memory buffer for malware. If the underlying scanner is
     * the clamd daemon, the buffer is streamed directly; otherwise it is
     * written to a temporary file first, as the clamscan binary requires a
     * file on disk.
     */
    async scanBuffer(file) {
        log.debug('Scanning uploaded buffer', file.name, 'with malware scanner', this.name);
        try {
            const scanResponse = this.options.clamdServiceEnabled
                ? await this.scanner.scanStream(stream_1.Readable.from(file.data))
                : await this.scanBufferWithTempFile(file.data, file.name);
            return this.buildScanResult(scanResponse, file.name);
        }
        catch (error) {
            log.error('Error while scanning buffer', file.name, error);
            return { result: h5p_server_1.MalwareScanResult.NotScanned };
        }
    }
    async scanBufferWithTempFile(data, fileName) {
        log.debug('Using temporary file scan for ClamAV binary');
        return (0, tmp_promise_1.withFile)(async ({ path: tempFilePath }) => {
            await (0, promises_1.writeFile)(tempFilePath, data);
            return this.scanner.scanFile(tempFilePath);
        }, 
        // basename() strips any path-traversal segments a malicious
        // filename might contain; extname() only ever contributes a
        // suffix like ".svg" to the generated temp path.
        { postfix: (0, path_1.extname)((0, path_1.basename)(fileName)) || undefined });
    }
    buildScanResult(response, fileName) {
        if (response.isInfected) {
            const viruses = response.viruses.join(',');
            log.info('Uploaded file', fileName, 'is infected with:', viruses);
            return { result: h5p_server_1.MalwareScanResult.MalwareFound, viruses };
        }
        log.debug('Uploaded file', fileName, 'is clean');
        return { result: h5p_server_1.MalwareScanResult.Clean };
    }
}
exports.default = ClamAVScanner;
//# sourceMappingURL=ClamAVScanner.js.map