import { pageLoading } from 'kolibri-common/composables/usePageLoading';
import { PageNames } from '../constants';
import AssignmentsRootPage from '../views/coursework/AssignmentsRootPage';
import GradebookPage from '../views/coursework/GradebookPage';
import DiscussionsPage from '../views/coursework/DiscussionsPage';
import { RouteSegments } from './utils';

const { CLASS } = RouteSegments;

function defaultHandler() {
  pageLoading.value = false;
}

export default [
  {
    name: PageNames.COURSEWORK_ASSIGNMENTS,
    path: CLASS + '/coursework/assignments',
    component: AssignmentsRootPage,
    handler: defaultHandler,
    meta: {
      titleParts: ['CLASS_NAME'],
    },
  },
  {
    name: PageNames.COURSEWORK_GRADEBOOK,
    path: CLASS + '/coursework/gradebook',
    component: GradebookPage,
    handler: defaultHandler,
    meta: {
      titleParts: ['CLASS_NAME'],
    },
  },
  {
    name: PageNames.COURSEWORK_DISCUSSIONS,
    path: CLASS + '/coursework/discussions',
    component: DiscussionsPage,
    handler: defaultHandler,
    meta: {
      titleParts: ['CLASS_NAME'],
    },
  },
];
