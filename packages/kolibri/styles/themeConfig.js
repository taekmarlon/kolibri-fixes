import Vue from 'vue';

const themeConfig = Vue.observable({
  appBar: {
    background: null,
    textColor: null,
    headerTitle: null,
    primaryColor: null,
    topLogo: {
      src: null,
      alt: null,
      style: null,
    },
  },
  signIn: {
    topLogo: {
      src: null,
      alt: null,
      style: null,
    },
    title: null,
    subtext: null,
    showTitle: null,
    titleStyle: null,
    showPoweredBy: null,
    poweredByStyle: null,
    showKolibriFooterLogo: null,
    background: null,
  },
  sideNav: {
    topLogo: {
      src: null,
      alt: null,
      style: null,
    },
    brandedFooter: {},
    showKFooterLogo: true,
  },
  background: {
    image: null,
    opacity: null,
  },
});

export default themeConfig;
