import { registerNavItem } from 'kolibri/composables/useNav';
import urls from 'kolibri/urls';
import useUser from 'kolibri/composables/useUser';
import useAiTutor from 'kolibri-common/composables/useAiTutor';
import useLiveSessions from 'kolibri-common/composables/useLiveSessions';
import { createTranslator } from 'kolibri/utils/i18n';
import baseRoutes from '../routes/baseRoutes';

let pollStarted = false;
function initPolling() {
  if (!pollStarted && typeof window !== 'undefined') {
    pollStarted = true;
    const { fetchLiveSessions } = useLiveSessions();
    fetchLiveSessions();
    setInterval(fetchLiveSessions, 3000);
  }
}

const navStrings = createTranslator('LearnSideNavEntryStrings', {
  homeLabel: {
    message: 'Home',
    context:
      "Home page is a place for learners containing summary of their activities and suggestions for what to do next. For example, they can see a list of classes they're enrolled in, their recent lessons and quizzes, and they can directly navigate to resources to continue learning from.",
  },
  libraryLabel: {
    message: 'Library',
    context:
      "The 'Library' section displays channels available on Kolibri server, and allows learners to browse, explore and filter topics and resources on their own.",
  },
  bookmarksLabel: {
    message: 'Bookmarks',
    context:
      'Bookmarks are used to give all users a way of saving a reference for a specific resource or topic to come back to later.',
  },
  liveMeetingLabel: {
    message: 'Live Class',
    context: 'Label for live class / video conferencing in learner navigation and top bar',
  },
  aiTutorLabel: {
    message: 'AI Tutor',
    context: 'Label for personal AI Tutor in learner side navigation and top bar',
  },
  learnLabel: {
    message: 'Learn',
    context:
      "Each time a learner signs in to Kolibri, the first thing they see is the  'Learn' page with the list of all the classes they are enrolled to.",
  },
});

registerNavItem({
  get url() {
    return urls['kolibri:kolibri.plugins.learn:learn']();
  },
  get routes() {
    initPolling();
    const { isUserLoggedIn } = useUser();
    const { isAiEnabled } = useAiTutor();
    const { liveClassesCount } = useLiveSessions();
    if (!isUserLoggedIn.value) {
      return [];
    }
    const isLive = liveClassesCount.value > 0;
    const navItems = [
      {
        label: navStrings.$tr('homeLabel'),
        icon: 'dashboard',
        route: baseRoutes.home.path,
        name: baseRoutes.home.name,
      },
      {
        label: isLive
          ? `🟢 ${navStrings.$tr('liveMeetingLabel')}`
          : navStrings.$tr('liveMeetingLabel'),
        icon: 'group',
        route: baseRoutes.liveMeeting.path,
        name: baseRoutes.liveMeeting.name,
      },
    ];

    if (isAiEnabled.value) {
      navItems.push({
        label: navStrings.$tr('aiTutorLabel'),
        icon: 'practice',
        route: baseRoutes.aiTutor.path,
        name: baseRoutes.aiTutor.name,
      });
    }

    navItems.push(
      {
        label: navStrings.$tr('libraryLabel'),
        icon: 'library',
        route: baseRoutes.library.path,
        name: baseRoutes.library.name,
      },
      {
        label: navStrings.$tr('bookmarksLabel'),
        icon: 'bookmark',
        route: baseRoutes.bookmarks.path,
        name: baseRoutes.bookmarks.name,
      },
    );

    return navItems;
  },
  get label() {
    return navStrings.$tr('learnLabel');
  },
  icon: 'learn',
  bottomBar: true,
});
