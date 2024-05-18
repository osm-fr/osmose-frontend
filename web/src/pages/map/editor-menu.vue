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

export default Vue.extend({
  props: {
    object_count: {
      type: Number,
      default: null,
    },
  },

  methods: {
    save(): void {
      this.$emit('editor-save')
    },
  },
})
</script>

<style scoped>
.save_button {
  background: #64db64;
}
</style>
