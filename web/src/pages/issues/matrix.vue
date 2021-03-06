<template>
  <div style="font-size: 50%">
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <table
      v-else
      class="table table-striped table-bordered table-hover table-sm"
    >
      <thead>
        <tr>
          <th class="n" colspan="2" rowspan="2">
            {{ total | numFormat }}
          </th>
          <th
            v-for="(sum, country) in sorted_countries_sum"
            class="country"
            :key="'1_' + country"
          >
            <div class="rotate-90">
              <router-link :to="`../errors/?country=${country}`">
                {{ country }}
              </router-link>
            </div>
          </th>
        </tr>
        <tr>
          <th
            v-for="(sum, country) in sorted_countries_sum"
            :key="'2_' + country"
            class="n"
          >
            {{ sum | numFormat }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(sum, analyser) in sorted_analysers_sum" :key="analyser">
          <th style="text-align: left">{{ analyser }}</th>
          <th class="n">{{ sum | numFormat }}</th>
          <td
            v-for="(sum, country) in sorted_countries_sum"
            :key="'3_' + country"
          >
            <template v-if="analysers[analyser][country]">{{
              analysers[analyser][country] | numFormat
            }}</template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import VueParent from "../Parent.vue";

export default VueParent.extend({
  data() {
    return {
      error: false,
      total: null,
      sorted_countries_sum: [],
      sorted_analysers_sum: [],
    };
  },
  mounted() {
    this.fetchJsonProgressAssign(
      API_URL + window.location.pathname + ".json" + window.location.search,
      (response) => {
        this.sorted_countries_sum = this.sortObject(this.countries_sum);
        this.sorted_analysers_sum = this.sortObject(this.analysers_sum);

        document.title = "Osmose - " + this.$t("Issue counts matrix");
      }
    );
  },
  methods: {
    sortObject: (o) =>
      Object.entries(o)
        .sort((a, b) => (a[1] === b[1] ? 0 : a[1] < b[1] ? 1 : -1))
        .reduce((r, k) => ((r[k[0]] = o[k[0]]), r), {}),
  },
});
</script>

<style scoped>
th.n,
td {
  text-align: right;
  font-size: 80%;
}
</style>
