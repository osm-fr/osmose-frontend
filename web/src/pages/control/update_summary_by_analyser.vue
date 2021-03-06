<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <table
      v-else
      class="table table-striped table-bordered table-hover table-sm"
    >
      <thead class="thead-dark">
        <tr>
          <th><translate>Analyser</translate></th>
          <th><translate>Count</translate></th>
          <th><translate>Age</translate></th>
          <th><translate>Version</translate></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="analyser in summary_keys" :key="analyser">
          <td>{{ analyser }}</td>
          <td>{{ summary[analyser].count }}</td>
          <td>
            <delay :v="summary[analyser].min_age">
              {{ summary[analyser].min_age | numFormat("0.0") }}-
              <delay :v="summary[analyser].max_age">
                {{ summary[analyser].max_age | numFormat("0.0") }}
              </delay>
            </delay>
          </td>
          <td>
            <span
              is="version"
              :max="max_versions"
              :v="summary[analyser].min_version"
            >
              {{ summary[analyser].min_version }}
            </span>
            -
            <span
              is="version"
              :max="max_versions"
              :v="summary[analyser].max_version"
            >
              {{ summary[analyser].max_version }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import VueParent from "../Parent.vue";
import Delay from "../../components/delay.vue";
import Version from "../../components/version.vue";

export default VueParent.extend({
  data() {
    return {
      error: false,
      summary: null,
    };
  },
  computed: {
    summary_keys(a) {
      return this.summary && Object.keys(this.summary).sort();
    },
  },
  components: {
    Delay,
    Version,
  },
  mounted() {
    this.fetchJsonProgressAssign(
      API_URL + window.location.pathname + ".json" + window.location.search
    );
    document.title = "Osmose - " + this.$t("Updates summary");
  },
});
</script>
