/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen, fireEvent, waitFor } from '@testing-library/vue';
import LessonCustomResourcePage from '../LessonCustomResourcePage.vue';
import { LearnerLessonResource } from '../../../apiResources';

jest.mock('../../../apiResources', () => ({
  LearnerLessonResource: {
    fetchModel: jest.fn(),
  },
}));

jest.mock('kolibri/client', () => jest.fn().mockResolvedValue({ data: {} }));
jest.mock('kolibri/urls', () => ({
  'kolibri:core:contentsummarylog_list': jest
    .fn()
    .mockReturnValue('/api/logger/contentsummarylog/'),
}));
jest.mock('kolibri/composables/useSnackbar', () => () => ({
  createSnackbar: jest.fn(),
  clearSnackbar: jest.fn(),
}));
jest.mock('vue-router/composables', () => ({
  useRoute: () => ({
    params: {
      classId: 'class-1',
      lessonId: 'lesson-1',
      resourceId: 'res-youtube-1',
    },
  }),
}));

const routes = [
  { name: 'HOME', path: '/home' },
  { name: 'ALL_CLASSES', path: '/classes' },
  { name: 'CLASS_ASSIGNMENTS', path: '/classes/:classId' },
  { name: 'LESSON_PLAYLIST', path: '/classes/:classId/lesson/:lessonId' },
];

describe('LessonCustomResourcePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders custom YouTube resource with title and type pill', async () => {
    LearnerLessonResource.fetchModel.mockResolvedValue({
      id: 'lesson-1',
      title: 'Algebra 101',
      classroom: { id: 'class-1', name: 'Math Class' },
      resources: [
        {
          contentnode_id: 'res-youtube-1',
          content_id: 'res-youtube-1',
          is_custom: true,
          resource_type: 'youtube',
          title: 'Graphing Linear Equations',
          description: 'Watch carefully before class',
          url: 'https://www.youtube.com/watch?v=0k2ZzkwW444',
          progress: 0,
        },
      ],
    });

    render(LessonCustomResourcePage, { routes });

    await waitFor(() => {
      expect(screen.getAllByText('Graphing Linear Equations').length).toBeGreaterThan(0);
      expect(screen.getByText('YOUTUBE VIDEO')).toBeInTheDocument();
      expect(screen.getByText('Watch carefully before class')).toBeInTheDocument();
      expect(screen.getByText('Mark as Completed')).toBeInTheDocument();
    });
  });

  it('marks resource as completed when Mark as Completed is clicked', async () => {
    LearnerLessonResource.fetchModel.mockResolvedValue({
      id: 'lesson-1',
      title: 'Algebra 101',
      classroom: { id: 'class-1', name: 'Math Class' },
      resources: [
        {
          contentnode_id: 'res-youtube-1',
          content_id: 'res-youtube-1',
          is_custom: true,
          resource_type: 'youtube',
          title: 'Graphing Linear Equations',
          url: 'https://www.youtube.com/watch?v=0k2ZzkwW444',
          progress: 0,
        },
      ],
    });

    render(LessonCustomResourcePage, { routes });

    await waitFor(() => {
      expect(screen.getByText('Mark as Completed')).toBeInTheDocument();
    });

    const completeBtn = screen.getByText('Mark as Completed');
    await fireEvent.click(completeBtn);

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });
  });
});
