<template>

  <div
    v-show="!$isPrint"
    ref="appBar"
    :style="{
      backgroundColor: themeConfig.appBar.background,
      color: themeConfig.appBar.textColor,
    }"
  >
    <header>
      <SkipNavigationLink />

      <KToolbar
        :removeNavIcon="showAppNavView"
        type="clear"
        class="app-bar"
        :style="{
          height: topBarHeight + 'px',
          color: themeConfig.appBar.textColor,
        }"
        :raised="false"
        :removeBrandDivider="true"
      >
        <KTextTruncator
          :text="truncatedTitle"
          :maxLines="1"
        />
        <template
          v-if="!showAppNavView"
          #icon
        >
          <KIconButton
            icon="menu"
            data-onboarding-id="menubar"
            :color="themeConfig.appBar.textColor"
            :ariaLabel="$tr('openNav')"
            @click="$emit('toggleSideNav')"
          />
        </template>

        <template #brand>
          <div
            class="brand-wrapper"
            style="display: flex; align-items: center; gap: 10px;"
          >
            <img
              v-if="themeConfig.appBar.topLogo"
              :src="themeConfig.appBar.topLogo.src"
              :alt="themeConfig.appBar.topLogo.alt"
              :style="themeConfig.appBar.topLogo.style"
              :class="showAppNavView ? 'brand-logo-left' : 'brand-logo'"
            >
            <span
              v-if="displaySchoolTitle"
              class="facility-school-title"
              :style="{
                color: themeConfig.appBar.textColor,
                fontWeight: '700',
                fontSize: '16px',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '260px',
                marginRight: '10px',
              }"
            >
              {{ displaySchoolTitle }}
            </span>
            <span
              v-if="displaySchoolTitle && truncatedTitle"
              :style="{
                color: themeConfig.appBar.textColor,
                opacity: 0.5,
                marginRight: '10px',
                fontWeight: '300',
              }"
            >|</span>
          </div>
        </template>

        <template
          v-if="showNavigation"
          #navigation
        >
          <slot name="sub-nav">
            <Navbar
              v-if="links.length > 0"
              :style="hiddenNavbarStyle"
              :navigationLinks="links"
              :title="title"
              @update-overflow-count="overflowCount = $event"
            />
          </slot>
        </template>

        <template #actions>
          <div
            ref="appBarActions"
            aria-live="polite"
            :style="{
              paddingBottom: '6px',
            }"
          >
            <slot name="app-bar-actions"></slot>
            <span v-if="isLearner">
              <KIcon
                ref="pointsButton"
                icon="pointsActive"
                :ariaLabel="$tr('pointsAriaLabel')"
                :color="$themeTokens.primary"
              />
              <div
                v-if="!windowIsSmall"
                class="points-description"
              >
                {{ $formatNumber(totalPoints) }}
              </div>
              <div
                v-if="pointsDisplayed"
                class="points-popover"
                :style="{
                  color: $themeTokens.text,
                  padding: '8px',
                  backgroundColor: $themeTokens.surface,
                }"
              >
                {{ $tr('pointsMessage', { points: totalPoints }) }}
              </div>
            </span>
            <!-- Facility Indicator Pill (Super Admin / Admin indicator & switcher) -->
            <button
              v-if="isUserLoggedIn && activeFacilityName"
              ref="facilityPill"
              type="button"
              class="facility-indicator-pill"
              :class="{ clickable: canSwitchFacility }"
              :title="facilityPillTitle"
              :style="facilityPillStyle"
              @click="toggleFacilityDropdown"
            >
              <span
                class="facility-pill-icon"
                aria-hidden="true"
              >{{ '🏫' }}</span>
              <span class="facility-pill-name">{{ activeFacilityName }}</span>
              <span
                v-if="canSwitchFacility"
                class="facility-pill-caret"
              >{{ showFacilityDropdown ? '▲' : '▼' }}</span>
            </button>

            <!-- Facility Switcher Dropdown Menu -->
            <div
              v-if="showFacilityDropdown && canSwitchFacility"
              ref="facilityDropdown"
              class="facility-dropdown-menu"
              :style="{
                backgroundColor: $themeTokens.surface,
                color: $themeTokens.text,
              }"
            >
              <div
                class="facility-dropdown-header"
                :style="{ color: $themeTokens.annotation }"
              >
                {{ $tr('switchFacility') }}
              </div>
              <button
                v-for="fac in facilities"
                :key="fac.id"
                type="button"
                class="facility-dropdown-item"
                :class="{ active: fac.name === activeFacilityName }"
                @click="selectFacility(fac)"
              >
                <span class="fac-name">{{ fac.name }}</span>
                <span
                  v-if="fac.name === activeFacilityName"
                  class="fac-check"
                >{{ '✓' }}</span>
              </button>
            </div>

            <span
              v-if="isUserLoggedIn"
              tabindex="-1"
            >
              <KIcon
                icon="person"
                :style="{
                  fill: themeConfig.appBar.textColor,
                  height: '24px',
                  width: '24px',
                  margin: '4px',
                  top: '8px',
                }"
              />
              <span class="username">
                {{ usernameForDisplay }}
              </span>
            </span>
          </div>
        </template>
      </KToolbar>
    </header>
    <div
      v-show="showNavigation && !showAppNavView && !showTopNavBar"
      class="subpage-nav"
    >
      <slot name="sub-nav">
        <Navbar
          v-if="links.length > 0"
          :class="{ 'sub-nav': !showTopNavBar }"
          :navigationLinks="links"
          :title="title"
        />
      </slot>
    </div>
  </div>

</template>


<script>

  import { get } from '@vueuse/core';
  import { computed, ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router/composables';
  import client from 'kolibri/client';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import KToolbar from 'kolibri-design-system/lib/KToolbar';
  import KIconButton from 'kolibri-design-system/lib/buttons-and-links/KIconButton';
  import themeConfig from 'kolibri/styles/themeConfig';
  import useKResponsiveWindow from 'kolibri-design-system/lib/composables/useKResponsiveWindow';
  import useTotalProgress from 'kolibri/composables/useTotalProgress';
  import useNav from 'kolibri/composables/useNav';
  import useUser from 'kolibri/composables/useUser';
  import SkipNavigationLink from '../../../SkipNavigationLink';
  import Navbar from './Navbar';

  const hashedValuePattern = /^[a-f0-9]{30}$/;

  export default {
    name: 'AppBar',
    components: {
      KToolbar,
      KIconButton,
      SkipNavigationLink,
      Navbar,
    },
    mixins: [commonCoreStrings],
    setup() {
      const $route = useRoute();
      const { windowIsSmall } = useKResponsiveWindow();
      const { topBarHeight, navItems } = useNav();
      const {
        isLearner,
        isUserLoggedIn,
        isAdmin,
        isSuperuser,
        username,
        full_name,
        userFacilityName,
        userFacilityId,
      } = useUser();
      const { totalPoints, fetchPoints } = useTotalProgress();
      const links = computed(() => {
        const currentItem = get(navItems).find(nc => nc.url === window.location.pathname);
        if (!currentItem || !currentItem.routes) {
          return [];
        }
        return currentItem.routes.map(route => ({
          title: route.label,
          link: { name: route.name, params: $route.params, query: $route.query },
          icon: route.icon,
          condition: route.condition,
        }));
      });

      const facilities = ref([]);
      const showFacilityDropdown = ref(false);
      const selectedFacilityId = ref(localStorage.getItem('facilityId') || '');
      const selectedFacilityName = ref(
        localStorage.getItem('facilityName') ||
          localStorage.getItem('kolibri_active_facility_name') ||
          ''
      );

      const activeFacilityName = computed(() => {
        if (selectedFacilityName.value) {
          return selectedFacilityName.value;
        }
        if (userFacilityName.value) {
          return userFacilityName.value;
        }
        if (facilities.value.length > 0) {
          return facilities.value[0].name;
        }
        return '';
      });

      const displaySchoolTitle = computed(() => {
        return themeConfig.appBar.headerTitle || activeFacilityName.value || '';
      });

      const canSwitchFacility = computed(() => {
        return (isSuperuser.value || isAdmin.value) && facilities.value.length > 1;
      });

      function fetchFacilities() {
        if (!isUserLoggedIn.value) return;
        client({ url: '/api/auth/facility/' })
          .then(res => {
            const data = Array.isArray(res.data) ? res.data : res.data?.results || [];
            facilities.value = data;
            if (!selectedFacilityName.value && data.length > 0) {
              const matched = data.find(f => f.id === userFacilityId.value) || data[0];
              selectedFacilityId.value = matched.id;
              selectedFacilityName.value = matched.name;
              localStorage.setItem('facilityId', matched.id);
              localStorage.setItem('facilityName', matched.name);
            }
          })
          .catch(() => {});
      }

      onMounted(() => {
        fetchFacilities();
      });

      function toggleFacilityDropdown(e) {
        if (!canSwitchFacility.value) return;
        e.stopPropagation();
        showFacilityDropdown.value = !showFacilityDropdown.value;
      }

      function selectFacility(fac) {
        selectedFacilityId.value = fac.id;
        selectedFacilityName.value = fac.name;
        localStorage.setItem('facilityId', fac.id);
        localStorage.setItem('facilityName', fac.name);
        localStorage.setItem('kolibri_active_facility_id', fac.id);
        localStorage.setItem('kolibri_active_facility_name', fac.name);
        showFacilityDropdown.value = false;
        window.dispatchEvent(new CustomEvent('kolibri-facility-changed', { detail: fac }));
        window.location.reload();
      }

      const facilityPillStyle = computed(() => ({
        color: themeConfig.appBar.textColor,
        borderColor:
          themeConfig.appBar.textColor === '#ffffff'
            ? 'rgba(255, 255, 255, 0.35)'
            : 'rgba(0, 0, 0, 0.2)',
        backgroundColor:
          themeConfig.appBar.textColor === '#ffffff'
            ? 'rgba(255, 255, 255, 0.15)'
            : 'rgba(0, 0, 0, 0.06)',
      }));

      const facilityPillTitle = computed(() => {
        if (canSwitchFacility.value) {
          return `Current Facility: ${activeFacilityName.value} (Click to switch)`;
        }
        return `Current Facility: ${activeFacilityName.value}`;
      });

      return {
        themeConfig,
        windowIsSmall,
        topBarHeight,
        links,
        isUserLoggedIn,
        isLearner,
        username,
        fullName: full_name,
        totalPoints,
        fetchPoints,
        facilities,
        showFacilityDropdown,
        activeFacilityName,
        displaySchoolTitle,
        canSwitchFacility,
        facilityPillStyle,
        facilityPillTitle,
        toggleFacilityDropdown,
        selectFacility,
      };
    },
    props: {
      title: {
        type: String,
        required: true,
      },
      showNavigation: {
        type: Boolean,
        default: true,
      },
      showAppNavView: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        pointsDisplayed: false,
        appBarWidth: 0,
        overflowCount: 0,
      };
    },
    computed: {
      // temp hack for the VF plugin
      usernameForDisplay() {
        return !hashedValuePattern.test(this.username) ? this.username : this.fullName;
      },
      showTopNavBar() {
        return this.overflowCount === 0;
      },
      truncatedTitle() {
        if (!this.title) return '';
        // Dynamically truncate title based on remaining space in AppBar
        const offset = this.$refs.appBarActions?.clientWidth + 100;
        const averageCharWidth = 10;
        const availableWidth = this.appBarWidth - offset;
        const maxChars = availableWidth > 0 ? Math.floor(availableWidth / averageCharWidth) : 1;
        return this.truncateText(this.title, maxChars);
      },
      hiddenNavbarStyle() {
        if (this.showTopNavBar) {
          return {};
        }
        // Hide top navbar, but keep it in the DOM for overflow calulations
        const rightOffset = `${this.title.length * 10 + 250}px`;
        return {
          pointerEvents: 'none',
          opacity: '0',
          position: 'fixed',
          right: rightOffset,
        };
      },
    },
    created() {
      if (this.isLearner) {
        this.fetchPoints();
      }
    },
    beforeDestroy() {
      window.removeEventListener('click', this.handleWindowClick);
      window.removeEventListener('keydown', this.handlePopoverByKeyboard, true);
      window.removeEventListener('resize', this.updateAppBarWidth);
    },
    mounted() {
      window.addEventListener('click', this.handleWindowClick);
      window.addEventListener('keydown', this.handlePopoverByKeyboard, true);
      window.addEventListener('resize', this.updateAppBarWidth);
      this.updateAppBarWidth();
    },
    methods: {
      handleWindowClick(event) {
        if (this.$refs.pointsButton && this.$refs.pointsButton.$el) {
          if (!this.$refs.pointsButton.$el.contains(event.target) && this.pointsDisplayed) {
            this.pointsDisplayed = false;
          } else if (
            this.$refs.pointsButton &&
            this.$refs.pointsButton.$el &&
            this.$refs.pointsButton.$el.contains(event.target)
          ) {
            this.pointsDisplayed = !this.pointsDisplayed;
          }
        }
        if (this.showFacilityDropdown) {
          const pill = this.$refs.facilityPill;
          const drop = this.$refs.facilityDropdown;
          if (
            (!pill || !pill.contains(event.target)) &&
            (!drop || !drop.contains(event.target))
          ) {
            this.showFacilityDropdown = false;
          }
        }
        return event;
      },
      handlePopoverByKeyboard(event) {
        if ((event.key == 'Tab' || event.key == 'Escape') && this.pointsDisplayed) {
          this.pointsDisplayed = false;
        }
        if ((event.key == 'Tab' || event.key == 'Escape') && this.showFacilityDropdown) {
          this.showFacilityDropdown = false;
        }
      },
      updateAppBarWidth() {
        this.appBarWidth = this.$refs.appBar?.clientWidth || 0;
      },
      truncateText(value, maxLength) {
        if (value && value.length > maxLength) {
          return value.substring(0, maxLength) + '...';
        }
        return value;
      },
    },
    $trs: {
      openNav: {
        message: 'Open site navigation',
        context:
          "This message is providing additional context to the screen-reader users, but is not visible in the Kolibri UI.\n\nIn this case the screen-reader will announce the message when user navigates to the 'hamburger' button with the keyboard, to indicate that it allows them to open the sidebar navigation menu.",
      },
      pointsMessage: {
        message: 'You earned { points, number } points',
        context: 'Notification indicating how many points a leaner has earned.',
      },
      pointsAriaLabel: {
        message: 'Points earned',
        context:
          'Information for screen reader users about what information they will get by clicking a button',
      },
      switchFacility: {
        message: 'Switch Facility',
        context: 'Dropdown header to switch active facility',
      },
    },
  };

</script>


<style lang="scss" scoped>

  @import '~kolibri-design-system/lib/styles/definitions';

  .user-menu-button {
    text-transform: none;
    vertical-align: middle;
  }

  .facility-indicator-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    margin-right: 12px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.5;
    letter-spacing: 0.2px;
    cursor: default;
    user-select: none;
    vertical-align: middle;
    border: 1px solid transparent;
    border-radius: 16px;
    outline: none;
    transition: all 0.2s ease;

    &.clickable {
      cursor: pointer;
      &:hover {
        opacity: 0.9;
        transform: translateY(-1px);
      }
    }
  }

  .facility-pill-icon {
    font-size: 14px;
    line-height: 1;
  }

  .facility-pill-name {
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .facility-pill-caret {
    margin-left: 2px;
    font-size: 8px;
    transition: transform 0.2s ease;
  }

  .facility-dropdown-menu {
    position: fixed;
    top: 50px;
    right: 130px;
    z-index: 1000;
    min-width: 220px;
    max-width: 320px;
    overflow: hidden;
    font-size: 13px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
  }

  .facility-dropdown-header {
    padding: 10px 14px 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  }

  .facility-dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 10px 14px;
    font-family: inherit;
    font-size: 13px;
    color: inherit;
    text-align: left;
    cursor: pointer;
    background: transparent;
    border: none;
    outline: none;
    transition: background-color 0.15s;

    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
    }

    &.active {
      font-weight: bold;
      background-color: rgba(0, 0, 0, 0.08);
    }
  }

  .fac-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .fac-check {
    margin-left: 8px;
    font-weight: bold;
  }

  @media (max-width: 750px) {
    .facility-pill-name {
      max-width: 80px;
    }
  }

  .username {
    position: relative;
    bottom: 3px;
    max-width: 200px;
    // overflow-x hidden seems to affect overflow-y also, so include a fixed height
    height: 16px;
    padding-left: 8px;
    // overflow: hidden on both x and y so that the -y doesn't show scroll buttons
    // at certain zooms/screen sizes
    overflow: hidden;
    font-size: small;
    font-weight: bold;
    text-overflow: ellipsis;
  }

  @media (max-width: 750px) {
    .username {
      max-width: 50px;
    }
  }

  // Holdover from keen-ui to keep dropdown profile correctly formatted.
  ::v-deep .ui-menu {
    min-width: 10.5rem;
    max-width: 17rem;
    max-height: 100vh;
    padding: 0.25rem 0;
    margin: 0;
    overflow-x: hidden;
    overflow-y: auto;
    list-style: none;
    background-color: inherit;
    border: 0.0625rem solid rgba(0, 0, 0, 0.08);
    outline: none;
  }

  .user-menu-dropdown {
    position: fixed;
    right: 8px;
    z-index: 8;
  }

  .role {
    margin-bottom: 8px;
    font-size: small;
    font-weight: bold;
  }

  .total-points {
    display: inline-block;
    margin-left: 16px;
  }

  ::v-deep .k-toolbar-right {
    display: flex;
    align-items: center;
  }

  ::v-deep .k-toolbar-left {
    display: flex;
    align-items: center;
    margin-left: 8px;
  }

  .brand-logo {
    max-width: 48px;
    max-height: 48px;
    margin-right: 8px;
    vertical-align: middle;
  }

  .brand-logo-left {
    margin-left: -16px !important;
  }

  // Hide the UiButton focus ring
  ::v-deep .ui-button__focus-ring {
    display: none;
  }

  .points-popover {
    @extend %dropshadow-6dp;

    position: absolute;
    right: 50px;
    z-index: 24;
    font-size: 12px;
    border-radius: 8px;
  }

  .points-description {
    display: inline-block;
    margin-left: 8px;
    font-size: 14px;
  }

  ::v-deep .sub-nav .items {
    margin-top: 0;
  }

</style>
