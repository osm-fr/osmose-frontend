<template>
  <div id="map"></div>
</template>

<script lang="ts">
import MaplibreGeocoder from '@maplibre/maplibre-gl-geocoder'
import {
  Map,
  NavigationControl,
  ScaleControl,
  GeolocateControl,
} from 'maplibre-gl'
import Vue from 'vue'

import ControlLayers from '../../../static/map/ControlLayers'
import { mapBases, mapOverlay, glStyle } from '../../../static/map/layers'
import OsmoseHeatmap from '../../../static/map/Osmose.Heatmap'
import OsmoseMarker from '../../../static/map/Osmose.Marker'

import '../../../static/map/ControlLayers.css'
import 'maplibre-gl/dist/maplibre-gl.css'
import '@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css'

export default Vue.extend({
  props: {
    itemState: {
      type: Object,
      required: true,
    },
    issueUuid: {
      type: String,
      default: undefined,
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
    const map = new Map({
      container: 'map',
      center: [this.mapState.lon, this.mapState.lat],
      zoom: this.mapState.zoom,
      style: glStyle,
      hash: 'loc',
    })
    this.$emit('set-map', map)
    map.addControl(new NavigationControl(), 'top-left')
    map.addControl(new ScaleControl())
    map.addControl(
      new GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true,
        },
      }),
      'top-left'
    )

    const geocoderApi = {
      forwardGeocode: async (config) => {
        const features = []
        try {
          const request = `https://nominatim.openstreetmap.org/search?q=${config.query}&format=geojson&polygon_geojson=1&addressdetails=1`
          const response = await fetch(request)
          const geojson = await response.json()
          for (const feature of geojson.features) {
            const center = [
              feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
              feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2,
            ]
            const point = {
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: center,
              },
              place_name: feature.properties.display_name,
              properties: feature.properties,
              text: feature.properties.display_name,
              place_type: ['place'],
              center,
            }
            features.push(point)
          }
        } catch (e) {
          console.error(`Failed to forwardGeocode with error: ${e}`)
        }

        return {
          features,
        }
      },
    }
    map.addControl(
      new MaplibreGeocoder(geocoderApi, {
        maplibregl: map,
        collapsed: true,
      }),
      'top-left'
    )

    // map.addControl(
    //   L.Control.loading({
    //     separate: true,
    //   })
    // )

    // Control Layer
    map.addControl(new ControlLayers(mapBases, mapOverlay), 'top-right')

    map.on('load', () => {
      this.markerLayer = new OsmoseMarker(
        map,
        this.issueUuid,
        (uuid) => {
          this.$emit('update-issue-uuid', uuid)
        },
        // FIXME - Hardcode legacy to avoid waiting for JSON to init the map
        'https://www.openstreetmap.org/'
      )
      this.$emit('set-marker-layer', this.markerLayer)

      this.heatmapLayer = new OsmoseHeatmap(map)

      this.updateLayer()
    })

    map.on('moveend', function () {
      const zoom = Math.round(map.getZoom())
      if (zoom !== map.getZoom()) {
        map.setZoom(zoom)
      }
    })

    map.scrollZoom.setWheelZoomRate(1)
  },

  methods: {
    updateLayer(): void {
      const state = Object.assign({}, this.itemState)

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
