<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div>
      <top
        :languages_name="languages_name"
        :user="user"
        :user_error_count="user_error_count"
        :timestamp="timestamp"
      />
      <items :tags="tags" :categories="categories" />
      <doc />
      <div id="map"></div>
      <editor-component :user="user" />
      <editor :main_website="main_website" />
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup :main_website="main_website" :remote_url_read="remote_url_read" />
    </div>
  </div>
</template>

<script>
// --- Legacy
import $ from "jquery";
import { initMap } from "../../../static/map/map.js";

require("leaflet");
require("leaflet/dist/leaflet.css");

require("../../../static/map/style.css");
require("../../../static/images/markers/markers-l.css");

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop;
window.$ = $;
// --- End Legacy

import Vue from "vue";

import Top from "./top.vue";
import Items from "./items.vue";
import Doc from "./doc.vue";
import EditorComponent from "./editor-component.vue";
import Editor from "./editor.vue";
import Popup from "./popup.vue";

export default Vue.extend({
  data() {
    return {
      languages_name: [],
      user: null,
      user_error_count: null,
      timestamp: null,
      tags: [],
      categories: [],
      main_website: "",
      remote_url_read: "",
    };
  },
  components: {
    Top,
    Items,
    Doc,
    EditorComponent,
    Editor,
    Popup,
  },
  mounted() {
    // FIXME - Hardcode legacy to avoind waiting for JSON to init the map
    window.remoteUrlRead = "https://www.openstreetmap.org/";
    this._menu = initMap();

    this.$refs.topProgress.start();
    this.setData().then(() => {
      this.$refs.topProgress.done();
    });
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
      return fetch(
        API_URL + window.location.pathname + ".json" + window.location.search,
        {
          headers: new Headers({
            "Accept-Language": this.$route.params.lang,
          }),
        }
      )
        .then((response) => response.json())
        .then((response) => {
          // Legacy global variables
          window.itemLevels = response.item_levels;
          window.itemTags = response.item_tags;
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

          Object.assign(this, response);
          this.$nextTick(() => {
            this._menu.init();
          });
        });
    },
  },
});
</script>
