<template>
  <div v-if="showCurrent" class="pannel">
    <a id="togglemenu" href="#" @click.stop.prevent="showCurrent = !showCurrent"
      >×</a
    >
    <slot></slot>
  </div>
</template>

<script lang="ts">
import { Map, PositionAnchor } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

import ToggleControl from '../../../static/map/ToggleControl'

export default Vue.extend({
  props: {
    map: {
      type: Object as PropType<Map | null>,
      default: null,
    },
    showInitial: {
      type: Boolean,
      default: true,
    },
    position: {
      type: String as PropType<PositionAnchor>,
      default: undefined,
      required: false,
    },
    menuText: {
      type: String as PropType<string>,
      default: undefined,
      required: false,
    },
    menuTitle: {
      type: String as PropType<string>,
      default: undefined,
      required: false,
    },
  },

  data(): {
    showCurrent: Boolean
  } {
    return {
      showCurrent: this.showInitial,
    }
  },

  watch: {
    map(): void {
      if (this.map && this.position) {
        const toogleControl = new ToggleControl(
          () => {
            this.showCurrent = !this.showCurrent
          },
          {
            menuText: this.menuText,
            menuTitle: this.menuTitle,
          }
        )
        this.map.addControl(toogleControl, this.position)
      }
    },
  },

  methods: {
    show(): void {
      this.showCurrent = true
    },

    hide(): void {
      this.showCurrent = false
    },
  },
})
</script>

<style scoped>
.pannel {
  font: 13.2px/1.5 'Helvetica Neue', Arial, Helvetica, sans-serif;
  background: white;
  overflow-y: auto;
  resize: horizontal;
}

.pannel:not(:last-child) {
  border-right: 2px solid rgba(0, 0, 0, 0.2);
}

.pannel:not(:first-child) {
  border-left: 2px solid rgba(0, 0, 0, 0.2);
}

@media (min-width: 768px) and (max-width: 991px) {
  .pannel {
    width: 270px;
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .pannel {
    width: 285px;
  }
}

@media (min-width: 1200px) {
  .pannel {
    width: 300px;
  }
}

@media (min-width: 768px) {
  a#togglemenu {
    display: none;
  }
}

@media (max-width: 767px) {
  a#togglemenu {
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
  }
}
</style>
