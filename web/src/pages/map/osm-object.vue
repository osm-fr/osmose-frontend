<template></template>

<script lang="ts">
import { Map } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

import osm2geojson from '../../../static/map/osm2geojson'

export default Vue.extend({
  props: {
    map: {
      type: Object as PropType<Map>,
      required: true,
    },
    remoteUrlRead: {
      type: String,
      required: true,
    },
  },

  methods: {
    async select(data) {
      data.elems_id = data.elems.map((elem) => elem.type + elem.id).join(',')

      // Get the OSM objects
      if (data.elems_id) {
        this.clear()
        const features = await Promise.all(
          data.elems.map((elem) =>
            fetch(
              elem.type === 'node'
                ? `${this.remoteUrlRead}api/0.6/node/${elem.id}`
                : `${this.remoteUrlRead}api/0.6/${elem.type}/${elem.id}/full`
            )
              .then((response) => response.text())
              .then((str) =>
                new window.DOMParser().parseFromString(str, 'text/xml')
              )
              .then((xml) => osm2geojson(xml).features)
          )
        )
        this.map.getSource('osm').setData({
          type: 'FeatureCollection',
          features: features.flat(),
        })
      }
    },

    clear(): void {
      this.map.getSource('osm').setData({
        type: 'FeatureCollection',
        features: [],
      })
    },
  },
})
</script>
