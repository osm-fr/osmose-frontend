<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <table class="table table-striped table-bordered table-hover table-sm">
      <thead class="thead-dark">
        <tr>
          <th><translate>source</translate></th>
          <th style="min-width: 800px"><translate>remote url</translate></th>
          <th><translate>timestamp</translate></th>
          <th><translate>version</translate></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="res in list" :key="res.timestamp">
          <td>
            <a :href="`../../errors/?source={res.source_id}`">
              {{ res.source_id }}
            </a>
          </td>
          <td>{{ remote(res) }}</td>
          <td>{{ res.timestamp }}</td>
          <td>{{ res.version }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  data() {
    return {
      list: null,
    };
  },
  mounted() {
    this.$refs.topProgress.start();
    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        this.$refs.topProgress.done();

        Object.assign(this, response);
      });
    document.title = "Osmose - " + this.$t("Update");
  },
  methods: {
    remote(res) {
      var url = res.remote_url;
      if (url.startsWith("http://")) {
        url = url.split("/")[2];
      } else if (res.remote_ip) {
        url = res.remote_ip;
      }
      return url;
    },
  },
});
</script>
