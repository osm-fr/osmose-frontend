<template>
  <div id="top_links">
    <ul id="topmenu">
      <li id="menu-lang">
        <a href="#" onclick="return false;">
          <translate>Change language</translate> ▼
        </a>
        <ul class="submenu">
          <li
            v-for="(v, k) in languages_name"
            :key="k"
            :class="$route.params.lang == k ? 'bold' : ''"
          >
            <router-link
              :to="'/' + k + location"
              v-on:click.native="changeLang(v)"
            >
              {{ v.name }} ({{ k }})
            </router-link>
          </li>
        </ul>
      </li>

      <li v-if="!user" id="menu-byuser">
        <router-link :to="user ? `../byuser/${user}` : '../byuser/'">
          <translate
            translate-comment="TRANSLATORS: link to help in appropriate language"
          >
            Issues by user
          </translate>
        </router-link>
      </li>
      <li id="menu-statistics">
        <router-link to="../control/update_matrix">
          <translate translate-comment="TRANSLATORS: link to source code">
            Statistics
          </translate>
        </router-link>
      </li>

      <li>
        <a href="#" onclick="return false;"><translate>Export</translate> ▼</a>
        <ul class="submenu">
          <li>
            <a class="menu-export" data-href="../errors/" target="_blank">
              <translate>Html list</translate>
            </a>
          </li>
          <li>
            <a
              class="menu-export"
              :data-href="api_url + '/en/josm_proxy?errors.josm'"
              target="hiddenIframe"
            >
              JOSM
            </a>
          </li>
          <li>
            <a class="menu-export" data-href="../errors.rss" target="_blank">
              RSS
            </a>
          </li>
          <li><a class="menu-export" data-href="../errors.gpx">GPX</a></li>
          <li><a class="menu-export" data-href="../errors.kml">KML</a></li>
          <li>
            <a class="menu-export" data-href="/api/0.3/issues" target="_blank">
              Json
            </a>
          </li>
          <li>
            <a class="menu-export" data-href="../errors.csv" target="_blank">
              CSV
            </a>
          </li>
          <li>
            <a class="menu-export" data-href="markers" target="_blank">
              GeoJson
            </a>
          </li>
        </ul>
      </li>

      <li id="menu-help">
        <a href="#" onclick="return false;"><translate>Help</translate> ▼</a>
        <ul class="submenu">
          <li>
            <router-link to="../contact">
              <translate>Contact</translate>
            </router-link>
          </li>
          <li>
            <a href="http://wiki.openstreetmap.org/wiki/Osmose">
              <translate>Help on wiki</translate>
            </a>
          </li>
          <li>
            <router-link to="../copyright">
              <translate>Copyright</translate>
            </router-link>
          </li>
          <li>
            <a href="https://github.com/osm-fr?q=osmose">
              <translate>Sources</translate>
            </a>
          </li>
          <li>
            <router-link to="../translation">
              <translate>Translation</translate>
            </router-link>
          </li>
        </ul>
      </li>

      <li
        is="delay"
        warning="0.9"
        error="1.6"
        :v="(Date.now() - Date.parse(timestamp)) / 1000 / 60 / 60 / 24"
        id="menu-delay"
      >
        <router-link to="../control/update_summary">
          {{ $t("Delay:") }}
          <time-ago v-if="timestamp" :datetime="timestamp" tooltip />
          <span v-else>-</span>
        </router-link>
      </li>

      <li id="menu-user">
        <template v-if="user">
          <router-link :to="`../byuser/${user}`">
            {{ user }} ({{
              user_error_count[1] + user_error_count[2] + user_error_count[3]
            }}) ▼
          </router-link>
          <ul class="submenu">
            <li>
              <router-link :to="`../byuser/${user}?level=1`">
                {{
                  $t("Level {level} issues ({count})", {
                    level: 1,
                    count: user_error_count[1],
                  })
                }}
              </router-link>
            </li>
            <li>
              <router-link :to="`../byuser/${user}?level=2`">
                {{
                  $t("Level {level} issues ({count})", {
                    level: 2,
                    count: user_error_count[2],
                  })
                }}
              </router-link>
            </li>
            <li>
              <router-link :to="`../byuser/${user}?level=3`">
                {{
                  $t("Level {level} issues ({count})", {
                    level: 3,
                    count: user_error_count[3],
                  })
                }}
              </router-link>
            </li>
            <li>
              <a :href="api_url + `/${$route.params.lang}/logout`">
                <translate>Logout</translate>
              </a>
            </li>
          </ul>
        </template>
        <a v-else :href="api_url + `/${$route.params.lang}/login`">
          <translate>Login</translate>
        </a>
      </li>
      <li is="editor-menu" />
    </ul>
  </div>
</template>

<script>
import Vue from "vue";
import TimeAgo from "vue2-timeago";

import Delay from "../../components/delay.vue";
import EditorMenu from "./editor-menu.vue";

export default Vue.extend({
  props: ["languages_name", "lang", "user", "user_error_count", "timestamp"],
  computed: {
    api_url: () => API_URL,
    location() {
      const i = window.location.pathname.indexOf("/", 1);
      return (
        window.location.pathname.substring(i) + "?" + window.location.search
      );
    },
  },
  components: {
    Delay,
    EditorMenu,
    TimeAgo,
  },
  methods: {
    changeLang: (lang) => {
      window.document.dir = lang.direction;
    },
  },
});
</script>


<style>
div#top_links {
  background-color: #ffffff;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.65);
  position: absolute;
  height: 24px;
  width: 100%;
  left: 0px;
  top: 0px;
  opacity: 0.9;
  font-size: 13px;

  vertical-align: middle;
  text-align: center;
  z-index: 1025;
}

.leaflet-touch + div#top_links {
  box-shadow: none;
  border-bottom: 2px solid rgba(0, 0, 0, 0.2);
  background-clip: padding-box;
}

#topmenu {
  list-style-type: none;
  margin: 0;
  padding: 0;
  border: 0;
  position: absolute;
  top: 0;
}
#topmenu li {
  display: inline-block;
  vertical-align: top;
  margin: 0;
  padding: 0;
  border: 0;
}
#topmenu li a:link,
#topmenu li a:visited {
  display: block;
  margin: 0;
  padding: 2px 8px;
  border-right: 1px solid #cccccc;
  text-decoration: none;
}
#topmenu li a:hover #topmenu li a:active {
  background-color: #b0b0b0;
}

#topmenu .submenu {
  display: none;
  list-style-type: none;
  margin: 0;
  padding: 0;
  border: 0;
}
#topmenu .submenu li {
  display: block;
  margin: 0;
  padding: 0;
  border: 0;
  border-top: 1px solid #003453;
  border-right: 1px solid #003453;
}
#topmenu .submenu li a:link,
#topmenu .submenu li a:visited {
  display: block;
  margin: 0;
  border: 0;
  text-decoration: none;
  background: #dddddd;
}
#topmenu .submenu li a:hover {
  background-image: none;
  background-color: #b0b0b0;
}

#topmenu li:hover > .submenu {
  display: block;
}
</style>
