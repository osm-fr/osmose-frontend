<template>
  <span
    :class="v > 2.05 ? 'delay-error' : v > 1.05 ? 'elay-warning' : null"
    :style="`background-opacity: ${opacity}`"
  >
    <slot></slot>
  </span>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: {
    v: null,
    opacity: { default: 1 },
  },
});
</script>
