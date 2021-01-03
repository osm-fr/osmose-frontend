<template>
  <table v-if="dict">
    <tr v-for="(v, k) in sortObject(dict)" :key="k">
      <td>{{ k }}</td>
      <td>{{ v }}</td>
    </tr>
  </table>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["dict"],
  methods: {
    sortObject(o) {
      return Object.keys(o)
        .sort()
        .reduce((r, k) => ((r[k] = o[k]), r), {});
    },
  },
});
</script>
