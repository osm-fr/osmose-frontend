<template>
  <div>
    <h1>Osmose-QA</h1>
    <ul>
      <li>
        <a href="map/">{{ $t("Map of issues") }}</a>
      </li>
      <li>
        <a :href="$t('http://wiki.openstreetmap.org/wiki/Osmose')">{{
          $t("Help on OSM wiki")
        }}</a>
      </li>
    </ul>

    <h2>{{ $t("Information on issues database") }}</h2>
    <ul>
      <li>
        <a href="errors/false-positive">{{ $t("False positives list") }}</a>
      </li>
      <li>
        <a href="control/update">{{ $t("Last analysis updates") }}</a>
      </li>
    </ul>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  created() {
    document.title = "Osmose";
  },
});
</script>
