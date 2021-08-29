<template>
  <div>
    <div class="form-group row">
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

    <div class="form-group row">
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

    <div class="form-group row">
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

    <template v-if="extra_filter">
      <a
        href="#"
        v-on:click.stop.prevent="extra_filter = false"
        class="more_filters"
      >
        <translate>Less filters</translate> <span>▲</span>
      </a>
      <div>
        <div class="form-group row">
          <label for="item" class="col-sm-3 col-form-label">
            <translate>Country</translate>
          </label>
          <div class="col-sm-9">
            <select
              v-model="state.country"
              class="form-control form-control-sm"
              name="country"
            >
              <option value=""></option>
              <option v-for="res in {}" :key="res" :value="res">
                {{ res }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-group row">
        <label for="source" class="col-sm-3 col-form-label">
          <translate>Source id</translate>
        </label>
        <div class="col-sm-9">
          <input
            v-model="state.source"
            name="source"
            type="text"
            class="form-control form-control-sm"
          />
        </div>
      </div>

      <div class="form-group row">
        <label for="class" class="col-sm-3 col-form-label">
          <translate>Class id</translate>
        </label>
        <div class="col-sm-9">
          <input
            v-model="state.class"
            name="class"
            type="text"
            class="form-control form-control-sm"
          />
        </div>
      </div>

      <div class="form-group row">
        <label for="useDevItem" class="col-sm-3 col-form-label">
          <translate>Show hidden items</translate>
        </label>
        <div class="col-sm-9">
          <select
            v-model="state.useDevItem"
            name="useDevItem"
            class="form-control form-control-sm"
          >
            <option value="">
              <translate>No (Default)</translate>
            </option>
            <option value="all">
              <translate>All</translate>
            </option>
            <option value="true">
              <translate>Only</translate>
            </option>
          </select>
        </div>

        <div class="form-group row">
          <label for="username" class="col-sm-3 col-form-label">
            <translate>OSM Username</translate>
          </label>
          <div class="col-sm-9">
            <input
              v-model="state.username"
              name="username"
              type="text"
              class="form-control form-control-sm"
            />
          </div>
        </div>
      </div>
    </template>
    <a
      v-else
      href="#"
      v-on:click.stop.prevent="extra_filter = true"
      class="more_filters"
    >
      <translate>More filters</translate> <span>▼</span>
    </a>
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
      extra_filter: false,
    };
  },
  mounted() {
    console.error(this.state);
    if (
      this.state.class != null ||
      this.state.useDevItem ||
      this.state.source != null ||
      this.state.username ||
      this.state.country
    ) {
      this.extra_filter = true;
    }
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

.form-group {
  margin-bottom: 0px;
  margin-right: 0px;
  margin-left: 0px;
}

.form-group > label,
.form-group > div {
  padding-right: 0px;
  padding-left: 0px;
}

.more_filters {
  display: block;
  text-align: right;
}
</style>
