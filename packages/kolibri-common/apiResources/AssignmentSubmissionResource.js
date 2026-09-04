import { Resource } from 'kolibri/apiResource';

export default new Resource({
  name: 'submission',
  gradeSubmission(submissionId, gradeData) {
    return this.postDetailEndpoint('grade', submissionId, gradeData);
  },
});
