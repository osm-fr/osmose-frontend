<script lang="ts">
import Vue, { PropType } from 'vue'

export default Vue.extend({
  props: {
    params: {
      type: Object as PropType<{ [key: string]: any }>,
      default: () => {},
    },
  },

  render(createElement) {
    var text = this.$slots?.default?.at(0)?.text
    if (text) {
      text = text
        .replace(/(\r\n|\n|\r)/gm, ' ')
        .replace(/ +/gm, ' ')
        .trim()
    }
    return createElement('span', {}, [this.$t(text, this.params)])
  },
})
</script>
