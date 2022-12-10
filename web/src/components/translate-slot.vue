<template>
  <i18n v-if="text" tag="span" :path="text">
    <template v-for="(index, name) in $slots" #[name]>
      <slot :name="name" />
    </template>
  </i18n>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data(): {
    text?: string
  } {
    return {
      text: undefined,
    }
  },

  mounted() {
    const text = this.$slots?.default?.at(0)?.children?.at(0)?.text
    if (text) {
      this.text = text
        .replace(/(\r\n|\n|\r)/gm, ' ')
        .replace(/ +/gm, ' ')
        .trim()
    }
  },
})
</script>
