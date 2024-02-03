<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div>
      <top
        :map="map"
        :item-state="itemState"
        :map-state="mapState"
        :languages_name="languages_name"
        :user="user"
        :user_error_count="user_error_count"
        :timestamp="timestamp"
      />
      <div id="map">
        <items ref="items" :map-state="mapState" :map="map" :error="error">
          <items-filters
            :original_tags="tags"
            :countries="countries"
            :item-state="itemState"
            @state-update="itemState = $event"
          />
          <items-list
            ref="items-list"
            :categories="categories"
            :item_levels="item_levels"
            :item-state="itemState"
            @state-update="itemState = $event"
          />
        </items>
        <doc :map="map" @hide-item-markers="onHideItemMarkers($event)" />
        <l-map
          :item-state="itemState"
          :map-state="mapState"
          @set-map="setMap($event)"
          @set-marker-layer="setMarkerLayer($event)"
        />
        <editor
          ref="editor"
          :map="map"
          :main_website="main_website"
          :user="user"
          @issue-done="markerLayer.corrected()"
        />
      </div>
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        :marker-layer="markerLayer"
        @fix-edit="$refs.editor.load($event.uuid, $event.fix)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { ItemState, LanguagesName, Category } from '../../types'
import VueParent from '../Parent.vue'
import Doc from './doc.vue'
import Editor from './editor.vue'
import ItemsFilters from './items-filters.vue'
import ItemsList from './items-list.vue'
import Items from './items.vue'
import LMap from './map.vue'
import Popup from './popup.vue'
import Top from './top.vue'

interface MapState {
  lat: number
  lon: number
  zoom: number
}

export default VueParent.extend({
  data(): {
    error?: string
    languages_name: LanguagesName
    user: string
    user_error_count: { [level: number]: number }
    timestamp: string
    tags: string[]
    countries: string[]
    categories: Category[]
    main_website: string
    remote_url_read: string
    map: Object
    markerLayer: Object
    item_levels: {}
    itemState: ItemState
    mapState: MapState
  } {
    return {
      error: undefined,
      languages_name: {},
      user: null,
      user_error_count: null,
      timestamp: null,
      tags: [],
      countries: [],
      categories: [],
      main_website: '',
      remote_url_read: '',
      map: null,
      markerLayer: null,
      item_levels: {},
      itemState: {
        item: 'xxxx',
        level: '1',
        // TODO filtrer on existing tagss
        tags: null,
        fixable: null,
        class: null,
        useDevItem: null,
        source: null,
        username: null,
        country: null,
        issue_uuid: null,
      },
      mapState: {
        lat: 46.97,
        lon: 2.75,
        zoom: 16,
      },
    }
  },

  components: {
    Top,
    LMap,
    Items,
    ItemsFilters,
    ItemsList,
    Doc,
    Editor,
    Popup,
  },

  created(): void {
    document.querySelector(
      'head'
    ).innerHTML += `<link rel="stylesheet" href="${API_URL}/assets/sprites.css" type="text/css"/>`
    this.initializeItemState()
    this.initializeMapState()
  },

  mounted(): void {
    this.setData()
  },

  watch: {
    $route(to, from): void {
      if (to.params.lang != from.params.lang) {
        this.setData()
      }
    },

    map(newMap: Object, oldMap: Object): void {
      if (!oldMap && newMap) {
        this.map.on('zoomend moveend', () => {
          this.mapState.lat = this.map.getCenter().lat
          this.mapState.lon = this.map.getCenter().lng
          this.mapState.zoom = this.map.getZoom()
        })

        // Permalink
        this.permalink = new L.Control.Permalink({
          useLocation: true,
          text: '',
        })
        this.map.addControl(this.permalink)
        this.permalink.on('update', (e) => {
          Object.keys(this.itemState).forEach((k) => {
            if (this.itemState[k] != e.params[k]) {
              this.itemState[k] = e.params[k]
            }
          })
        })
      }
    },

    itemState: {
      deep: true,
      handler(): void {
        this.saveItemState()
      },
    },

    mapState: {
      deep: true,
      handler(): void {
        this.saveMapState()
      },
    },
  },

  methods: {
    getUrlVars(): { [key: string]: string } {
      const vars = {}
      let hash: string[]
      if (window.location.href.indexOf('#') >= 0) {
        const hashes = window.location.href
          .slice(window.location.href.indexOf('#') + 1)
          .split('&')
        for (let i = 0; i < hashes.length; i += 1) {
          hash = hashes[i].split('=')
          vars[decodeURIComponent(hash[0])] = decodeURIComponent(hash[1])
        }
      }
      return vars
    },

    filter(keys: string[], state): void {
      return Object.fromEntries(
        Object.entries(state).filter(
          ([key, val]) => val !== undefined && val != null && keys.includes(key)
        )
      )
    },

    initializeItemState(): void {
      const keys = Object.keys(this.itemState)

      const urlState = this.filter(keys, this.getUrlVars())

      let localStorageState = {}
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem('itemState')
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem('itemState'))
        )
      }

      Object.assign(this.itemState, localStorageState, urlState)
    },

    initializeMapState(): void {
      const keys = Object.keys(this.mapState)

      const urlState = this.filter(keys, this.getUrlVars())

      let localStorageState = {}
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem('mapState')
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem('mapState'))
        )
      }

      Object.assign(this.mapState, localStorageState, urlState)
    },

    saveItemState(): void {
      localStorage.setItem('itemState', JSON.stringify(this.itemState))
      this.permalink._update(this.itemState)
    },

    saveMapState(): void {
      localStorage.setItem('mapState', JSON.stringify(this.mapState))
    },

    setData(): void {
      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + '.json' + window.location.search,
        (response) => {
          // Legacy global variables
          window.API_URL = API_URL

          document.title = 'Osmose'
          const description = document.getElementById('description')
          if (description) {
            description.content = this.$t(
              'Control, verification and correction of {project} issues',
              { project: response.main_project }
            )
          }
          const viewport = document.getElementById('viewport')
          if (viewport) {
            viewport.content =
              'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
          }
        }
      )
    },

    onHideItemMarkers(disabled_item): void {
      this.$refs['items-list'].toggle_item(disabled_item, false)
    },

    setMap(map): void {
      this.map = map
    },

    setMarkerLayer(markerLayer): void {
      this.markerLayer = markerLayer
    },
  },
})
</script>

<style>
body {
  margin: 0;
  font-family: arial, helvetica, sans-serif;
}

.bold {
  font-weight: bold;
}

@media (max-width: 640px) {
  .leaflet-touch .josm {
    display: none;
  }
}

.leaflet-sidebar {
  z-index: 1010;
}

@media (min-width: 768px) and (max-width: 991px) {
  .leaflet-sidebar {
    width: 270px;
  }

  .leaflet-sidebar.left.visible ~ .leaflet-left {
    left: 270px;
  }

  .leaflet-sidebar.right.visible ~ .leaflet-right {
    right: 270px;
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .leaflet-sidebar {
    width: 285px;
  }

  .leaflet-sidebar.left.visible ~ .leaflet-left {
    left: 285px;
  }

  .leaflet-sidebar.right.visible ~ .leaflet-right {
    right: 285px;
  }
}

@media (min-width: 1200px) {
  .leaflet-sidebar {
    width: 300px;
  }

  .leaflet-sidebar.left.visible ~ .leaflet-left {
    left: 300px;
  }

  .leaflet-sidebar.right.visible ~ .leaflet-right {
    right: 300px;
  }
}
</style>

<style scoped>
a:link,
a:visited {
  color: rgb(0, 123, 255);
}

div#map {
  position: absolute;
  top: 23px;
  bottom: 0px;
  left: 0px;
  right: 0px;
}
</style>
