/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen, fireEvent, waitFor } from '@testing-library/vue';
import LessonCustomResourcePage from '../LessonCustomResourcePage.vue';
import { LearnerLessonResource } from '../../../apiResources';

jest.mock('../../../apiResources', () => ({
  LearnerLessonResource: {
    fetchModel: jest.fn(),
    setCustomProgress: jest.fn().mockResolvedValue({ data: { progress: 1.0 } }),
  },
}));

jest.mock('kolibri-common/composables/useFacilities');
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
      expect(LearnerLessonResource.setCustomProgress).toHaveBeenCalledWith(
        'lesson-1',
        expect.objectContaining({
          content_id: 'res-youtube-1',
          progress: 1.0,
        }),
      );
    });
  });

  it('renders custom structured lesson_builder resource with headings, callouts, and checkpoints', async () => {
    const blocks = [
      {
        id: 'b-1',
        type: 'heading',
        title: 'Cell Biology Overview',
        subtitle: 'The Building Blocks of Life',
      },
      {
        id: 'b-2',
        type: 'text',
        text: 'All living organisms are composed of one or more cells.',
      },
      {
        id: 'b-3',
        type: 'callout',
        callout_type: 'concept',
        title: 'Core Concept',
        text: 'Cells carry genetic material passed during cell division.',
      },
      {
        id: 'b-4',
        type: 'checkpoint',
        question: 'Who first discovered cells under a microscope?',
        answer: 'Robert Hooke in 1665.',
      },
    ];

    LearnerLessonResource.fetchModel.mockResolvedValue({
      id: 'lesson-1',
      title: 'Biology 101',
      classroom: { id: 'class-1', name: 'Science Class' },
      resources: [
        {
          contentnode_id: 'res-youtube-1',
          content_id: 'res-youtube-1',
          is_custom: true,
          resource_type: 'lesson_builder',
          title: 'Cell Biology Interactive Module',
          description: 'A rich structured learning guide',
          content: JSON.stringify(blocks),
          progress: 0,
        },
      ],
    });

    render(LessonCustomResourcePage, { routes });

    await waitFor(() => {
      expect(screen.getByText('CUSTOM LESSON')).toBeInTheDocument();
      expect(screen.getByText('Cell Biology Overview')).toBeInTheDocument();
      expect(screen.getByText('The Building Blocks of Life')).toBeInTheDocument();
      expect(
        screen.getByText('All living organisms are composed of one or more cells.')
      ).toBeInTheDocument();
      expect(screen.getByText('Core Concept')).toBeInTheDocument();
      expect(
        screen.getByText('Who first discovered cells under a microscope?')
      ).toBeInTheDocument();
      expect(screen.getByText('Show Explanation / Answer')).toBeInTheDocument();
    });

    // Click to reveal checkpoint explanation
    const revealBtn = screen.getByText('Show Explanation / Answer');
    await fireEvent.click(revealBtn);

    await waitFor(() => {
      expect(screen.getByText('Robert Hooke in 1665.')).toBeInTheDocument();
      expect(screen.getByText('Hide Explanation')).toBeInTheDocument();
    });
  });
});
