<template>
  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div role="main">
      <AnnouncementsSection :standalone="true" />
    </div>
  </LearnAppBarPage>
</template>

<script>
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import commonLearnStrings from './commonLearnStrings';
  import LearnAppBarPage from './LearnAppBarPage';
  import AnnouncementsSection from './AnnouncementsSection';

  export default {
    name: 'LearnerAnnouncementsPage',
    components: {
      LearnAppBarPage,
      AnnouncementsSection,
    },
    mixins: [commonLearnStrings],
    setup() {
      return {
        pageLoading,
      };
    },
  };
</script>

<style lang="scss" scoped>

  [role='main'] {
    max-width: 900px;
    margin: 0 auto;
    padding: 16px;
  }

</style>
