<template>
  <i18n tag="span" :path="text">
    <template v-for="(index, name) in $slots" v-slot:[name]>
      <slot :name="name" />
    </template>
  </i18n>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  data() {
    return {
      text: null,
    };
  },
  mounted() {
    this.text = this.$slots.default[0].children[0].text;
    this.text = this.text
      .replace(/(\r\n|\n|\r)/gm, " ")
      .replace(/ +/gm, " ")
      .trim();
  },
});
</script>
