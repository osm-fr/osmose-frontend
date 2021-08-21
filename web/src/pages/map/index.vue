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
      <items ref="items" :mapState="mapState" :map="map" :error="error">
        <items-filters
          :original_tags="tags"
          :itemState="itemState"
          v-on:state-update="itemState = $event"
        />
        <items-list
          :categories="categories"
          :item_levels="item_levels"
          :itemState="itemState"
          v-on:state-update="itemState = $event"
        />
      </items>
      <doc :map="map" v-on:hide-item-markers="onHideItemMarkers($event)" />
      <l-map
        :itemState="itemState"
        :mapState="mapState"
        v-on:set-map="
          map = $event.map;
          markerLayer = $event.markerLayer;
          heatmapLayer = $event.heatmapLayer;
        "
      />
      <editor
        ref="editor"
        :map="map"
        :main_website="main_website"
        :user="user"
        v-on:issue-done="markerLayer.corrected()"
      />
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        :markerLayer="markerLayer"
        v-on:fix-edit="$refs.editor.load($event.uuid, $event.fix)"
      />
    </div>
  </div>
</template>

<script>
import VueParent from "../Parent.vue";
import Top from "./top.vue";
import LMap from "./map.vue";
import Items from "./items.vue";
import ItemsFilters from "./items-filters.vue";
import ItemsList from "./items-list.vue";
import Doc from "./doc.vue";
import Editor from "./editor.vue";
import Popup from "./popup.vue";

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
      markerLayer: null,
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
    LMap,
    Items,
    ItemsFilters,
    ItemsList,
    Doc,
    Editor,
    Popup,
  },
  created() {
    this.initializeItemState();
    this.initializeMapState();
  },
  mounted() {
    this.setData();
  },
  watch: {
    $route(to, from) {
      if (to.params.lang != from.params.lang) {
        this.setData();
      }
    },
    map(newMap, oldMap) {
      if (!oldMap && newMap) {
        this.map.on("zoomend moveend", () => {
          this.mapState.lat = this.map.getCenter().lat;
          this.mapState.lon = this.map.getCenter().lng;
          this.mapState.zoom = this.map.getZoom();
        });

        // Permalink
        this.permalink = new L.Control.Permalink({
          useLocation: true,
          text: "",
        });
        this.map.addControl(this.permalink);
        this.permalink.on("update", (e) => {
          Object.keys(this.itemState).forEach((k) => {
            if (this.itemState[k] != e.params[k]) {
              this.itemState[k] = e.params[k];
            }
          });
        });
      }
    },
    itemState: {
      deep: true,
      handler() {
        this.saveItemState();
      },
    },
    mapState: {
      deep: true,
      handler() {
        this.saveMapState();
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
    saveItemState() {
      localStorage.setItem("itemState", JSON.stringify(this.itemState));
      this.permalink._update(this.itemState);
    },
    saveMapState() {
      localStorage.setItem("mapState", JSON.stringify(this.mapState));
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

.leaflet-active-area {
  position: absolute;
  top: 0px;
  left: 300px;
  right: 300px;
  bottom: 0px;
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

  .leaflet-active-area {
    left: 270px;
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

  .leaflet-active-area {
    left: 285px;
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

  .leaflet-active-area {
    left: 300px;
    right: 300px;
  }
}
</style>
