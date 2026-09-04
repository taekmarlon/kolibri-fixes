import { render, screen } from '@testing-library/vue';
import AssignedCourseworkCards from '../AssignedCourseworkCards.vue';
import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
import AssignmentSubmissionResource from 'kolibri-common/apiResources/AssignmentSubmissionResource';
import { ClassesPageNames } from '../../../constants';

jest.mock('kolibri-common/apiResources/AssignmentResource', () => ({
  fetchCollection: jest.fn(),
}));

jest.mock('kolibri-common/apiResources/AssignmentSubmissionResource', () => ({
  fetchCollection: jest.fn(),
}));

const routes = [
  {
    name: ClassesPageNames.COURSEWORK_ASSIGNMENT_DETAIL,
    path: '/classes/:classId/assignments/:assignmentId',
  },
  {
    name: ClassesPageNames.COURSEWORK_DISCUSSIONS,
    path: '/classes/:classId/discussions',
  },
];

describe('AssignedCourseworkCards', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders section header and discussion banner', async () => {
    AssignmentResource.fetchCollection.mockResolvedValue([]);
    AssignmentSubmissionResource.fetchCollection.mockResolvedValue([]);

    render(AssignedCourseworkCards, {
      props: {
        classId: 'class-123',
      },
      routes,
    });

    expect(screen.getByText('Homework & Assignments')).toBeTruthy();
    expect(screen.getByText('Classroom Q&A & Discussions')).toBeTruthy();
    expect(screen.getByText('Open Forum')).toBeTruthy();
  });

  it('renders assignments with video badge and points', async () => {
    AssignmentResource.fetchCollection.mockResolvedValue([
      {
        id: 'asgn-1',
        title: 'Fractions & Ratios Homework',
        description: 'Watch the video and solve problems',
        points_possible: 100,
        due_date: '2026-10-01T12:00:00Z',
        video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      },
    ]);
    AssignmentSubmissionResource.fetchCollection.mockResolvedValue([]);

    render(AssignedCourseworkCards, {
      props: {
        classId: 'class-123',
      },
      routes,
    });

    expect((await screen.findAllByText('Fractions & Ratios Homework')).length).toBeGreaterThan(0);
    expect(screen.getByText('🎥 Video Lesson')).toBeTruthy();
    expect(screen.getByText('100 pts')).toBeTruthy();
  });
});
