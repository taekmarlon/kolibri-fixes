"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.displayIps = displayIps;
exports.listenOnAvailablePort = listenOnAvailablePort;
exports.clearTempFiles = clearTempFiles;
const os_1 = __importDefault(require("os"));
const promises_1 = require("fs/promises");
/**
 * Displays links to the server at all available IP addresses.
 * @param port The port at which the server can be accessed.
 */
function displayIps(port) {
    console.log('H5P Interactive server is running:');
    const networkInterfaces = os_1.default.networkInterfaces();
    // eslint-disable-next-line guard-for-in
    for (const devName in networkInterfaces) {
        networkInterfaces[devName]
            .filter((int) => !int.internal)
            .forEach((int) => console.log(`http://${int.family === 'IPv6' ? '[' : ''}${int.address}${int.family === 'IPv6' ? ']' : ''}:${port}`));
    }
}
/**
 * Starts listening on the given port. If the port is already in use, it
 * tries the next port number up, and keeps doing so until it finds a free
 * one.
 * @param app the Express app to start listening with
 * @param port the port to start trying from
 * @returns the http.Server instance and the port it is actually listening on
 */
function listenOnAvailablePort(app, port) {
    return new Promise((resolve, reject) => {
        const server = app.listen(port);
        server.once('listening', () => {
            resolve({ server, port });
        });
        server.once('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                server.close();
                resolve(listenOnAvailablePort(app, port + 1));
            }
            else {
                reject(error);
            }
        });
    });
}
/**
 * This method will delete all temporary uploaded files from the request
 */
async function clearTempFiles(req) {
    if (!req.files) {
        return;
    }
    await Promise.all(Object.keys(req.files).map((file) => req.files[file].tempFilePath !== undefined &&
        req.files[file].tempFilePath !== ''
        ? (0, promises_1.rm)(req.files[file].tempFilePath, {
            recursive: true,
            force: true
        })
        : Promise.resolve()));
}
//# sourceMappingURL=utils.js.map