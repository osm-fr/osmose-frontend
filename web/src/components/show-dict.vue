<template>
  <table v-if="dict">
    <tr v-for="(v, k) in sortObject(dict)" :key="k">
      <td>{{ k }}</td>
      <td>{{ v }}</td>
    </tr>
  </table>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'

interface KV {
  [key: string]: string
}

export default Vue.extend({
  props: {
    dict: {
      type: Object as PropType<KV>,
      required: true,
    },
  },

  methods: {
    sortObject(o: KV): KV {
      const ret: KV = {}
      return Object.keys(o)
        .sort()
        .reduce((r, k) => ((r[k] = o[k]), r), ret)
    },
  },
})
</script>
