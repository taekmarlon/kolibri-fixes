"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const cache_manager_1 = require("cache-manager");
const keyv_1 = require("keyv");
const cacheable_1 = require("cacheable");
/**
 * Caches arbitrary key-value pairs.
 */
class CachedKeyValueStorage {
    prefix;
    cache;
    /**
     * @param cache the cache backend, if left undefined, an in-memory cache is
     * created.
     */
    constructor(prefix, cache) {
        this.prefix = prefix;
        this.cache = cache;
        if (!this.cache) {
            this.cache = (0, cache_manager_1.createCache)({
                stores: [
                    new keyv_1.Keyv({
                        store: new cacheable_1.CacheableMemory({ lruSize: 2 ** 10 }),
                        // We store data in memory only, so there's no need
                        // to (de)serialize it to/from strings. Doing so
                        // would break on values like Date objects.
                        serialize: undefined,
                        deserialize: undefined
                    })
                ]
            });
        }
    }
    async load(key) {
        return this.cache.get(`${this.prefix}-${key}`);
    }
    async save(key, value) {
        // A ttl of 0 tells Keyv to store the entry without expiration,
        // overriding any default ttl configured on the cache backend (this
        // storage class is used to persist actual data, not just as a
        // re-fetchable cache).
        return this.cache.set(`${this.prefix}-${key}`, value, 0);
    }
}
exports.default = CachedKeyValueStorage;
//# sourceMappingURL=CachedKeyValueStorage.js.map