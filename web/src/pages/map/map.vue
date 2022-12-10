<template>
  <div id="map"></div>
</template>

<script lang="ts">
import 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-plugins/control/Permalink.js'

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop

import 'leaflet-active-area/src/leaflet.activearea.js'
import '../../../static/map/Location.js'
import 'leaflet-control-geocoder/src/index.js'
import 'leaflet-control-geocoder/Control.Geocoder.css'
import 'leaflet-loading'
import 'leaflet-loading/src/Control.Loading.css'

import Vue from 'vue'

import { mapBases, mapOverlay } from '../../../static/map/layers'
import OsmoseHeatmap from '../../../static/map/Osmose.Heatmap'
import OsmoseMarker from '../../../static/map/Osmose.Marker'

export default Vue.extend({
  props: {
    itemState: {
      type: String,
      required: true,
    },
    mapState: {
      type: String,
      required: true,
    },
  },

  data(): {
    markerLayer: Object
    heatmapLayer: Object
  } {
    return {
      markerLayer: null,
      heatmapLayer: null,
    }
  },

  watch: {
    itemState: {
      deep: true,
      handler(): void {
        this.updateLayer()
      },
    },
  },

  mounted(): void {
    // Layers
    this.markerLayer = new OsmoseMarker(
      this.itemState,
      'fakeURL',
      // FIXME - Hardcode legacy to avoid waiting for JSON to init the map
      'https://www.openstreetmap.org/'
    )
    mapOverlay['Osmose Issues'] = this.markerLayer

    this.heatmapLayer = new OsmoseHeatmap(this.itemState, 'fakeURL')
    mapOverlay['Osmose Issues Heatmap'] = this.heatmapLayer

    // Map
    const map = L.map('map', {
      center: new L.LatLng(this.mapState.lat, this.mapState.lon),
      zoom: this.mapState.zoom,
      layers: [mapBases['carto'], this.markerLayer],
      worldCopyJump: true,
    }).setActiveArea('leaflet-active-area', true)

    // Control Layer
    map.addControl(L.control.layers(mapBases, mapOverlay))

    // Widgets

    map.addControl(
      L.control.scale({
        position: 'bottomleft',
      })
    )

    map.addControl(L.control.location())

    const geocode = L.Control.geocoder({
      position: 'topleft',
      showResultIcons: true,
    })
    geocode.markGeocode = function (result) {
      this._map.fitBounds(result.geocode.bbox)
      return this
    }
    map.addControl(geocode)

    map.addControl(
      L.Control.loading({
        separate: true,
      })
    )

    this.$emit('set-map', {
      map,
      markerLayer: this.markerLayer,
      heatmapLayer: this.heatmapLayer,
    })

    this.updateLayer()
  },

  methods: {
    updateLayer(): void {
      const state = Object.assign({}, this.itemState)
      delete state.issue_uuid

      const query = Object.entries(state)
        .filter(([, v]) => v !== undefined && v != null)
        .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
        .join('&')

      this.markerLayer.setURLQuery(query)
      this.heatmapLayer.setURLQuery(query)
    },
  },
})
</script>

<style>
.leaflet-control-layers label {
  margin-bottom: 0px;
}

ul.leaflet-control-geocoder-alternatives {
  width: 60vw;
}
.leaflet-control-geocoder-alternatives a:hover,
.leaflet-control-geocoder-selected {
  background-color: inherit;
}
</style>

<style scoped>
div#map {
  position: absolute;
  top: 23px;
  bottom: 0px;
  left: 0px;
  right: 0px;
}
</style>
