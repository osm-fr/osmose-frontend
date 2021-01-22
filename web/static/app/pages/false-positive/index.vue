<template>
  <marker-details :marker="marker" :uuid="uuid" />
</template>

<script>
import Vue from "vue";

import MarkerDetails from "../../components/marker-details.vue";

export default Vue.extend({
  data() {
    return {
      marker: null,
    };
  },
  components: {
    MarkerDetails,
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
        document.title =
          "Osmose - " +
          this.$t("Information on issue {uuid}", { uuid: this.uuid });

        const favicon = document.getElementById("favicon");
        favicon.href = `../images/markers/marker-l-${this.marker.item}.png`;
      });
  },
});
</script>
