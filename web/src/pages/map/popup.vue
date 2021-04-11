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
            :href="api_url + `/en/josm_proxy?load_object?objects=n${elem.id}`"
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
            :href="api_url + `/en/josm_proxy?load_object?objects=w${elem.id}`"
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
            :href="
              api_url +
              `/en/josm_proxy?import?url=${remote_url_read}/api/0.6/${elem.type}/${elem.id}/full`
            "
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
            v-on:click.stop.prevent="editor(uuid)"
            class="editor_edit"
            :title="
              $t('Edit Object with {where}', {
                where: $t('online Osmose Editor'),
              })
            "
          >
            edit</a
          >
          <br />
          <div v-for="fix in elem.fixes" :key="fix.num" class="fix">
            <div class="fix_links">
              <a
                :href="
                  api_url +
                  '/en/josm_proxy?import?url=' +
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
                v-on:click.stop.prevent="editor(uuid, fix.num)"
                class="editor_fix"
                :title="
                  $t('Load the fix in {where}', {
                    where: $t('online Osmose Editor'),
                  })
                "
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
                  api_url +
                  '/en/josm_proxy?import?url=' +
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
          :href="
            api_url +
            `/en/josm_proxy?load_and_zoom?left=${minlon}&bottom=${minlat}&right=${maxlon}&top=${maxlat}`
          "
          target="hiddenIframe"
          class="josm"
          :title="$t('Edit the area on {where}', { where: 'JOSM' })"
        >
          josm-zone</a
        >
        <a
          :href="`../error/${uuid}`"
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
              v-on:click.stop.prevent="doc(item, classs)"
              :title="$t('Help')"
            >
              ℹ
            </a>
            <a
              class="false_positive btn btn-danger btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              v-on:click="setFalsePositive(uuid)"
              :title="
                $t('false positive') +
                ' - ' +
                $t(
                  'Report the issue as improper, if according to you is not an issue. The issue will not be displayed to anyone more.'
                )
              "
            >
              ✘
            </a>
            <a
              class="corrected btn btn-success btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              v-on:click="setDone(uuid)"
              :title="
                $t('corrected') +
                ' - ' +
                $t(
                  'After issue fixed on the OSM data, mark it as done. May also disappear automatically on next check if no more issue.'
                )
              "
            >
              ✔
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

import ExternalVueAppEvent from "../../ExternalVueAppEvent.js";

export default Vue.extend({
  props: ["main_website", "remote_url_read", "layerMarker"],
  data() {
    return {
      status: "clean",
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
    };
  },
  computed: {
    api_url: () =>
      (API_URL.startsWith("http") ? "" : location.protocol) + API_URL,
    classs: function () {
      return this.class;
    },
  },
  mounted() {
    ExternalVueAppEvent.$on("popup-status", (status) => {
      this.status = status;
    });
    ExternalVueAppEvent.$on("popup-load", this.load);
  },
  methods: {
    load(uuid) {
      fetch(API_URL + `/api/0.3/issue/${uuid}?langs=auto`, {
        headers: new Headers({
          "Accept-Language": this.$route.params.lang,
        }),
      })
        .then((response) => response.json())
        .then((response) => {
          Object.assign(this, response);
          this.status = "fill";

          this.$nextTick(() => {
            this.layerMarker._setPopup(response);
          });
        })
        .catch((error) => {
          this.error = error.message;
          this.status = "error";
        });
    },
    setDone(uuid) {
      fetch(API_URL + `/api/0.3/issue/${uuid}/done`);
      this.layerMarker._dismissMarker();
    },
    setFalsePositive(uuid) {
      const message = this.$t(
        "Report the issue as improper, if according to you is not an issue. The issue will not be displayed to anyone more."
      );
      if (confirm(message)) {
        fetch(API_URL + `/api/0.3/issue/${uuid}/false`);
        this.layerMarker._dismissMarker();
      }
    },
    editor(uuid, fix) {
      this.layerMarker._edit(uuid, fix);
    },
    doc(item, classs) {
      this.layerMarker._help(item, classs);
    },
  },
});
</script>

<style>
#map svg.leaflet-tile g image[width="17px"][height="33px"] {
  cursor: pointer;
}
</style>

<style scoped>
.bulle_elem .add b:before {
  content: " + ";
}
.bulle_elem .del b:before {
  content: " - ";
}
.bulle_elem .mod b:before {
  content: " ~ ";
}
</style>
