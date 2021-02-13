<template>
  <div>
    <h1>Osmose-QA</h1>
    <ul>
      <li>
        <router-link to="map/">
          <translate>Map of issues</translate>
        </router-link>
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
        <router-link to="errors/false-positive">
          <translate>False positives list</translate>
        </router-link>
      </li>
      <li>
        <router-link to="control/update">
          <translate>Last analysis updates</translate>
        </router-link>
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
