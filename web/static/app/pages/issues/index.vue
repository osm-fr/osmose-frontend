<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <nav
      class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark"
      style="background-color: #212529"
    >
      <span v-if="favicon" class="navbar-brand">
        <img :src="favicon" />
      </span>
      <div class="collapse navbar-collapse">
        <div class="navbar-nav">
          <a class="nav-item nav-link active" :href="`.?${query}`">
            <translate>Informations</translate>
          </a>
          <a class="nav-item nav-link active" :href="`done?${query}`">
            <translate>Fixed</translate>
          </a>
          <a class="nav-item nav-link active" :href="`false-positive?${query}`">
            <translate>False positives</translate>
          </a>
          <a class="nav-item nav-link active" :href="`graph.png?${query}`">
            <translate>Graph</translate>
          </a>
          <a class="nav-item nav-link active" :href="`../map/#${query}`">
            <translate>Map</translate>
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
              <!-- {{ TRANSLATORS: this should be replaced by a abbreviation for class }} -->
              <translate>class (abbreviation)</translate>
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
          <tr v-for="res in sort.values" :key="res.source_id + '|' + res.class">
            <td>
              <a :href="`?source=${res.source_id}`">
                {{ res.source_id }}
              </a>
            </td>
            <td>
              {{ res.analyser }}-
              <a :href="`?country=${res.country}`">
                {{ res.country }}
              </a>
            </td>
            <td>
              <time-ago :datetime="res.timestamp" tooltip />
            </td>
            <td>
              <img
                :src="`../images/markers/marker-l-${res.item}.png`"
                :alt="res.item"
              />
              <a :href="`?item=${res.item}&amp;country=${res.country}`">
                {{ res.item }}
              </a>
              <span v-if="res.menu">{{ res.menu }}</span>
            </td>
            <td>
              <a
                :href="`?item=${res.item}&amp;class=${res.class}&amp;country=${res.country}`"
              >
                {{ res.class }}
              </a>
            </td>
            <td>{{ res.title }}</td>
            <td>
              <a
                :href="`?source=${res.source_id}&amp;item=${res.item}&amp;class=${res.class}`"
              >
                {{ res.count === -1 ? "N/A" : res.count }}
              </a>
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
      <a v-if="limit" :href="`?limit=${limit * 5}`">
        <translate>Show more issues</translate>
      </a>
      <a v-else :href="`?${query}&amp;limit=100`">
        <translate>Show more issues</translate>
      </a>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import TimeAgo from "vue2-timeago";

import IssuesList from "../../components/issues-list.vue";

export default Vue.extend({
  data() {
    return {
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
      gen: window.location.pathname.includes("false-positive")
        ? "false-positive"
        : "gen",
    };
  },
  components: {
    IssuesList,
    TimeAgo,
  },
  mounted() {
    this.$refs.topProgress.start();
    this.query = window.location.search.substring(1);

    let title = {
      "issues/open": this.$t("Information"),
      "issues/done": this.$t("Fixed issues"),
      "issues/false-positive": this.$t("False positives"),
    }[this.$route.name];

    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        this.$refs.topProgress.done();

        Object.assign(this, response);

        var res = this.items.find((e) => e.item == this.item);
        if (res) {
          title += " - " + res.menu.auto;
          const favicon = document.getElementById("favicon");
          this.favicon = `../images/markers/marker-l-${this.item}.png`;
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
      });
  },
  methods: {
    sortable: (data) => {
      return data.map((res) => {
        res.analyser_country = res.analyser + "-" + res.country;
        return res;
      });
    },
  },
});
</script>
