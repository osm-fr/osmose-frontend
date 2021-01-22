<template>
  <div>
    <h1>
      {{ $t("User statistics for {users}", { users: users.join(", ") }) }}
    </h1>
    <p>
      {{
        $t(
          "This page shows issues on elements that were last modified by '{users}'. This doesn't means that this user is responsible for all these issues.",
          users.join("', '")
        )
      }}
    </p>
    <p>
      <a :href="rss">{{ $t("This list is also available via rss.") }}</a>
    </p>
    <p>
      <span v-if="count < 500">{{
        $t("Number of found issues: {count}", { count: count })
      }}</span>
      <span v-else>{{
        $t("Number of found issues: more than {count}", { count: count })
      }}</span>
      -
      <a :href="`../map/#username=${username}`">{{
        $t("Show issues on a map")
      }}</a>
    </p>

    <issues-list
      :errors="errors"
      gen="info"
      :main_website="main_website"
      :page_args="`username=${username}&`"
    />
  </div>
</template>

<script>
import Vue from "vue";

import IssuesList from "../../components/issues-list.vue";

export default Vue.extend({
  data() {
    return {
      users: null,
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
  created() {
    this.query = window.location.search.substring(1);

    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        Object.assign(this, response);
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
      });
  },
});
</script>
