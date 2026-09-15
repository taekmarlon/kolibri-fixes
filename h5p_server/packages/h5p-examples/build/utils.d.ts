import { Request, Express } from 'express';
import { Server } from 'http';
/**
 * Displays links to the server at all available IP addresses.
 * @param port The port at which the server can be accessed.
 */
export declare function displayIps(port: string): void;
/**
 * Starts listening on the given port. If the port is already in use, it
 * tries the next port number up, and keeps doing so until it finds a free
 * one.
 * @param app the Express app to start listening with
 * @param port the port to start trying from
 * @returns the http.Server instance and the port it is actually listening on
 */
export declare function listenOnAvailablePort(app: Express, port: number): Promise<{
    server: Server;
    port: number;
}>;
/**
 * This method will delete all temporary uploaded files from the request
 */
export declare function clearTempFiles(req: Request & {
    files: any;
}): Promise<void>;
