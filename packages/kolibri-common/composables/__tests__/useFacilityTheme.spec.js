import themeConfig from 'kolibri/styles/themeConfig';
import FacilityDatasetResource from 'kolibri-common/apiResources/FacilityDatasetResource';
import { applyFacilityTheme } from '../useFacilityTheme';

jest.mock('kolibri-common/apiResources/FacilityDatasetResource');
jest.mock('../useFacility', () => {
  const { ref } = require('vue');
  const facilityConfig = ref({
    id: 'dataset-123',
    extra_fields: {
      theme: {
        header_background: '#047857',
        header_text_color: '#ffffff',
        header_title: 'Evergreen High',
        primary_color: '#10b981',
      },
    },
  });
  return jest.fn(() => ({
    facilityConfig,
    selectedFacilityId: ref('fac-1'),
    currentFacilityName: ref('Evergreen High'),
    fetchFacilityConfig: jest.fn(),
  }));
});

describe('useFacilityTheme', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('applyFacilityTheme', () => {
    it('applies custom theme properties to themeConfig', () => {
      applyFacilityTheme({
        header_background: '#1e3a8a',
        header_text_color: '#fbbf24',
        header_title: 'St. Jude Academy',
        primary_color: '#2563eb',
        logo_url: 'https://example.com/logo.png',
        sign_in_title: 'Welcome to St. Jude',
        sign_in_subtext: 'Empowering Young Leaders',
      });

      expect(themeConfig.appBar.background).toBe('#1e3a8a');
      expect(themeConfig.appBar.textColor).toBe('#fbbf24');
      expect(themeConfig.appBar.headerTitle).toBe('St. Jude Academy');
      expect(themeConfig.appBar.primaryColor).toBe('#2563eb');
      expect(themeConfig.appBar.topLogo.src).toBe('https://example.com/logo.png');
      expect(themeConfig.signIn.title).toBe('Welcome to St. Jude');
      expect(themeConfig.signIn.subtext).toBe('Empowering Young Leaders');
    });

    it('resets theme to defaults when passed empty theme', () => {
      applyFacilityTheme({});

      expect(themeConfig.appBar.headerTitle).toBeNull();
      expect(themeConfig.appBar.primaryColor).toBeNull();
      expect(themeConfig.signIn.subtext).toBeNull();
    });
  });

  describe('saveFacilityTheme', () => {
    it('persists updated theme to dataset via FacilityDatasetResource', async () => {
      FacilityDatasetResource.saveModel.mockResolvedValue({ id: 'dataset-123' });
      // eslint-disable-next-line global-require
      const useFacilityTheme = require('../useFacilityTheme').default;
      const { saveFacilityTheme } = useFacilityTheme();

      const newTheme = {
        header_background: '#4c1d95',
        header_title: 'Purple Academy',
      };

      await saveFacilityTheme('dataset-123', newTheme);

      expect(FacilityDatasetResource.saveModel).toHaveBeenCalledWith({
        id: 'dataset-123',
        data: {
          extra_fields: {
            theme: newTheme,
          },
        },
      });
      expect(themeConfig.appBar.headerTitle).toBe('Purple Academy');
      expect(themeConfig.appBar.background).toBe('#4c1d95');
    });
  });
});
