<template>
  <table v-if="tags">
    <tr v-for="kv in sortObject(tags)" :key="kv.k">
      <td>{{ kv.k }}</td>
      <td v-if="kv.v">{{ kv.v }}</td>
      <td>
        <a v-if="kv.vlink" :href="kv.vlink">{{ kv.vlink }}</a>
      </td>
    </tr>
  </table>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["tags"],
  methods: {
    sortObject(o) {
      return o.sort((a, b) => (a.k === b.k ? 0 : a.k < b.k ? -1 : 1));
    },
  },
});
</script>
