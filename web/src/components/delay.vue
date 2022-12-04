<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
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

  render: function (createElement) {
    return createElement(
      this.$vnode?.data?.tag,
      {
        class:
          this.v > this.error
            ? 'delay-error'
            : this.v > this.warning
            ? 'delay-warning'
            : null,
        attrs: {
          style: `background-opacity: ${this.opacity}`,
        },
      },
      this.$slots.default
    )
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
