<template></template>

<script lang="ts">
import { Map, Popup } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

import ExternalVueAppEvent from '../../../src/ExternalVueAppEvent'
import osm2geojson from '../../../static/map/osm2geojson'

export default Vue.extend({
  props: {
    map: {
      type: Object as PropType<Map>,
      required: true,
    },
    initialUuid: {
      type: String,
      default: undefined,
    },
    remoteUrlRead: {
      type: String,
      required: true,
    },
  },

  data(): {
    popup: Popup | null
    open_popup?: string | null // uuid
  } {
    return {
      popup: null,
      open_popup: null,
    }
  },

  mounted(): void {
    this.map.on('load', () => {
      this.popup = new Popup({ closeOnClick: false })
        .setMaxWidth('280px')
        .setOffset([0, -24])
        .setDOMContent(document.getElementById('popupTpl'))

      if (this.initialUuid) {
        this._openPopup(this.initialUuid, [0, 0], this)
      }

      this.map.on('mouseenter', 'markers', () => {
        this.map.getCanvas().style.cursor = 'pointer'
      })

      this.map.on('mouseleave', 'markers', () => {
        this.map.getCanvas().style.cursor = ''
      })

      this.map.on('click', 'markers', (e) => {
        e.preventDefault()
        if (e.features[0].properties.uuid) {
          if (this.highlight === e.features[0].properties.uuid) {
            this._closePopup()
          } else {
            this.highlight = e.features[0].properties.uuid
            this.feature_id = e.features[0].id
            this._openPopup(
              e.features[0].properties.uuid,
              e.features[0].geometry.coordinates.slice(),
              e.features[0]
            )
          }
        }
      })

      this.map.on('click', (e) => {
        if (e.defaultPrevented === false) {
          this._closePopup()
        }
      })

      this.popup.on('close', (e) => {
        this.clearOsmLayer()
      })

      this.map.on('zoomstart', () => {
        this.popup.remove()
      })
    })
  },

  methods: {
    _closePopup(): void {
      this.highlight = undefined
      this.$emit('update-issue-uuid', null)
      this.open_popup = undefined
      if (this.popup && this.map) {
        this.popup.remove()
      }
    },

    _openPopup(uuid, lngLat, layer): void {
      if (this.open_popup === uuid) {
        return
      }
      this.open_popup = uuid
      this.$emit('update-issue-uuid', uuid)

      ExternalVueAppEvent.$emit('popup-status', 'loading')
      this.popup.setLngLat(lngLat).addTo(this.map)

      setTimeout(() => {
        if (this.popup.isOpen()) {
          // Popup still open, so download content
          ExternalVueAppEvent.$emit('popup-load', { uuid, popup: this.popup })
          this.layer = layer
        } else {
          ExternalVueAppEvent.$emit('popup-status', 'clean')
        }
      }, 100)
    },

    async _setPopup(data) {
      data.elems_id = data.elems.map((elem) => elem.type + elem.id).join(',')

      ExternalVueAppEvent.$emit('load-doc', {
        item: data.item,
        classs: data['class'],
      })
      // Get the OSM objects
      if (data.elems_id) {
        let shift = -1
        this.clearOsmLayer()
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

    _dismissMarker(): void {
      setTimeout(() => {
        this.corrected()
      }, 200)
    },

    _help(item, classs): void {
      ExternalVueAppEvent.$emit('show-doc', { item, classs })
    },

    corrected(): void {
      this.map.setFeatureState(
        { source: 'markers', sourceLayer: 'issues', id: this.feature_id },
        { hidden: true }
      )

      this._closePopup()
    },

    clearOsmLayer(): void {
      this.map.getSource('osm').setData({
        type: 'FeatureCollection',
        features: [],
      })
    },
  },
})
</script>
