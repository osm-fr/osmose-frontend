<template>
  <li v-if="object_count" class="save_button">
    <a href="#" @click.stop.prevent="save">
      <translate>Save</translate>
      (<span>{{ object_count }}</span
      >)
    </a>
  </li>
</template>

<script lang="ts">
import Vue from 'vue'

import ExternalVueAppEvent from '../../ExternalVueAppEvent'

export default Vue.extend({
  data(): {
    object_count: number
  } {
    return {
      object_count: 0,
    }
  },

  mounted() {
    ExternalVueAppEvent.$on('editor-count', this.count)
  },

  methods: {
    count(n: number): void {
      this.object_count = n
    },

    save(): void {
      ExternalVueAppEvent.$emit('editor-save')
    },
  },
})
</script>

<style scoped>
.save_button {
  background: #64db64;
}
</style>
