<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <h1>
        <translate :params="{ users: users.join(', ') }">
          User statistics for {users}
        </translate>
      </h1>
      <p>
        <translate :params="{ users: users.join('\', \'') }">
          This page shows issues on elements that were last modified by
          '{users}'. This doesn't means that this user is responsible for all
          these issues.
        </translate>
      </p>
      <p>
        <a :href="rss">
          <translate>This list is also available via rss.</translate>
        </a>
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
        -
        <router-link :to="`../map/#username=${username}`">
          <translate>Show issues on a map</translate>
        </router-link>
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
    rss() {
      return `https://${this.website}/byuser/${this.username}.rss`;
    },
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
