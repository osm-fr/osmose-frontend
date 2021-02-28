<template>
  <component :is="$vnode.data.tag" v-if="object_count" class="save_button">
    <a href="#" v-on:click.stop.prevent="save">
      <translate>Save</translate>
      (<span>{{ object_count }}</span
      >)
    </a>
  </component>
</template>


<script>
import Vue from "vue";

import ExternalVueAppEvent from "../../ExternalVueAppEvent.js";

export default Vue.extend({
  data() {
    return {
      object_count: 0,
    };
  },
  mounted() {
    ExternalVueAppEvent.$on("editor-count", this.count);
  },
  methods: {
    count(n) {
      this.object_count = n;
    },
    save() {
      ExternalVueAppEvent.$emit("editor-save");
    },
  },
});
</script>

<style scoped>
.save_button {
  background: #64db64;
}
</style>
