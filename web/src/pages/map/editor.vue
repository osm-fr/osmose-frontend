<template>
  <div id="editor" :data-user="!!user">
    <div v-if="!user">
      <p>
        <translate>You must be logged in order to use the tag editor</translate>
      </p>
      <a href="../login"><translate>Login</translate></a>
    </div>
    <div v-if="status == 'error'">{{ error }}</div>
    <div v-if="status == 'loading'">
      <center>
        <img src="~../../../static/images/throbbler.gif" alt="downloading" />
      </center>
    </div>
    <div v-if="status == 'editor'">
      <h1><translate>Tags Editor</translate></h1>
      <form>
        <div v-for="elem in elems" :key="`${elem.type}/${elem.id}`">
          <a target="_blank" :href="main_website + `${elem.type}/${elem.id}`">
            {{ elem.type }} {{ elem.id }}
          </a>
          <div
            class="tags"
            :data-type="elem.type"
            :data-id="elem.id"
            :data-version="elem.version"
          >
            <div class="del"></div>
            <div class="same"></div>
            <div class="mod"></div>
            <div class="add"></div>
          </div>
        </div>
        <br />
        <div id="buttons">
          <input
            type="button"
            v-on:click.stop.prevent="cancel()"
            class="btn btn-secondary"
            :value="$t('Cancel')"
          />
          <input
            type="button"
            v-on:click.stop.prevent="validate(uuid)"
            class="btn btn-primary"
            :value="$t('Done')"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

import ExternalVueAppEvent from "../../ExternalVueAppEvent.js";

export default Vue.extend({
  props: ["user", "main_website", "editor"],
  data() {
    return {
      status: null,
      uuid: null,
    };
  },
  mounted() {
    ExternalVueAppEvent.$on("editor-load", this.load);
  },
  methods: {
    load(uuid, fix) {
      this.status = "loading";

      fetch(
        API_URL +
          `/api/0.3/issue/${uuid}/fresh_elems${
            typeof fix !== "undefined" ? `/${fix}` : ""
          }`,
        {
          headers: new Headers({
            "Accept-Language": this.$route.params.lang,
          }),
        }
      )
        .then((response) => response.json())
        .then((response) => {
          Object.assign(this, response);
          this.uuid = uuid;
          this.status = "editor";
          this.$nextTick(() => {
            this.editor._setTags(response);
          });
        })
        .catch((error) => {
          this.error = error.message;
          this.status = "error";
        });
    },
    validate(uuid) {
      this.editor._validate(uuid);
    },
    cancel() {
      this.editor._cancel();
    },
  },
});
</script>
