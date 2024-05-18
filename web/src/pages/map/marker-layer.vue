<template></template>

<script lang="ts">
import { Map } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

export default Vue.extend({
  props: {
    map: {
      type: Object as PropType<Map>,
      required: true,
    },
  },

  mounted(): void {
    this.map.on('load', () => {
      this.map.on('mouseenter', 'markers', () => {
        this.map.getCanvas().style.cursor = 'pointer'
      })

      this.map.on('mouseleave', 'markers', () => {
        this.map.getCanvas().style.cursor = ''
      })
    })
  },

  methods: {
    remove(featureId): void {
      this.map.setFeatureState(
        { source: 'markers', sourceLayer: 'issues', id: featureId },
        { hidden: true }
      )
    },
  },
})
</script>
