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

<script lang="ts">
import Vue, { PropType } from 'vue'

import { Tag } from '../types'

type KVLink = Tag & {
  vlink: string
}

export default Vue.extend({
  props: {
    tags: {
      type: Array as PropType<KVLink[]>,
      required: true,
    },
  },

  methods: {
    sortObject(o: KVLink[]): KVLink[] {
      // Clone the array as workaround infinite loop on sort
      return [...o].sort((a, b) => (a.k === b.k ? 0 : a.k < b.k ? -1 : 1))
    },
  },
})
</script>
