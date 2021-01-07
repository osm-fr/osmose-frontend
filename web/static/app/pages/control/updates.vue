<template>
  <div>
    <p>
      {{ $t("Median delay:") }}
      <time-ago v-if="median_delay" :datetime="median_delay" tooltip />
    </p>
    <table class="table table-striped table-bordered table-hover table-sm">
      <thead class="thead-dark">
        <tr>
          <th>{{ $t("source") }}</th>
          <th style="min-width: 100px">{{ $t("country") }}</th>
          <th style="min-width: 100px">{{ $t("analyser") }}</th>
          <th style="min-width: 200px">{{ $t("last generation") }}</th>
          <th>{{ $t("history") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="source in list"
          :key="source.source + '|' + source.timestamp"
        >
          <td>
            <a :href="`../errors/?source=${source.id}`">{{
              source.id
            }}</a>
          </td>
          <td>{{ source.country }}</td>
          <td>{{ source.analyser }}</td>
          <td>
            <time-ago
              v-if="source.timestamp"
              :datetime="source.timestamp"
              tooltip
            />
            <span v-else>_("never generated")</span>
          </td>
          <td>
            <a :href="`update/{{source[4]}}`">{{ $t("history") }}</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Vue from "vue";
import TimeAgo from "vue2-timeago";

export default Vue.extend({
  data() {
    return {
      list: null,
    };
  },
  computed: {
    median_delay() {
      return this.list && this.list.length > 0
        ? this.list[Math.trunc(this.list.length / 2)].timestamp
        : null;
    },
  },
  components: {
    TimeAgo,
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
