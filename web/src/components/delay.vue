<template>
  <component :is="tag" :class="classs" :style="style">
    <slot />
  </component>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    tag: {
      type: String,
      default: 'span',
    },
    warning: {
      type: Number,
      default: 1.05,
    },
    error: {
      type: Number,
      default: 2.05,
    },
    v: {
      type: Number,
      default: undefined,
    },
    opacity: {
      type: Number,
      default: 1,
    },
  },

  computed: {
    classs(): string {
      return this.v > this.error
        ? 'delay-error'
        : this.v > this.warning
        ? 'delay-warning'
        : null
    },

    style(): string {
      return `background-opacity: ${this.opacity}`
    },
  },
})
</script>

<style scoped>
.delay-warning {
  background: orange !important;
}
.delay-error {
  background: red !important;
}
</style>
