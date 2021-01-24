<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <marker-details v-if="marker" :marker="marker" :uuid="uuid" />
  </div>
</template>

<script>
import Vue from "vue";

import MarkerDetails from "../../components/marker-details.vue";

export default Vue.extend({
  data() {
    return {
      uuid: "",
      marker: null,
    };
  },
  components: {
    MarkerDetails,
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
        document.title =
          "Osmose - " +
          this.$t("Information on issue {uuid}", { uuid: this.uuid });

        const favicon = document.getElementById("favicon");
        favicon.href = `../images/markers/marker-l-${this.marker.item}.png`;
      });
  },
});
</script>
