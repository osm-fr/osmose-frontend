<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div>
      <top
        :map="map"
        :itemState="itemState"
        :mapState="mapState"
        :languages_name="languages_name"
        :user="user"
        :user_error_count="user_error_count"
        :timestamp="timestamp"
      />
      <items
        ref="items"
        :itemState="itemState"
        :mapState="mapState"
        :map="map"
        :original_tags="tags"
        :categories="categories"
        :item_levels="item_levels"
        :error="error"
      />
      <doc :map="map" v-on:hide-item-markers="onHideItemMarkers($event)" />
      <div id="map"></div>
      <editor
        ref="editor"
        :map="map"
        :main_website="main_website"
        :user="user"
        v-on:issue-done="layerMarker.corrected()"
      />
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        :layerMarker="layerMarker"
        v-on:fix-edit="$refs.editor.load($event.uuid, $event.fix)"
      />
    </div>
  </div>
</template>

<script>
// --- Legacy
import initMap from "../../../static/map/map.js";

import "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-plugins/control/Permalink.js";

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop;
// --- End Legacy

import VueParent from "../Parent.vue";
import Top from "./top.vue";
import Items from "./items.vue";
import Doc from "./doc.vue";
import Editor from "./editor.vue";
import Popup from "./popup.vue";

import "../../../static/map/style.css";
import "../../../static/images/markers/markers-l.css";

export default VueParent.extend({
  data() {
    return {
      error: false,
      languages_name: [],
      user: null,
      user_error_count: null,
      timestamp: null,
      tags: [],
      categories: [],
      main_website: "",
      remote_url_read: "",
      map: null,
      layerMarker: null,
      heatmapLayer: null,
      menu: null,
      item_levels: {},
      itemState: {
        item: "xxxx",
        level: "1",
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
    };
  },
  components: {
    Top,
    Items,
    Doc,
    Editor,
    Popup,
  },
  created() {
    this.initializeItemState();
    this.initializeMapState();
  },
  mounted() {
    // FIXME - Hardcode legacy to avoid waiting for JSON to init the map
    window.remoteUrlRead = "https://www.openstreetmap.org/";
    const a = initMap(this.itemState, this.mapState, this.tileQuery());
    this.map = a[0];
    this.layerMarker = a[1];
    this.heatmapLayer = a[2];

    this.map.on("zoomend moveend", (e) => {
      this.mapState.lat = this.map.getCenter().lat;
      this.mapState.lon = this.map.getCenter().lng;
      this.mapState.zoom = this.map.getZoom();
    });

    // Permalink
    this.permalink = new L.Control.Permalink({
      useLocation: true,
      text: '',
    });
    this.map.addControl(this.permalink);
    this.permalink.on("update", (e) => {
      Object.keys(this.itemState).forEach((k) => {
        if (this.itemState[k] != e.params[k]) {
          this.itemState[k] = e.params[k];
        }
      });
    });

    this.setData();
  },
  watch: {
    $route(to, from) {
      if (to.params.lang != from.params.lang) {
        this.setData();
      }
    },
    itemState: {
      deep: true,
      handler(newItemState) {
        this.saveItemState(newItemState);
        this.updateLayer();
      },
    },
    mapState: {
      deep: true,
      handler(newMapState) {
        this.saveMapState(newMapState);
      },
    },
  },
  methods: {
    getUrlVars() {
      const vars = {};
      let hash;
      if (window.location.href.indexOf("#") >= 0) {
        const hashes = window.location.href
          .slice(window.location.href.indexOf("#") + 1)
          .split("&");
        for (let i = 0; i < hashes.length; i += 1) {
          hash = hashes[i].split("=");
          vars[decodeURIComponent(hash[0])] = decodeURIComponent(hash[1]);
        }
      }
      return vars;
    },
    filter(keys, state) {
      return Object.fromEntries(
        Object.entries(state).filter(
          ([key, val]) => val !== undefined && val != null && keys.includes(key)
        )
      );
    },
    initializeItemState() {
      const keys = Object.keys(this.itemState);

      const urlState = this.filter(keys, this.getUrlVars());

      let localStorageState = {};
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem("itemState")
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem("itemState"))
        );
      }

      Object.assign(this.itemState, localStorageState, urlState);
    },
    initializeMapState() {
      const keys = Object.keys(this.mapState);

      const urlState = this.filter(keys, this.getUrlVars());

      let localStorageState = {};
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem("mapState")
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem("mapState"))
        );
      }

      Object.assign(this.mapState, localStorageState, urlState);
    },
    saveItemState(itemState) {
      localStorage.setItem("itemState", JSON.stringify(itemState));
      this.permalink._update(itemState);
    },
    saveMapState(mapState) {
      localStorage.setItem("mapState", JSON.stringify(mapState));
    },
    tileQuery() {
      const state = Object.assign({}, this.itemState);
      delete state.issue_uuid;

      return Object.entries(state)
        .filter(([k, v]) => v !== undefined && v != null)
        .map(([k, v]) => encodeURIComponent(k) + "=" + encodeURIComponent(v))
        .join("&");
    },
    updateLayer() {
      const query = this.tileQuery();
      this.layerMarker.setURLQuery(query);
      this.heatmapLayer.setURLQuery(query);
    },
    setData() {
      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + ".json" + window.location.search,
        (response) => {
          // Legacy global variables
          window.API_URL = API_URL;

          document.title = "Osmose";
          const description = document.getElementById("description");
          if (description) {
            description.content = this.$t(
              "Control, verification and correction of {project} issues",
              { project: response.main_project }
            );
          }
          const viewport = document.getElementById("viewport");
          if (viewport) {
            viewport.content =
              "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no";
          }
        }
      );
    },
    onHideItemMarkers(disabled_item) {
      this.$refs.items.toggle_item(disabled_item, false);
    },
  },
});
</script>
