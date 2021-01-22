<template>
  <div>
    <h1><translate>User statistics</translate></h1>
    <translate>Osmose allows you to control your own issues.</translate>
    <br />
    <translate>
      By entering your OSM username in the following form, you will be able to
      see issues that are attached to your username. Note that the algorithm
      that attaches issues to username is not perfect, as Osmose only checks the
      last contributor of the relevant erroneous elements.
    </translate>
    <br /><br />
    <form method="GET" action="#" v-on:submit="submit">
      <label for="username"><translate>Username:</translate></label>
      <input type="text" v-model="username" name="username" />
      <input type="submit" />
    </form>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  data() {
    return {
      username: null,
    };
  },
  created() {
    document.title = "Osmose - " + this.$t("Statistics for user");
  },
  methods: {
    submit(e) {
      e.preventDefault();
      window.location.href = `./${this.username}`;
    },
  },
});
</script>
