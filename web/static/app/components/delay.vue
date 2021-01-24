<script>
import Vue from "vue";

export default Vue.extend({
  props: {
    v: null,
    opacity: { default: 1 },
  },
  render: function (createElement) {
    if (this.v) {
      return createElement(
        this.$vnode.data.tag,
        {
          class:
            this.v > 2.05
              ? "delay-error"
              : this.v > 1.05
              ? "delay-warning"
              : null,
          attrs: {
            style: `background-opacity: ${this.opacity}`,
          },
        },
        this.$slots.default
      );
    } else {
      return createElement(this.$vnode.data.tag);
    }
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
