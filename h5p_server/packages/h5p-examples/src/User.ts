import { IUser } from '@lumieducation/h5p-server';

/**
 * Example user object
 */
export default class User implements IUser {
    constructor(
        id: string = '1',
        name: string = 'Kolibri User',
        email: string = 'user@kolibri.local'
    ) {
        this.id = id;
        this.name = name;
        this.type = 'local';
        this.email = email;
    }

    public email: string;
    public id: string;
    public name: string;
    public type: 'local';
}
