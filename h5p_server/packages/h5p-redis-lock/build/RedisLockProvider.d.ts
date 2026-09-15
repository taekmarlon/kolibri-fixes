import { RedisClientType } from 'redis';
import { ILockProvider } from '@lumieducation/h5p-server';
export default class RedisLockProvider implements ILockProvider {
    private redis;
    private options?;
    constructor(redis: RedisClientType, options?: {
        retryTime?: number;
    });
    acquire<T>(key: string, callback: () => Promise<T>, options: {
        timeout: number;
        maxOccupationTime: number;
    }): Promise<T>;
}
