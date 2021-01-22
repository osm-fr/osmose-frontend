<template>
  <div style="font-size: 50%">
    <table class="table table-striped table-bordered table-hover table-sm">
      <thead>
        <tr>
          <th colspan="4" rowspan="4" />
          <th v-for="k in keys" :key="k" class="country">
            <div class="rotate-90">
              <a href="`../errors/?country=${k}&item=xxxx`">{{ k }}</a>
            </div>
          </th>
        </tr>
        <tr v-for="i in 3" :key="i">
          <th v-for="k in keys" :key="k">
            <delay :v="stats_country[k][i]">{{
              stats_country[k][i] | numFormat("0.0")
            }}</delay>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in matrix_keys" :key="r">
          <th style="text-align: left">{{ r }}</th>
          <th v-for="i in 3" :key="i">
            <delay :v="stats_analyser[r][i]">{{
              stats_analyser[r][i] | numFormat("0.0")
            }}</delay>
          </th>
          <td v-for="k in keys" :key="k">
            <delay v-if="matrix[r][k]" :v="matrix[r][k][0]">
              <a :href="`update/{{matrix[r][k][1]}}`">{{
                matrix[r][k][0] | numFormat("0.0")
              }}</a>
            </delay>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Vue from "vue";

import Delay from "../../components/delay.vue";

export default Vue.extend({
  data() {
    return {
      keys: null,
      matrix_keys: null,
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
    document.title = "Osmose - " + this.$t("Last updates");
  },
});
</script>
