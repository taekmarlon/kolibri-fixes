import { Resource } from 'kolibri/apiResource';

export default new Resource({
  name: 'discussionthread',
  togglePin(threadId) {
    return this.postDetailEndpoint('toggle_pin', threadId);
  },
  toggleClose(threadId) {
    return this.postDetailEndpoint('toggle_close', threadId);
  },
});
