<template>
  <span :class="v !== '' && v != max ? 'delay-warning' : null">
    <slot></slot>
  </span>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["v", "max"],
});
</script>
