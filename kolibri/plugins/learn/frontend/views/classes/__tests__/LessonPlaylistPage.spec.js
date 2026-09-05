/* eslint-disable kolibri/tests-no-hardcoded-strings */
import Vuex from 'vuex';
import { render, screen } from '@testing-library/vue';
import LessonPlaylistPage from '../LessonPlaylistPage.vue';
import { PageNames, ClassesPageNames } from '../../../constants';

jest.mock('kolibri-common/composables/usePageLoading');

jest.mock('../../../composables/useContentLink', () => () => ({
  genContentLinkBackLinkCurrentPage: jest.fn(() => ({ name: 'TOPICS_CONTENT' })),
}));

jest.mock('../../../composables/useContentNodeProgress', () => () => ({
  contentNodeProgressMap: {},
  contentNodeProgressMetaDataMap: {},
  fetchContentNodeProgress: jest.fn(),
}));

const routes = [
  { name: PageNames.HOME, path: '/home' },
  { name: ClassesPageNames.ALL_CLASSES, path: '/classes' },
  { name: ClassesPageNames.CLASS_ASSIGNMENTS, path: '/classes/:classId' },
  { name: ClassesPageNames.LESSON_PLAYLIST, path: '/classes/:classId/lesson/:lessonId' },
  {
    name: ClassesPageNames.LESSON_CUSTOM_RESOURCE,
    path: '/classes/:classId/lesson/:lessonId/resource/:resourceId',
  },
  { name: PageNames.TOPICS_CONTENT, path: '/topics/:id' },
];

function createMockStore({ currentLesson = {}, contentNodesMap = {} } = {}) {
  return new Vuex.Store({
    modules: {
      lessonPlaylist: {
        namespaced: true,
        state: {
          currentLesson,
          contentNodesMap,
        },
        mutations: {
          SET_CURRENT_LESSON(state, lesson) {
            state.currentLesson = lesson;
          },
        },
      },
    },
  });
}

describe('LessonPlaylistPage', () => {
  it('renders custom resource cards and does NOT show missing resources alert for custom resources', () => {
    const customResource = {
      contentnode_id: 'custom-img-1',
      content_id: 'custom-img-1',
      is_custom: true,
      resource_type: 'image',
      title: 'Fraction Diagram.jpg',
      file_url: '/media/lessons/resources/diagram.jpg',
      file_name: 'Fraction Diagram.jpg',
    };

    const currentLesson = {
      id: 'lesson-1',
      title: 'Intro to Fractions',
      description: 'Review the diagram',
      is_active: true,
      classroom: { id: 'class-1', name: 'Grade 1 Math' },
      resources: [customResource],
      missing_resource: false,
    };

    const store = createMockStore({
      currentLesson,
      contentNodesMap: {},
    });

    render(LessonPlaylistPage, {
      store,
      routes,
    });

    expect(screen.getAllByText('Intro to Fractions').length).toBeGreaterThan(0);
    expect(screen.getByText('Fraction Diagram.jpg')).toBeInTheDocument();
    // Alert should NOT be in document
    expect(screen.queryByText(/Some resources are missing or not supported/i)).toBeNull();
  });

  it('shows missing resources alert if channel resources are actually missing', () => {
    const channelResource = {
      contentnode_id: 'channel-node-1',
      content_id: 'channel-node-1',
      is_custom: false,
      title: 'Khan Academy Video',
    };

    const currentLesson = {
      id: 'lesson-2',
      title: 'Video Lesson',
      is_active: true,
      classroom: { id: 'class-1', name: 'Grade 1 Math' },
      resources: [channelResource],
      missing_resource: true,
    };

    const store = createMockStore({
      currentLesson,
      contentNodesMap: {},
    });

    render(LessonPlaylistPage, {
      store,
      routes,
    });

    expect(screen.getByText(/Some resources are missing or not supported/i)).toBeInTheDocument();
  });
});
