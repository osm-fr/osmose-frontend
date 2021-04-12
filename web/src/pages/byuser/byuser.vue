<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <nav
        class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark"
        style="background-color: #212529"
      >
        <span class="navbar-brand">
          <translate :params="{ users: users.join(', ') }">
            User statistics for {users}
          </translate>
        </span>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link
                class="nav-link"
                :to="`../map/#username=${username}`"
              >
                <translate>Map</translate>
              </router-link>
            </li>
          </ul>
          <div class="form-inline my-2 my-lg-0">
            <a :href="`${api_url_path}.rss`" class="badge badge-secondary">
              .rss</a
            >
          </div>
        </div>
      </nav>
      <br />

      <p>
        <translate :params="{ users: users.join('\', \'') }">
          This page shows issues on elements that were last modified by
          '{users}'. This doesn't means that this user is responsible for all
          these issues.
        </translate>
      </p>
      <p>
        <span v-if="count < 500">
          <translate :params="{ count: count }">
            Number of found issues: {count}
          </translate>
        </span>
        <span v-else>
          <translate :params="{ count: count }">
            Number of found issues: more than {count}
          </translate>
        </span>
      </p>

      <issues-list
        :errors="errors"
        gen="info"
        :main_website="main_website"
        :page_args="`username=${username}&`"
      />
    </div>
  </div>
</template>

<script>
import VueParent from "../Parent.vue";
import IssuesList from "../../components/issues-list.vue";

export default VueParent.extend({
  data() {
    return {
      error: false,
      users: [],
      username: "",
      count: 0,
      errors: [],
      main_website: "",
    };
  },
  computed: {
    api_url_path: () => API_URL + window.location.pathname,
  },
  components: {
    IssuesList,
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
    render() {
      this.query = window.location.search.substring(1);

      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + ".json" + window.location.search,
        (response) => {
          document.title =
            "Osmose - " +
            this.$t("Statistics for user {user}", {
              user: this.users.join(", "),
            });

          var rss = document.getElementById("rss");
          if (rss) {
            rss.remove();
          }
          rss = document.createElement("link");
          Object.assign(rss, {
            id: "rss",
            href: `http://${this.website}/${this.$route.params.lang}/byuser/${this.$route.params.user}.rss?${this.query}`,
            rel: "alternate",
            type: "application/rss+xml",
            title: document.title,
          });
          document.head.appendChild(rss);
        }
      );
    },
  },
});
</script>

<style scoped>
a.badge:visited {
  color: #fff; /* Unclicked color for bootstrap badge-secondary */
}
</style>
