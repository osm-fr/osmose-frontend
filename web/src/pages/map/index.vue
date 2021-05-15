<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div>
      <top
        :languages_name="languages_name"
        :user="user"
        :user_error_count="user_error_count"
        :timestamp="timestamp"
      />
      <items
        ref="items"
        :menu="menu"
        :original_tags="tags"
        :categories="categories"
        :item_levels="item_levels"
        :error="error"
      />
      <doc v-on:hide-item-markers="onHideItemMarkers($event)" />
      <div id="map"></div>
      <editor :main_website="main_website" :user="user" :editor="editor" />
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        :layerMarker="layerMarker"
      />
    </div>
  </div>
</template>

<script>
// --- Legacy
import { initMap } from "../../../static/map/map.js";

import "leaflet";
import "leaflet/dist/leaflet.css";

import "../../../static/map/style.css";
import "../../../static/images/markers/markers-l.css";

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop;
// --- End Legacy

import VueParent from "../Parent.vue";
import Top from "./top.vue";
import Items from "./items.vue";
import Doc from "./doc.vue";
import Editor from "./editor.vue";
import Popup from "./popup.vue";

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
      layerMarker: null,
      editor: null,
      menu: null,
      item_levels: {},
    };
  },
  components: {
    Top,
    Items,
    Doc,
    Editor,
    Popup,
  },
  mounted() {
    // FIXME - Hardcode legacy to avoid waiting for JSON to init the map
    window.remoteUrlRead = "https://www.openstreetmap.org/";
    const a = initMap();
    this.menu = a[0];
    this.layerMarker = a[1];
    this.editor = a[2];

    this.setData();
  },
  watch: {
    $route(to, from) {
      if (to.params.lang != from.params.lang) {
        this.setData();
      }
    },
  },
  methods: {
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

          this.$nextTick(() => {
            this.menu.init();
          });
        }
      );
    },
    onHideItemMarkers(disabled_item) {
      this.$refs.items.toggle_item(disabled_item, false);
    }
  },
});
</script>
