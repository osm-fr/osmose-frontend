<template>
  <div
    :class="v > 2.05 ? 'delay-error' : v > 1.05 ? 'delay-warning' : null"
    :style="`background-opacity: ${opacity}`"
  >
    <slot></slot>
  </div>
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

<style scoped>
.delay-warning {
  background: orange !important;
}
.delay-error {
  background: red !important;
}
</style>
