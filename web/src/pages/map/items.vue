<template>
  <div id="menu">
    <a href="#" id="togglemenu" v-on:click.stop.prevent="leafletSideBar.hide()"
      >☰</a
    >
    <div v-if="error">{{ error }}</div>
    <form v-else action="#">
      <div v-if="need_zoom" id="need_zoom">
        <translate>Zoom in to see issues.</translate>
      </div>
      <template v-else>
        <slot></slot>
      </template>
    </form>
  </div>
</template>

<script>
import Vue from "vue";

import SidebarToggle from "../../../static/map/SidebarToggle.js";

export default Vue.extend({
  props: ["error", "map", "mapState"],
  data() {
    return {
      leafletSideBar: null,
    };
  },
  watch: {
    map: function () {
      if (this.map) {
        this.leafletSideBar = new SidebarToggle(this.map, "menu", {
          position: "left",
          closeButton: false,
          localStorageProperty: "menu.show",
          toggle: {
            position: "topleft",
            menuText: "☰",
            menuTitle: "Menu",
          },
        });
        this.map.addControl(this.leafletSideBar);
        this.leafletSideBar.show();
      }
    },
  },
  computed: {
    need_zoom() {
      return !(
        this.mapState.zoom >= 7 ||
        (this.mapState.zoom >= 5 && this.mapState.lat > 60) ||
        (this.mapState.zoom >= 4 && this.mapState.lat > 70) ||
        (this.mapState.zoom >= 3 && this.mapState.lat > 75)
      );
    },
  },
});
</script>

<style>
.leaflet-sidebar > #menu {
  padding: 3px 3px 5px 5px;
}
</style>

<style scoped>
div#menu {
  resize: horizontal;
}

div#menu div#need_zoom {
  font-size: 14px;
  font-weight: bold;
  color: #ff0000;
  text-align: center;
}

@media (min-width: 768px) {
  a#togglemenu {
    display: none;
  }
}

@media (max-width: 767px) {
  a#togglemenu {
    position: absolute;
    display: block;
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    color: #000000;
    font-weight: bold;
    line-height: 26px;
    text-align: center;
    text-decoration: none;
    height: 26px;
    width: 26px;
    top: 5px;
    left: 5px;
    z-index: 2;
  }
}
</style>
