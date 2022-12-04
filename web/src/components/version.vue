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

  render: function (createElement) {
    if (this.v) {
      return createElement(
        this.$vnode?.data?.tag,
        {
          class: this.v !== '' && this.v != this.max ? 'version-warning' : null,
        },
        this.$slots.default
      )
    } else {
      return createElement(this.$vnode?.data?.tag)
    }
  },
})
</script>

<style scoped>
.version-warning {
  background: orange !important;
}
</style>
