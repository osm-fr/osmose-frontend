<template>
  <div id="filters">
    <div id="level-span" class="form-group row">
      <label for="level" class="col-sm-3 col-form-label">
        <translate>Severity</translate>
      </label>
      <div class="col-sm-9">
        <select v-model="state.level" class="form-control form-control-sm">
          <option class="level-1__" value="1">
            <translate>High</translate>
          </option>
          <option class="level-12_" value="1,2">
            <translate>Normal or higher</translate>
          </option>
          <option class="level-123" value="1,2,3">
            <translate>All</translate>
          </option>
          <option disabled="disabled"></option>
          <option class="level-_2_" value="2">
            <translate>Normal only</translate>
          </option>
          <option class="level-__3" value="3">
            <translate>Low only</translate>
          </option>
        </select>
      </div>
    </div>

    <div id="fixable-span" class="form-group row">
      <label for="fixable" class="col-sm-3 col-form-label">
        <translate>Fixable</translate>
      </label>
      <div class="col-sm-9">
        <select
          v-model="state.fixable"
          name="fixable"
          class="form-control form-control-sm"
          :title="$t('Show only markers with correction suggestions')"
        >
          <option value=""></option>
          <option value="online"><translate>Online</translate></option>
          <option value="josm">JOSM</option>
        </select>
      </div>
    </div>

    <div id="tags-span" class="form-group row">
      <label for="tags" class="col-sm-3 col-form-label">
        <translate>Topic</translate>
      </label>
      <div class="col-sm-9">
        <select
          v-model="state.tags"
          name="tags"
          class="form-control form-control-sm"
        >
          <option value=""></option>
          <option v-for="tag in tags" :key="tag" :value="tag">
            {{ $t(tag) }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import _ from "lodash";

export default Vue.extend({
  props: ["original_tags", "itemState"],
  data() {
    return {
      tags: [],
      state: Object.assign({}, this.itemState),
    };
  },
  watch: {
    original_tags: function () {
      if (this.original_tags) {
        this.tags = this.original_tags;
      }
    },
    state: {
      deep: true,
      handler() {
        this.$emit("state-update", Object.assign({}, this.state));
      },
    },
    itemState: {
      deep: true,
      handler() {
        if (!_.isEqual(this.itemState, this.state)) {
          this.state = Object.assign({}, this.itemState);
        }
      },
    },
  },
});
</script>

<style scoped>
form {
  margin: 0px;
  height: 100%;
}

label {
  text-align: center;
}

div#filters > div {
  margin-bottom: 0px;
  margin-right: 0px;
  margin-left: 0px;
}

div#filters > div > label,
div#filters > div > div {
  padding-right: 0px;
  padding-left: 0px;
}
</style>
