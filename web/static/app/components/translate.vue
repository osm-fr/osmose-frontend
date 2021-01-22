<script>
import Vue from "vue";

export default Vue.extend({
  props: {
    params: {
      default: () => {},
    },
  },
  render(createElement) {
    var text = this.$slots.default[0].text;
    text = text
      .replace(/(\r\n|\n|\r)/gm, " ")
      .replace(/ +/gm, " ")
      .trim();
    return createElement("span", {}, [this.$t(text, this.params)]);
  },
});
</script>
