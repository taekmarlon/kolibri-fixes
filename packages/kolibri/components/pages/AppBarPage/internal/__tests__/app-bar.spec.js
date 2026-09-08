import { shallowMount } from '@vue/test-utils';
import { ref } from 'vue';
import useKResponsiveWindow from 'kolibri-design-system/lib/composables/useKResponsiveWindow';
import useUser from 'kolibri/composables/useUser';
import AppBar from '../AppBar';

jest.mock('kolibri/client', () => jest.fn(() => Promise.resolve({ data: [] })));
jest.mock('kolibri/urls');
jest.mock('kolibri-design-system/lib/composables/useKResponsiveWindow');
jest.mock('kolibri/composables/useUser');
jest.mock('vue-router/composables', () => ({
  useRoute: jest.fn(() => ({ params: {}, query: {} })),
}));

function createWrapper({ propsData } = {}) {
  const node = document.createElement('div');
  document.body.appendChild(node);
  return shallowMount(AppBar, {
    propsData,
    attachTo: node,
  });
}

describe('app bar component', () => {
  beforeAll(() => {
    useKResponsiveWindow.mockImplementation(() => ({}));
  });
  describe('smoke test', () => {
    it('should render', () => {
      useUser.mockImplementation(() => ({
        isLearner: ref(false),
        isUserLoggedIn: ref(false),
        isAdmin: ref(false),
        isSuperuser: ref(false),
        username: ref(''),
        full_name: ref(''),
        userFacilityName: ref(''),
        userFacilityId: ref(''),
      }));
      const wrapper = createWrapper({ loading: false });
      expect(wrapper.findComponent(AppBar).element).toBeVisible();
    });

    it('should display facility indicator pill for logged-in admin', () => {
      useUser.mockImplementation(() => ({
        isLearner: ref(false),
        isUserLoggedIn: ref(true),
        isAdmin: ref(true),
        isSuperuser: ref(true),
        username: ref('taekmarlon'),
        full_name: ref('Marlon Manalili'),
        userFacilityName: ref('CEDARHALL ACADEMY INC.'),
        userFacilityId: ref('fac-1'),
      }));
      const wrapper = createWrapper({ loading: false });
      expect(wrapper.vm.activeFacilityName).toBe('CEDARHALL ACADEMY INC.');
      expect(wrapper.vm.displaySchoolTitle).toBe('CEDARHALL ACADEMY INC.');
    });
  });
});
