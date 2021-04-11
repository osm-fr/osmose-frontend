<template>
  <div id="menu">
    <a href="#" id="togglemenu">-</a>
    <div v-if="error">{{ error }}</div>
    <form v-else action="#">
      <div id="need_zoom">
        <translate>no bubbles at this zoom factor</translate>
      </div>
      <div id="action_links">
        <div id="level-span" class="form-group row">
          <label for="level" class="col-sm-3 col-form-label">
            <translate>Severity</translate>
          </label>
          <div class="col-sm-9">
            <select v-model="level" class="form-control form-control-sm">
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
              v-model="fixable"
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
              v-model="selected_tags"
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
        <translate>Select:</translate>
        <a href="#" v-on:click.stop.prevent="toggle_all(true)">
          <translate>all</translate>
        </a>
        <a href="#" v-on:click.stop.prevent="toggle_all(false)">
          <translate>nothing</translate>
        </a>
        <a href="#" v-on:click.stop.prevent="toggle_all(-1)">
          <translate>invert</translate>
        </a>
      </div>
      <div id="tests">
        <div
          v-for="categ in categories_format"
          :key="categ.id"
          class="test_group"
        >
          <h1>
            <a
              href="#"
              v-on:click.stop.prevent="toggle_categorie_block(categ.id)"
            >
              <i class="toggleCategIco"></i>
              {{ categ.title.auto }}
            </a>
            <span class="count">
              {{ count_items[categ.id] }}/{{ total_items[categ.id] }}
            </span>
            <a
              href="#"
              v-on:click.stop.prevent="toggle_categorie(categ.id, true)"
            >
              <translate>all</translate>
            </a>
            <a
              href="#"
              v-on:click.stop.prevent="toggle_categorie(categ.id, false)"
            >
              <translate>nothing</translate>
            </a>
          </h1>
          <ul :id="`categorie_block_${categ.id}`">
            <li
              v-for="item in categ.items"
              :key="item.item"
              class="item"
              :title="item.class_format"
              :style="showItem(item) ? '' : 'display:none'"
            >
              <div :class="`marker-l marker-l-${item.item}`"></div>
              <div class="level">
                <template v-for="level in 3">
                  <div
                    v-if="item.levels_format[level]"
                    :key="level"
                    :class="`level-${level} ${
                      active_levels.indexOf(level.toString()) >= 0
                        ? ''
                        : 'disabled'
                    }`"
                  >
                    <span>{{ item.levels_format[level] }}</span>
                  </div>
                  <div v-else :key="level"></div>
                </template>
              </div>
              <input
                type="checkbox"
                v-model="item.selected"
                @change="toggle_item(item.item, item.selected)"
              />
              <router-link target="_blank" :to="`../errors/?item=${item.item}`">
                {{ item.title.auto }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import Vue from "vue";

import ExternalVueAppEvent from "../../ExternalVueAppEvent.js";

export default Vue.extend({
  props: ["error", "menu", "tags", "categories", "item_levels"],
  data() {
    return {
      level: "1",
      fixable: null,
      selected_tags: null,
      active_levels: ["1", "2", "3"],
      total_items: {},
      count_items: {},
    };
  },
  watch: {
    level: function (level) {
      this.active_levels = level.split(",");
      this.itemsChanged();
    },
    fixable: function () {
      this.itemsChanged();
    },
    selected_tags: function () {
      this.itemsChanged();
    },
  },
  computed: {
    categories_format() {
      return this.categories.map((categorie) => {
        this.total_items[categorie.id] = categorie.items.length;
        categorie.items = categorie.items.map((item) => {
          item.class_format =
            this.$t("Item #{item}", { item: item.item }) +
            "\n" +
            item.class.map((c) => c.class + ". " + c.title.auto).join("\n");
          item.item_format = ("000" + item.item).slice(-4);
          item.levels_format = {};
          item.levels.forEach((level) => {
            item.levels_format[level.level] = level.count;
          });
          return item;
        });
        return categorie;
      });
    },
  },
  mounted() {
    ExternalVueAppEvent.$on("item-params-changed", this.setParams);
  },
  methods: {
    _select_items_loop(callback, categ_id) {
      this.categories.forEach((categorie) => {
        if (!categ_id || categorie.id == categ_id) {
          this.count_items[categorie.id] = 0;
          categorie.items.forEach((item) => {
            if (callback) {
              item.selected = callback(item);
            }
            if (item.selected) {
              this.count_items[categorie.id]++;
            }
          });
        }
      });
    },
    setParams(params) {
      if (params.item !== undefined) {
        const itemRegex = params.item
          .split(",")
          .filter((item) => item != "")
          .map((item) => new RegExp(item.replace(/x/g, ".")));
        this._select_items_loop((item) =>
          itemRegex.some((regex) => regex.test(item.item_format))
        );
      }

      if (params.level !== undefined) {
        this.level = params.level;
      }

      if (params.fixable !== undefined) {
        this.fixable = params.fixable;
      }

      if (params.tags !== undefined) {
        if (this.tags.indexOf(params.tags) < 0) {
          this.tags.push(params.tags);
        }
        this.selected_tags = params.tags;
      }

      this.$forceUpdate();
    },
    showItem(item) {
      return (
        this.item_levels[this.level].indexOf(item.item) >= 0 &&
        (!this.selected_tags ||
          (item.tags && item.tags.indexOf(this.selected_tags) >= 0))
      );
    },
    toggle_all(how) {
      this._select_items_loop((item) => (how === -1 ? !item.selected : how));
      this.$forceUpdate();
      this.itemsChanged();
    },
    toggle_categorie(categ_id, how) {
      this._select_items_loop((item) => how, categ_id);
      this.$forceUpdate();
      this.itemsChanged();
    },
    toggle_item(item_id, selected) {
      this._select_items_loop((item) => (item.item === item_id) ? selected : item.selected);
      this.$forceUpdate();
      this.itemsChanged();
    },
    toggle_categorie_block(categ_id) {
      const block = document.getElementById(`categorie_block_${categ_id}`);
      block.style.height = block.style.height == "0px" ? "" : "0px";
    },
    itemsChanged() {
      var full_categ = 0;
      var item_mask = this.categories
        .filter((categorie) => this.count_items[categorie.id] > 0)
        .map((categorie) => {
          if (
            this.total_items[categorie.id] == this.count_items[categorie.id]
          ) {
            full_categ++;
            return `${categorie.id / 10}xxx`;
          } else {
            return categorie.items
              .filter((item) => item.selected)
              .map((item) => item.item_format)
              .join(",");
          }
        })
        .join(",");
      if (full_categ == this.categories.length) {
        item_mask = "xxxx";
      }
      this.menu._itemChanged(
        item_mask,
        this.level,
        this.fixable,
        this.selected_tags
      );
    },
  },
});
</script>
