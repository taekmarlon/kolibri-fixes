"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Example user object
 */
class User {
    constructor(id = '1', name = 'Kolibri User', email = 'user@kolibri.local') {
        this.id = id;
        this.name = name;
        this.type = 'local';
        this.email = email;
    }
    email;
    id;
    name;
    type;
}
exports.default = User;
//# sourceMappingURL=User.js.map