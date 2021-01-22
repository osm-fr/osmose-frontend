<template>
  <table class="table table-striped table-bordered table-hover table-sm">
    <template v-for="remote in remote_keys">
      <thead :key="'h' + remote" class="thead-dark">
        <tr>
          <th>
            <a :href="`update_matrix?remote=${remote}`">{{
              hostnames[remote] || remote
            }}</a>
            ({{ min_versions[remote] }} - {{ max_versions[remote] }})
          </th>
        </tr>
      </thead>
      <tbody :key="'b' + remote">
        <tr>
          <td>
            <delay
              v-for="country in summary[remote]"
              :key="country.country"
              :v="country.min_age"
              :opacity="opacity(country.count, max_count)"
            >
              <a :href="`../errors/?country=${country.country}&item=xxxx`">{{
                country.country
              }}</a
              ><sup>{{ country.count }}</sup>
              <delay
                :v="country.max_age"
                :opacity="opacity(country.count, max_count)"
              >
                {{ country.max_age | numFormat("0.0") }}</delay
              >
              -{{ country.min_age | numFormat("0.0") }}</delay
            >
          </td>
        </tr>
      </tbody>
    </template>
  </table>
</template>

<script>
import Vue from "vue";

import Delay from "../../components/delay.vue";

export default Vue.extend({
  data() {
    return {
      remote_keys: null,
    };
  },
  components: {
    Delay,
  },
  created() {
    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        Object.assign(this, response);
      });
    document.title = "Osmose - " + this.$t("Updates summary");
  },
  methods: {
    opacity(count, max) {
      return (0.66 * count) / max + 0.33;
    },
  },
});
</script>
