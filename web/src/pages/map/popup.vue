<template>
  <div id="popupTpl" style="display: none">
    <template v-pre>{{={% %}=}}</template>
    <div id="popup-{%id%}">
      <div class="bulle_msg">
        <div class="bulle_err">
          <b>{%title.auto%}</b>
          <br />
          {%subtitle.auto%}
        </div>
        {%#elems%}
        <div class="bulle_elem">
          {%^infos%}
          <b>
            <a
              target="_blank"
              :href="main_website + '{%type%}/{%id%}'"
              :title="$t('Show Object on {where}', { where: main_website })"
            >
              {%type%} {%id%}
            </a>
          </b>
          {%/infos%} {%#relation%}
          <a
            target="_blank"
            href="http://polygons.openstreetmap.fr/?id={%id%}"
          >
            analyser
          </a>
          {%/relation%} {%#node%}
          <a
            :href="api_url + '/en/josm_proxy?load_object?objects=n{%id%}'"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm
          </a>
          <a
            :href="main_website + 'edit?editor=id&node={%id%}'"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD
          </a>
          {%/node%} {%#way%}
          <a
            :href="api_url + '/en/josm_proxy?load_object?objects=w{%id%}'"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm
          </a>
          <a
            :href="main_website + 'edit?editor=id&way={%id%}'"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD
          </a>
          {%/way%} {%#relation%}
          <a
            :href="api_url + '/en/josm_proxy?import?url=' + remote_url_read + '/api/0.6/{%type%}/{%id%}/full'"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
            :onclick="`$.get('` + api_url + `/en/josm_proxy?zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}'); return true;`"
          >
            josm
          </a>
          <a
            :href="main_website + 'edit?editor=id&relation={%id%}'"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD
          </a>
          {%/relation%}
          <a
            href="#"
            class="editor_edit"
            data-type="{%type%}"
            data-id="{%id%}"
            data-error="{%uuid%}"
            :title="
              $t('Edit Object with {where}', {
                where: $t('online Osmose Editor'),
              })
            "
          >
            edit
          </a>
          <br />
          {%#fixes%}
          <div class="fix">
            <div class="fix_links">
              <a
                :href="
                  api_url + '/en/josm_proxy?import?url=' +
                  api_url +
                  '/api/0.3/issue/{%uuid%}/fix/{%num%}'
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Load the fix in {where}', { where: 'JOSM' })"
                :onclick="`$.get('` + api_url + `/en/josm_proxy?zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}'); return true;`"
              >
                fix-josm
              </a>
              <a
                href="#"
                class="editor_fix"
                data-type="{%type%}"
                data-id="{%id%}"
                data-error="{%uuid%}"
                data-fix="{%num%}"
                :title="
                  $t('Load the fix in {where}', {
                    where: $t('online Osmose Editor'),
                  })
                "
              >
                fix-edit
              </a>
            </div>
            {%#add%}
            <div class="add">
              <b>{%k%}</b> = {%#vlink%}
              <a href="{%vlink%}" target="popup_tag2link">
                {%/vlink%} {%v%} {%#vlink%}
              </a>
              {%/vlink%}
            </div>
            {%/add%} {%#mod%}
            <div class="mod">
              <b>{%k%}</b> = {%#vlink%}
              <a href="{%vlink%}" target="popup_tag2link">
                {%/vlink%} {%v%} {%#vlink%}
              </a>
              {%/vlink%}
            </div>
            {%/mod%} {%#del%}
            <div class="del"><b>{%k%}</b></div>
            {%/del%}
          </div>
          {%/fixes%} {%#tags%}
          <b>{%k%}</b> = {%#vlink%}
          <a href="{%vlink%}" target="popup_tag2link">
            {%/vlink%} {%v%} {%#vlink%}
          </a>
          {%/vlink%}
          <br />
          {%/tags%}
        </div>
        {%/elems%} {%#new_elems%}
        <div class="bulle_elem">
          <div class="fix">
            <div class="fix_links">
              <a
                :href="
                  api_url + '/en/josm_proxy?import?url=' +
                  api_url +
                  '/api/0.3/issue/{%uuid%}/fix/{%num%}'
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Add the new object in {where}', { where: 'JOSM' })"
                :onclick="`$.get('` + api_url + `/en/josm_proxy?zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}'); return true;`"
              >
                fix-josm
              </a>
            </div>
            {%#add%}
            <div class="add">
              <b>{%k%}</b> = {%#vlink%}
              <a href="{%vlink%}" target="popup_tag2link">
                {%/vlink%} {%v%} {%#vlink%}
              </a>
              {%/vlink%}
            </div>
            {%/add%} {%#mod%}
            <div class="mod">
              <b>{%k%}</b> = {%#vlink%}
              <a href="{%vlink%}" target="popup_tag2link">
                {%/vlink%} {%v%} {%#vlink%}
              </a>
              {%/vlink%}
            </div>
            {%/mod%} {%#del%}
            <div class="del"><b>{%k%}</b></div>
            {%/del%}
          </div>
        </div>
        {%/new_elems%}
      </div>
      <div class="bulle_verif">
        <a
          :href="
            main_website + '?mlat={%lat%}&mlon={%lon%}#map=18/{%lat%}/{%lon%}'
          "
          target="popup_osm"
          :title="$t('Show the area on {where}', { where: main_website })"
        >
          osm-show
        </a>
        <a
          :href="main_website + 'edit#map=18/{%lat%}/{%lon%}'"
          target="_blank"
          :title="$t('Edit the area on {where}', { where: main_website })"
        >
          osm-edit
        </a>
        <a
          :href="api_url + '../josm_proxy?load_and_zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}&select={%elems_id%}'"
          target="hiddenIframe"
          class="josm"
          :title="$t('Edit the area on {where}', { where: 'JOSM' })"
        >
          josm-zone
        </a>
        <a
          href="../error/{%uuid%}"
          target="_blank"
          :title="$t('Issue details')"
        >
          <translate>details</translate>
        </a>
      </div>
      <div id="bulle_footer">
        <div id="bulle_maj">
          <span :title="$t('Report based on data from date')">
            <translate>Issue reported on:</translate> {%b_date%}
          </span>
        </div>
        <div id="bulle_button">
          <div class="btn-group" role="group">
            <a
              class="false_positive btn btn-info btn-sm popup_help"
              role="button"
              href="#"
              :title="$t('Help')"
            >
              ℹ
            </a>
            <a
              class="closePopup false_positive btn btn-danger btn-sm"
              role="button"
              href="/api/0.3/issue/{%uuid%}/false"
              target="hiddenIframe"
              :onclick="
                'return confirm(&quote;' +
                $t(
                  'Report the issue as improper, if according to you is not an issue. The issue will not be displayed to anyone more.'
                ) +
                '&quote;)'
              "
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
              class="closePopup corrected btn btn-success btn-sm"
              role="button"
              :href="api_url + '/api/0.3/issue/{%uuid%}/done'"
              target="hiddenIframe"
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

export default Vue.extend({
  props: ["main_website", "remote_url_read"],
  computed: {
    api_url: () => API_URL,
  },
});
</script>
