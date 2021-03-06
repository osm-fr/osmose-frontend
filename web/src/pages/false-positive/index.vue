<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <marker-details v-else-if="marker" :marker="marker" :uuid="uuid" />
  </div>
</template>

<script>
import VueParent from "../Parent.vue";
import MarkerDetails from "../../components/marker-details.vue";

export default VueParent.extend({
  data() {
    return {
      error: false,
      uuid: "",
      marker: null,
    };
  },
  components: {
    MarkerDetails,
  },
  mounted() {
    this.fetchJsonProgressAssign(
      API_URL + window.location.pathname + ".json" + window.location.search,
      (response) => {
        document.title =
          "Osmose - " +
          this.$t("Information on issue {uuid}", { uuid: this.uuid });

        const favicon = document.getElementById("favicon");
        favicon.href =
          URL_API + `/images/markers/marker-l-${this.marker.item}.png`;
      }
    );
  },
});
</script>
