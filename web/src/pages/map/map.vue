<template>
  <div id="map"></div>
</template>

<script lang="ts">
import 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-plugins/control/Permalink'
import '@maplibre/maplibre-gl-leaflet'

import '../../../static/map/Location'
import 'leaflet-control-geocoder/src/index'
import 'leaflet-control-geocoder/Control.Geocoder.css'
import 'leaflet-loading'
import 'leaflet-loading/src/Control.Loading.css'

import Vue from 'vue'

import { mapBases, mapOverlay, glStyle } from '../../../static/map/layers'
import OsmoseHeatmap from '../../../static/map/Osmose.Heatmap'
import OsmoseMarker from '../../../static/map/Osmose.Marker'
import { controlLayers } from '../../../static/map/ControlLayers'
import { Map as MapGl } from 'maplibre-gl'

export default Vue.extend({
  props: {
    itemState: {
      type: Object,
      required: true,
    },
    mapState: {
      type: Object,
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
    // Map
    var gl = L.maplibreGL({style: glStyle, interactive: true})
    const map = L.map('map', {
      center: new L.LatLng(this.mapState.lat, this.mapState.lon),
      zoom: this.mapState.zoom,
      layers: [gl],
      worldCopyJump: true,
    })
    this.$emit('set-map', map)

    const mapGl: MapGl = gl.getMaplibreMap()

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

    // Widgets
    map.addControl(
      L.control.scale({
        position: 'bottomleft',
      })
    )

    mapGl.on('load', () => {
      this.markerLayer = new OsmoseMarker(
        mapGl,
        this.itemState,
        // FIXME - Hardcode legacy to avoid waiting for JSON to init the map
        'https://www.openstreetmap.org/'
      )
      this.markerLayer.addTo(map)

      this.heatmapLayer = new OsmoseHeatmap(
        mapGl,
      )
      this.heatmapLayer.addTo(map)

      // Control Layer
      map.addControl(controlLayers(mapGl, mapBases, mapOverlay))

      this.$emit('set-marker-layer', this.markerLayer)

      this.updateLayer()
    })
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
