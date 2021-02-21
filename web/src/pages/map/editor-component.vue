<template>
  <div>
    <div id="editor" :data-user="!!user">
      <p>
        <translate>You must be logged in order to use the tag editor</translate>
      </p>
      <a href="../login"><translate>Login</translate></a>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["user"],
});
</script>
