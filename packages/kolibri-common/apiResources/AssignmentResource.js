import { Resource } from 'kolibri/apiResource';

export default new Resource({
  name: 'assignment',
  fetchGradebook(classId) {
    return this.getListEndpoint('gradebook', { collection: classId });
  },
});
