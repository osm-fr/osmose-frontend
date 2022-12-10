<template>
  <span :class="classs">
    <slot />
  </span>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    v: {
      type: String,
      default: undefined,
    },
    max: {
      type: String,
      default: undefined,
    },
  },

  computed: {
    classs(): string {
      return this.v !== '' && this.v != this.max ? 'version-warning' : null
    },
  },
})
</script>

<style scoped>
.version-warning {
  background: orange !important;
}
</style>
