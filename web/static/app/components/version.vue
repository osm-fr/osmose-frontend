<template>
  <div :class="v !== '' && v != max ? 'version-warning' : null">
    <slot></slot>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["v", "max"],
});
</script>

<style scoped>
.version-warning {
  background: orange !important;
}
</style>
