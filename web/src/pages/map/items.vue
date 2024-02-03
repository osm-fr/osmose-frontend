<template>
  <div id="menu">
    <div v-if="error">{{ error }}</div>
    <form v-else action="#">
      <div v-if="need_zoom" id="need_zoom">
        <translate>Zoom in to see issues.</translate>
      </div>
      <template v-else>
        <slot></slot>
      </template>
    </form>
  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'

export default Vue.extend({
  props: {
    error: {
      type: Error as PropType<Error | undefined>,
      default: undefined,
    },
    mapState: {
      type: Object,
      required: true,
    },
  },

  computed: {
    need_zoom(): boolean {
      return !(
        this.mapState.zoom >= 7 ||
        (this.mapState.zoom >= 5 && this.mapState.lat > 60) ||
        (this.mapState.zoom >= 4 && this.mapState.lat > 70) ||
        (this.mapState.zoom >= 3 && this.mapState.lat > 75)
      )
    },
  },
})
</script>

<style scoped>
#menu {
  padding: 3px 3px 5px 5px;
}

div#menu {
  resize: horizontal;
}

div#menu div#need_zoom {
  font-size: 14px;
  font-weight: bold;
  color: #ff0000;
  text-align: center;
}
</style>
