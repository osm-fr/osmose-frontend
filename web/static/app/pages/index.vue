<template>
  <div>
    <h1>Osmose-QA</h1>
    <ul>
      <li>
        <a href="map/"><translate>Map of issues</translate></a>
      </li>
      <li>
        <a :href="$t('http://wiki.openstreetmap.org/wiki/Osmose')">
          <translate>Help on OSM wiki</translate>
        </a>
      </li>
    </ul>

    <h2><translate>Information on issues database</translate></h2>
    <ul>
      <li>
        <a href="errors/false-positive">
          <translate>False positives list</translate>
        </a>
      </li>
      <li>
        <a href="control/update">
          <translate>Last analysis updates</translate>
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  mounted() {
    document.title = "Osmose";
  },
});
</script>
