<template>
  <div id="popupTpl">
    <div v-if="status == 'clean'"></div>
    <div v-if="status == 'error'">{{ error }}</div>
    <div v-if="status == 'loading'">
      <center>
        <img src="~../../../static/images/throbbler.gif" alt="downloading" />
      </center>
    </div>
    <div v-if="status == 'fill'">
      <div class="bulle_msg">
        <div class="bulle_err">
          <b>{{ title.auto }}</b>
          <br />
          <span v-if="subtitle">{{ subtitle.auto }}</span>
        </div>
        <div
          v-for="elem in elems"
          :key="`${elem.type}/${elem.id}`"
          class="bulle_elem"
        >
          <template v-if="!elem.infos">
            <b>
              <a
                target="_blank"
                :href="main_website + `${elem.type}/${elem.id}`"
                :title="$t('Show Object on {where}', { where: main_website })"
              >
                {{ elem.type }} {{ elem.id }}</a
              >
            </b>
          </template>
          <a
            v-if="elem.type == 'relation'"
            target="_blank"
            :href="`http://polygons.openstreetmap.fr/?id=${elem.id}`"
          >
            analyser
          </a>
          <a
            v-if="elem.type == 'node'"
            :href="`http://localhost:8111/load_object?objects=n${elem.id}`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'node'"
            :href="main_website + `edit?editor=id&node=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            v-if="elem.type == 'way'"
            :href="`http://localhost:8111/load_object?objects=w${elem.id}`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'way'"
            :href="main_website + `edit?editor=id&way=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            v-if="elem.type == 'relation'"
            :href="`http://localhost:8111/import?url=${remote_url_read}api/0.6/${elem.type}/${elem.id}/full`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'relation'"
            :href="main_website + `edit?editor=id&relation=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            href="#"
            class="editor_edit"
            :title="
              $t('Edit Object with {where}', {
                where: $t('online Osmose Editor'),
              })
            "
            @click.stop.prevent="editor(uuid)"
          >
            edit</a
          >
          <br />
          <div v-for="fix in elem.fixes" :key="fix.num" class="fix">
            <div class="fix_links">
              <a
                :href="
                  'http://localhost:8111/import?url=' +
                  api_url +
                  `/api/0.3/issue/${uuid}/fix/${fix.num}`
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Load the fix in {where}', { where: 'JOSM' })"
              >
                fix-josm</a
              >
              <a
                href="#"
                class="editor_fix"
                :title="
                  $t('Load the fix in {where}', {
                    where: $t('online Osmose Editor'),
                  })
                "
                @click.stop.prevent="editor(uuid, fix.num)"
              >
                fix-edit</a
              >
            </div>
            <div v-for="o in fix.add" :key="o.k" class="add">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.mod" :key="o.k" class="mod">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.del" :key="o.k" class="del">
              <b>{{ o.k }}</b>
            </div>
          </div>
          <div v-for="tag in elem.tags" :key="tag.k">
            <b>{{ tag.k }}</b> =
            <a v-if="tag.vlink" :href="tag.vlink" target="popup_tag2link">
              {{ tag.v }}
            </a>
            <span v-else>
              {{ tag.v }}
            </span>
          </div>
        </div>
        <div v-for="fix in new_elems" :key="fix.num" class="bulle_elem">
          <div class="fix">
            <div class="fix_links">
              <a
                :href="
                  'http://localhost:8111/import?url=' +
                  api_url +
                  `/api/0.3/issue/${uuid}/fix/${fix.num}`
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Add the new object in {where}', { where: 'JOSM' })"
              >
                fix-josm</a
              >
            </div>
            <div v-for="o in fix.add" :key="o.k" class="add">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.mod" :key="o.k" class="mod">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.del" :key="o.k" class="del">
              <b>{{ o.k }}</b>
            </div>
          </div>
        </div>
      </div>
      <div class="bulle_verif">
        <a
          :href="main_website + `?mlat=${lat}&mlon=${lon}#map=18/${lat}/${lon}`"
          target="popup_osm"
          :title="$t('Show the area on {where}', { where: main_website })"
        >
          osm-show</a
        >
        <a
          :href="main_website + `edit#map=18/${lat}/${lon}`"
          target="_blank"
          :title="$t('Edit the area on {where}', { where: main_website })"
        >
          iD-zone</a
        >
        <a
          :href="`http://localhost:8111/load_and_zoom?left=${minlon}&bottom=${minlat}&right=${maxlon}&top=${maxlat}`"
          target="hiddenIframe"
          class="josm"
          :title="$t('Edit the area on {where}', { where: 'JOSM' })"
        >
          josm-zone</a
        >
        <a
          :href="`../issue/${uuid}`"
          target="_blank"
          :title="$t('Issue details')"
        >
          <translate>details</translate></a
        >
      </div>
      <div id="bulle_footer">
        <div id="bulle_maj">
          <span :title="$t('Report based on data from date')">
            <translate>Issue reported on:</translate> {{ b_date }}
          </span>
        </div>
        <div id="bulle_button">
          <div class="btn-group" role="group">
            <a
              class="popup_help btn btn-info btn-sm"
              role="button"
              href="#"
              :title="$t('Help')"
              @click.stop.prevent="doc(item, classs)"
            >
              ℹ
            </a>
            <a
              class="false_positive btn btn-danger btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              :title="
                $t('false positive') +
                ' - ' +
                $t(
                  'Report the issue as improper, if it is not an issue according to you. The issue will not be displayed to anyone anymore.'
                )
              "
              @click="setFalsePositive(uuid)"
            >
              ✘
            </a>
            <a
              class="corrected btn btn-success btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              :title="
                $t('corrected') +
                ' - ' +
                $t(
                  'After fixing the issue in the OSM data, mark it as done. It will also disappear automatically on the next check.'
                )
              "
              @click="setDone(uuid)"
            >
              ✔
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Popup } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

import confirmFalsePositive from '../../components/confirmFalsePositive.vue'
import ExternalVueAppEvent from '../../ExternalVueAppEvent'
import { Elem, Fix } from '../../types'

export default Vue.extend({
  mixins: [confirmFalsePositive],

  props: {
    main_website: {
      type: String,
      required: true,
    },
    remote_url_read: {
      type: String,
      required: true,
    },
    markerLayer: {
      type: Object as PropType<Object | null>,
      default: null,
    },
  },

  data(): {
    status: 'clean' | 'error' | 'loading' | 'fill'
    error?: string
    uuid?: string
    item?: number
    class?: number
    title?: string
    subtitle?: string
    b_date?: string
    elems?: Elem[]
    new_elems?: Elem[]
    lon?: number
    lat?: number
    minlat?: number
    maxlat?: number
    minlon?: number
    maxlon?: number
  } {
    return {
      status: 'clean',
      error: null,
      uuid: null,
      item: null,
      class: null,
      title: null,
      subtitle: null,
      b_date: null,
      elems: [],
      new_elems: [],
      lon: null,
      lat: null,
      minlat: null,
      maxlat: null,
      minlon: null,
      maxlon: null,
    }
  },

  computed: {
    api_url(): string {
      return (API_URL.startsWith('http') ? '' : location.protocol) + API_URL
    },

    classs(): string {
      return this.class
    },
  },

  mounted(): void {
    ExternalVueAppEvent.$on('popup-status', (status) => {
      this.status = status
    })
    ExternalVueAppEvent.$on('popup-load', (event) =>
      this.load(event.uuid, event.popup)
    )
  },

  methods: {
    load(uuid: string, popop: Popup): void {
      fetch(API_URL + `/api/0.3/issue/${uuid}?langs=auto`, {
        headers: new Headers({
          'Accept-Language': this.$route.params.lang,
        }),
      })
        .then((response) => response.json())
        .then((response) => {
          Object.assign(this, response)
          this.status = 'fill'
          popop.setLngLat([this.lon, this.lat])

          this.$nextTick(() => {
            this.markerLayer._setPopup(response)
          })
        })
        .catch((error) => {
          this.error = error.message
          this.status = 'error'
        })
    },

    setDone(uuid: string): void {
      fetch(API_URL + `/api/0.3/issue/${uuid}/done`)
      this.markerLayer._dismissMarker()
    },

    setFalsePositive(uuid: string): void {
      if (this.confirmeFalsePositive(uuid)) {
        fetch(API_URL + `/api/0.3/issue/${uuid}/false`)
        this.markerLayer._dismissMarker()
      }
    },

    editor(uuid: string, fix: Fix): void {
      this.$emit('fix-edit', { uuid, fix })
    },

    doc(item: number, classs: number): void {
      this.markerLayer._help(item, classs)
    },
  },
})
</script>

<style>
.maplibregl-popup {
  will-change: unset; /* Overide MapLibre CSS to avoid blury popup text */
}

.maplibregl-popup-content {
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.4);
  border-radius: 12px;
}

.maplibregl-popup-content .btn {
  color: #fff;
}
.maplibregl-popup-content .bulle_msg a,
.maplibregl-popup-content .bulle_verif a {
  text-decoration: underline;
}
</style>

<style scoped>
.bulle_msg {
  min-width: 200px;
  max-height: 200px;
  overflow: auto;
  word-wrap: break-word;
}
.bulle_msg div.closebubble {
  float: right;
  color: #eeeeee;
  font-weight: bold;
  background-color: #aaaaaa;
  margin-right: 2px;
  text-decoration: none;
}
.bulle_msg div.closebubble a:link,
.bulle_msg div.closebubble a:visited {
  color: #eeeeee;
}
.bulle_msg div.closebubble a:hover {
  color: #000000;
}
.bulle_msg div.help {
  background-color: #0083ff;
}
.bulle_msg div.help a:hover {
  color: #d1d1d1;
}

.bulle_err,
a.bulle_err:link,
a.bulle_err:visited,
a.bulle_err:hover {
  color: #ff5555;
}

.bulle_elem {
  direction: ltr;
}

.bulle_elem,
.bulle_elem a:link,
.bulle_elem a:visited {
  color: #5555ff;
}
.bulle_elem a:hover {
  color: #5555ff;
}

.bulle_elem .fix {
  border: solid 1px lightgray;
}
.bulle_elem .fix_links {
  float: right;
}
.bulle_elem .fix .add {
  color: green;
}
.bulle_elem .fix .mod {
  color: darkorange;
}
.bulle_elem .fix .del {
  color: red;
}

.bulle_verif {
  font-size: 90%;
}
.bulle_verif a:link,
.bulle_verif a:visited,
.bulle_verif a:hover {
  color: #55aa55;
}

#bulle_footer {
  display: table;
  width: 100%;
}

#bulle_maj {
  display: table-cell;
  font-size: 80%;
  vertical-align: top;
}

#bulle_button {
  display: table-cell;
  float: right;
  padding-top: 5px;
  padding-left: 5px;
}
html[dir='rtl'] #bulle_button {
  float: left;
  padding-left: 0px;
  padding-right: 5px;
}

#bulle_button .btn-group {
  direction: ltr;
}

.bulle_elem .add b:before {
  content: ' + ';
}
.bulle_elem .del b:before {
  content: ' - ';
}
.bulle_elem .mod b:before {
  content: ' ~ ';
}
</style>
