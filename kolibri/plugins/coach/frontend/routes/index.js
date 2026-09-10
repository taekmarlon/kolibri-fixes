import store from 'kolibri/store';
import router from 'kolibri/router';
import { handleApiError } from 'kolibri/utils/appError';
import useUser from 'kolibri/composables/useUser';
import { get } from '@vueuse/core';
import useFacilities from 'kolibri-common/composables/useFacilities';
import useFacility, { useFacilitySelect } from 'kolibri-common/composables/useFacility';
import plugin_data from 'kolibri-plugin-data';
import { pageLoading } from 'kolibri-common/composables/usePageLoading';
import AllFacilitiesPage from '../views/AllFacilitiesPage';
import CoachClassListPage from '../views/CoachClassListPage';
import ClassLearnersListPage from '../views/ClassLearnersListPage';
import HomePage from '../views/home/HomePage';
import CoachPrompts from '../views/CoachPrompts';
import HomeActivityPage from '../views/home/HomeActivityPage';
import StatusTestPage from '../views/common/status/StatusTestPage';
import CoachLiveClassPage from '../views/CoachLiveClassPage';
import { ClassesPageNames } from '../../../learn/frontend/constants';
import { PageNames } from '../constants';
import { classIdParamRequiredGuard } from './utils';
import examRoutes from './examRoutes';
import lessonsRoutes from './lessonsRoutes';
import learnersRoutes from './learnersRoutes';
import groupsRoutes from './groupsRoutes';
import attendanceRoutes from './attendanceRoutes';
import coursesRoutes from './coursesRoutes';
import courseworkRoutes from './courseworkRoutes';

function showHomePage(toRoute) {
  const initClassInfoPromise = store.dispatch('initClassInfo', toRoute.params.classId);
  const { isSuperuser } = useUser();
  const { fetchFacilities, facilities } = useFacilities();

  const getFacilitiesPromise =
    get(isSuperuser) && get(facilities).length === 0
      ? fetchFacilities().catch(() => {})
      : Promise.resolve();

  return Promise.all([initClassInfoPromise, getFacilitiesPromise]);
}

export default [
  ...examRoutes,
  ...lessonsRoutes,
  ...learnersRoutes,
  ...groupsRoutes,
  ...attendanceRoutes,
  ...courseworkRoutes,
  ...(plugin_data.courses_exist ? coursesRoutes : []),
  {
    name: PageNames.LIVE_CLASS_ROOT,
    path: '/:classId?/live-class',
    alias: ['/:classId?/live_class'],
    component: CoachLiveClassPage,
    async handler(toRoute, fromRoute, next) {
      if (!toRoute.params.classId) {
        const { userFacilityId } = useUser();
        const { selectedFacilityId } = useFacilitySelect();
        const facilityId = selectedFacilityId.value || get(userFacilityId);
        if (facilityId && (!store.state.classList || store.state.classList.length === 0)) {
          try {
            await store.dispatch('setClassList', facilityId);
          } catch (e) {}
        }
        const currentClassId =
          store.state.classSummary?.id ||
          (store.state.classList && store.state.classList.length === 1
            ? store.state.classList[0].id
            : null);
        if (currentClassId) {
          next({
            name: PageNames.LIVE_CLASS_ROOT,
            params: { classId: currentClassId },
            replace: true,
          });
          return;
        }
        if (classIdParamRequiredGuard(toRoute, PageNames.LIVE_CLASS_ROOT, next)) {
          return;
        }
      }
      await showHomePage(toRoute);
      pageLoading.value = false;
    },
    meta: {
      titleParts: ['liveClassLabel', 'CLASS_NAME'],
    },
  },
  {
    path: '/live-class',
    alias: ['/live_class'],
    async handler(toRoute, fromRoute, next) {
      const { userFacilityId } = useUser();
      const { selectedFacilityId } = useFacilitySelect();
      const facilityId = selectedFacilityId.value || get(userFacilityId);
      if (facilityId && (!store.state.classList || store.state.classList.length === 0)) {
        try {
          await store.dispatch('setClassList', facilityId);
        } catch (e) {}
      }
      const currentClassId =
        store.state.classSummary?.id ||
        (store.state.classList && store.state.classList.length === 1
          ? store.state.classList[0].id
          : null);
      if (currentClassId) {
        next({
          name: PageNames.LIVE_CLASS_ROOT,
          params: { classId: currentClassId },
          replace: true,
        });
        return;
      }
      if (classIdParamRequiredGuard(toRoute, PageNames.LIVE_CLASS_ROOT, next)) {
        return;
      }
    },
  },
  {
    name: 'AllFacilitiesPage',
    path: '/facilities/:subtopicName?',
    component: AllFacilitiesPage,
    props: true,
    handler() {
      pageLoading.value = false;
    },
  },
  {
    name: 'CoachClassListPage',
    path: '/:facility_id?/classes/:subtopicName?',
    component: CoachClassListPage,
    props: true,
    async handler(toRoute) {
      // loading state is handled locally
      pageLoading.value = false;
      // if user only has access to one facility, facility_id will not be accessible from URL,
      // but always defaulting to userFacilityId would cause problems for multi-facility admins
      const { userFacilityId } = useUser();
      const { facilities, fetchFacilities, userIsMultiFacilityAdmin } = useFacilities();
      const { selectedFacilityId, setSelectedFacilityId } = useFacilitySelect();
      const { setFacilityId } = useFacility();
      const facilityId =
        toRoute.params.facility_id ||
        selectedFacilityId.value ||
        (typeof window !== 'undefined' && window.localStorage
          ? window.localStorage.getItem('facilityId')
          : null) ||
        get(userFacilityId);

      if (facilities.value.length === 0) {
        await fetchFacilities();
      }

      if (userIsMultiFacilityAdmin.value && !facilityId) {
        return router.replace({
          name: 'AllFacilitiesPage',
          params: { subtopicName: toRoute.params.subtopicName },
        });
      }

      if (facilityId) {
        setSelectedFacilityId(facilityId);
        if (!toRoute.params.facility_id && userIsMultiFacilityAdmin.value) {
          return router.replace({
            name: 'CoachClassListPage',
            params: {
              ...toRoute.params,
              facility_id: facilityId,
            },
          });
        }
      }

      await setFacilityId(facilityId);

      store.dispatch('setClassList', facilityId).then(
        () => {
          if (!store.getters.classListPageEnabled) {
            // If no class list page, redirect to the first (and only) class and
            // to the originally-selected subtopic, if available
            router.replace({
              name: toRoute.params.subtopicName || HomePage.name,
              params: { classId: store.state.classList[0].id },
            });
            return;
          }
        },
        error => handleApiError({ error, reloadOnReconnect: true }),
      );
    },
    meta: {
      titleParts: ['classesLabel'],
    },
  },
  {
    name: PageNames.HOME_PAGE,
    path: '/:classId?/home',
    component: HomePage,
    handler: async (toRoute, fromRoute, next) => {
      if (classIdParamRequiredGuard(toRoute, HomePage.name, next)) {
        return;
      }
      await showHomePage(toRoute);
      pageLoading.value = false;
    },
    meta: {
      titleParts: ['CLASS_NAME'],
    },
  },
  {
    path: '/:classId/home/activity',
    component: HomeActivityPage,
    handler: async toRoute => {
      await showHomePage(toRoute);
      pageLoading.value = false;
    },
    meta: {
      titleParts: ['activityLabel', 'CLASS_NAME'],
    },
  },
  {
    name: ClassesPageNames.CLASS_LEARNERS_LIST_VIEWER,
    path: '/:classId/learners/devices',
    component: ClassLearnersListPage,
    handler() {
      pageLoading.value = false;
    },
  },
  {
    path: '/about/statuses',
    component: StatusTestPage,
    handler() {
      pageLoading.value = false;
    },
  },
  {
    path: '/coach-prompts',
    component: CoachPrompts,
    handler() {
      pageLoading.value = false;
    },
  },
  {
    path: '/',
    // Redirect to AllFacilitiesPage if a superuser and device has > 1 facility and no active facility
    beforeEnter(to, from, next) {
      const { userIsMultiFacilityAdmin } = useFacilities();
      const { selectedFacilityId } = useFacilitySelect();
      const facilityId =
        selectedFacilityId.value ||
        (typeof window !== 'undefined' && window.localStorage
          ? window.localStorage.getItem('facilityId')
          : null);

      if (userIsMultiFacilityAdmin.value && !facilityId) {
        next({ name: 'AllFacilitiesPage', replace: true });
      } else {
        next({
          name: 'CoachClassListPage',
          params: facilityId ? { facility_id: facilityId } : {},
          replace: true,
        });
      }
    },
  },
  {
    path: '*',
    redirect: '/',
  },
];
