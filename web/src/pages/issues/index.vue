<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <nav
        class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark"
        style="background-color: #212529"
      >
        <span v-if="favicon" class="navbar-brand">
          <img :src="favicon" />
        </span>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" :to="`./?${query}`">
                <translate>Informations</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`done?${query}`">
                <translate>Fixed</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`false-positive?${query}`">
                <translate>False positives</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <a class="nav-link" :href="`graph.png?${query}`">
                <translate>Graph</translate>
              </a>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`../map/#${query}`">
                <translate>Map</translate>
              </router-link>
            </li>
          </ul>
          <div class="form-inline my-2 my-lg-0">
            <a
              :href="`${api_url_path}.rss?${query}`"
              class="badge badge-secondary"
            >
              .rss </a
            >&nbsp;
            <a
              :href="`${api_url_path}.gpx?${query}`"
              class="badge badge-secondary"
            >
              .gpx </a
            >&nbsp;
            <a
              :href="`${api_url_path}.kml?${query}`"
              class="badge badge-secondary"
            >
              .kml </a
            >&nbsp;
            <a
              :href="`${api_url_path}.csv?${query}`"
              class="badge badge-secondary"
            >
              .csv </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues?${query}`"
              class="badge badge-secondary"
            >
              .json </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues?${query}&full=true`"
              class="badge badge-secondary"
            >
              .json full</a
            >&nbsp;
            <a
              :href="`${api_url_path}.geojson?${query}`"
              class="badge badge-secondary"
            >
              .geojon
            </a>
          </div>
        </div>
      </nav>
      <br />

      <div class="form-inline col-sm-12 col-md-12">
        <form method="get" action="" id="errors-list">
          <div class="form-row">
            <div class="form-group col-sm-3 col-md-3">
              <label for="item">
                <translate>Country</translate>
              </label>
              <select
                v-model="country"
                class="form-control form-control-sm"
                name="country"
              >
                <option value=""></option>
                <option v-for="res in countries" :key="res" :value="res">
                  {{ res }}
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3">
              <label for="item">
                <translate>Item</translate>
              </label>
              <select
                v-model="item"
                class="form-control form-control-sm"
                name="item"
              >
                <option value="xxxx"></option>
                <option v-for="res in items" :key="res.item" :value="res.item">
                  {{ res.item }} - {{ res.menu.auto }}
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3">
              <label for="level">
                <translate>Severity</translate>
              </label>
              <select
                v-model="level"
                name="level"
                class="form-control form-control-sm"
              >
                <option class="level-1__" value="1">
                  <translate>High</translate>
                </option>
                <option class="level-12_" value="1,2">
                  <translate>Normal or higher</translate>
                </option>
                <option class="level-123" value="1,2,3">
                  <translate>All</translate>
                </option>
                <option disabled="disabled"></option>
                <option class="level-_2_" value="2">
                  <translate>Normal only</translate>
                </option>
                <option class="level-__3" value="3">
                  <translate>Low only</translate>
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3">
              <!-- {{ TRANSLATORS: 'Set' is used to choose a specific country/item on /errors }} -->
              <input
                type="submit"
                class="btn btn-outline-secondary btn-sm"
                :value="$t('Set')"
              />
            </div>
          </div>
        </form>
      </div>

      <sorted-table
        :values="sortable(errors_groups)"
        class="table table-striped table-bordered table-hover table-sm"
        id="table_source"
      >
        <thead class="thead-dark">
          <tr>
            <th scope="col"><sort-link name="source_id">#</sort-link></th>
            <th scope="col">
              <sort-link name="analyser_country">
                <translate>source</translate>
              </sort-link>
            </th>
            <th scope="col">
              <sort-link name="timestamp"><translate>age</translate></sort-link>
            </th>
            <th scope="col">
              <sort-link name="item"><translate>item</translate></sort-link>
            </th>
            <th scope="col" title="class">
              <sort-link name="class">
                <translate
                  translate-comment="TRANSLATORS: this should be replaced by a abbreviation for class"
                >
                  class (abbreviation)
                </translate>
              </sort-link>
            </th>
            <th scope="col">
              <sort-link name="title"><translate>title</translate></sort-link>
            </th>
            <th scope="col">
              <sort-link name="count"><translate>count</translate></sort-link>
            </th>
          </tr>
        </thead>
        <template #body="sort">
          <tbody>
            <tr
              v-for="res in sort.values"
              :key="res.source_id + '|' + res.class"
            >
              <td>
                <router-link :to="`?source=${res.source_id}`">
                  {{ res.source_id }}
                </router-link>
              </td>
              <td>
                {{ res.analyser }}-
                <router-link :to="`?country=${res.country}`">
                  {{ res.country }}
                </router-link>
              </td>
              <td>
                <time-ago :datetime="res.timestamp" tooltip />
              </td>
              <td>
                <img
                  :src="api_url + `/images/markers/marker-l-${res.item}.png`"
                  :alt="res.item"
                />
                <router-link
                  :to="`?item=${res.item}&amp;country=${res.country}`"
                >
                  {{ res.item }}
                </router-link>
                <span v-if="res.menu">{{ res.menu }}</span>
              </td>
              <td>
                <router-link
                  :to="`?item=${res.item}&amp;class=${res.class}&amp;country=${res.country}`"
                >
                  {{ res.class }}
                </router-link>
              </td>
              <td>{{ res.title }}</td>
              <td>
                <router-link
                  :to="`?source=${res.source_id}&amp;item=${res.item}&amp;class=${res.class}`"
                >
                  {{ res.count === -1 ? "N/A" : res.count }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </template>
        <tfoot class="thead-dark">
          <tr>
            <th colspan="6"><translate>Total</translate></th>
            <th style="text-align: left">{{ total }}</th>
          </tr>
        </tfoot>
      </sorted-table>
      <br />

      <div v-if="errors">
        <issues-list
          :errors="errors"
          :gen="gen"
          :opt_date="opt_date"
          :main_website="main_website"
          :remote_url_read="remote_url_read"
        />
        <a href="#" v-on:click.stop.prevent="show_more()">
          <translate>Show more issues</translate>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import TimeAgo from "vue2-timeago";

import VueParent from "../Parent.vue";
import IssuesList from "../../components/issues-list.vue";

export default VueParent.extend({
  data() {
    return {
      error: false,
      favicon: null,
      countries: [],
      items: [],
      errors_groups: [],
      total: 0,
      errors: [],
      opt_date: false,
      main_website: "",
      remote_url_read: "",
      query: "",
      country: this.$route.query.country,
      item: this.$route.query.item,
      level: this.$route.query.level,
      limit: this.$route.query.limit,
      gen:
        API_URL + window.location.pathname.includes("false-positive")
          ? "false-positive"
          : "gen",
    };
  },
  computed: {
    api_url: () => API_URL,
    api_url_path: () => API_URL + window.location.pathname,
  },
  components: {
    IssuesList,
    TimeAgo,
  },
  watch: {
    $route() {
      this.render();
    },
  },
  mounted() {
    this.render();
  },
  methods: {
    sortable: (data) => {
      return data.map((res) => {
        res.analyser_country = res.analyser + "-" + res.country;
        return res;
      });
    },
    render: function () {
      this.country = this.$route.query.country;
      this.item = this.$route.query.item;
      this.level = this.$route.query.level;
      this.limit = this.$route.query.limit;

      this.query = window.location.search.substring(1);

      let title = {
        "issues/open": this.$t("Information"),
        "issues/done": this.$t("Fixed issues"),
        "issues/false-positive": this.$t("False positives"),
      }[this.$route.name];

      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + ".json" + window.location.search,
        (response) => {
          var res = this.items.find((e) => e.item == this.item);
          if (res) {
            title += " - " + res.menu.auto;
            const favicon = document.getElementById("favicon");
            this.favicon =
              API_URL + `/images/markers/marker-l-${this.item}.png`;
            favicon.href = this.favicon;
          }

          document.title = "Osmose - " + title;

          var rss = document.getElementById("rss");
          if (rss) {
            rss.remove();
          }
          rss = document.createElement("link");
          Object.assign(rss, {
            id: "rss",
            href: `http://${this.website}/${this.$route.params.lang}/errors.rss?${this.query}`,
            rel: "alternate",
            type: "application/rss+xml",
            title: document.title,
          });
          document.head.appendChild(rss);
        }
      );
    },
    show_more: function () {
      var query = Object.assign({}, this.$route.query);
      query.limit = this.limit ? this.limit * 5 : 500;
      this.$router.push({ name: this.$route.name, query });
    },
  },
});
</script>

<style scoped>
a.badge:visited {
  color: #fff; /* Unclicked color for bootstrap badge-secondary */
}
</style>
