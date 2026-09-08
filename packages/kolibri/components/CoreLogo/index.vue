<template>

  <img
    v-if="image"
    :src="image"
    alt=""
    class="core-logo-img"
  >
  <svg
    v-else
    class="phiedu-core-logo"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 48 48"
    fill="none"
    role="img"
    aria-label="PHIEDU"
  >
    <rect
      width="48"
      height="48"
      rx="10"
      :fill="$themeTokens.primary || '#1d4ed8'"
    />
    <!-- Stylized open book icon -->
    <path
      d="M12 16.5C12 15.12 13.12 14 14.5 14H22V31.5H14.5C13.12 31.5 12 30.38 12 29V16.5Z"
      fill="white"
      opacity="0.95"
    />
    <path
      d="M36 16.5C36 15.12 34.88 14 33.5 14H26V31.5H33.5C34.88 31.5 36 30.38 36 29V16.5Z"
      fill="white"
      opacity="0.95"
    />
    <!-- Book spine / center line -->
    <line
      x1="24"
      y1="14"
      x2="24"
      y2="33"
      stroke="white"
      stroke-width="2"
      stroke-linecap="round"
    />
    <!-- Lower pages curve -->
    <path
      d="M12 29C15 28 20 28.5 24 31.5C28 28.5 33 28 36 29"
      stroke="white"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>

</template>


<script>

  export default {
    name: 'CoreLogo',
    props: {
      src: {
        type: String,
        default: '',
      },
    },
    computed: {
      image() {
        return this.src && this.src.length ? this.src : null;
      },
    },
  };

</script>


<style scoped>

  .phiedu-core-logo {
    display: inline-block;
    width: 48px;
    height: 48px;
    vertical-align: middle;
  }

  .core-logo-img {
    max-width: 100%;
    height: auto;
  }

</style>
