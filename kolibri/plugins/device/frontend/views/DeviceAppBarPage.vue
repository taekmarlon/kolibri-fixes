<template>

  <AppBarPage
    :title="title"
    :loading="loading"
  >
    <ImpactStoryBanner />
    <DeprecationWarningBanner style="margin-bottom: 1em" />

    <div>
      <slot></slot>
    </div>
  </AppBarPage>

</template>


<script>

  import AppBarPage from 'kolibri/components/pages/AppBarPage';
  import useFacilityTheme from 'kolibri-common/composables/useFacilityTheme';
  import ImpactStoryBanner from 'kolibri-common/components/ImpactStoryBanner';
  import DeprecationWarningBanner from './DeprecationWarningBanner';

  export default {
    name: 'DeviceAppBarPage',
    components: { AppBarPage, ImpactStoryBanner, DeprecationWarningBanner },
    setup() {
      useFacilityTheme();
    },
    props: {
      title: {
        type: String,
        required: true,
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
  };

</script>
