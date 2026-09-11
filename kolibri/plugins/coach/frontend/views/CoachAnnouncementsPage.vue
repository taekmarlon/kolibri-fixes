<template>

  <CoachAppBarPage :loading="pageLoading">
    <KPageContainer>
      <AnnouncementsBlock />
    </KPageContainer>
  </CoachAppBarPage>

</template>


<script>

  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import CoachAppBarPage from './CoachAppBarPage';
  import AnnouncementsBlock from './home/HomePage/AnnouncementsBlock';

  export default {
    name: 'CoachAnnouncementsPage',
    components: {
      CoachAppBarPage,
      AnnouncementsBlock,
    },
    setup() {
      return {
        pageLoading,
      };
    },
  };

</script>


<style lang="scss" scoped>
</style>
