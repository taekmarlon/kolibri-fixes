import { Resource } from 'kolibri/apiResource';

export default new Resource({
  name: 'discussionreply',
  toggleEndorse(replyId) {
    return this.postDetailEndpoint('endorse', replyId);
  },
});
