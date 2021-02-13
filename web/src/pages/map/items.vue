<template>
  <div id="menu">
    <a href="#" id="togglemenu">-</a>
    <form id="myform" name="myform" action="#">
      <div id="need_zoom">
        <translate>no bubbles at this zoom factor</translate>
      </div>
      <div id="action_links">
        <div id="level-span" class="form-group row">
          <label for="level" class="col-sm-3 col-form-label">
            <translate>Severity</translate>
          </label>
          <div class="col-sm-9">
            <select id="level" class="form-control form-control-sm">
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
              id="fixable"
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
            <select id="tags" class="form-control form-control-sm">
              <option value=""></option>
              <option v-for="tag in tags" :key="tag" :value="tag">
                {{ $t(tag) }}
              </option>
            </select>
          </div>
        </div>
        <translate>Select:</translate>
        <a href="#" class="toggleAllItem" data-view="all">
          <translate>all</translate>
        </a>
        <a href="#" class="toggleAllItem" data-view="nothing">
          <translate>nothing</translate>
        </a>
        <a href="#" class="invertAllItem">
          <translate>invert</translate>
        </a>
      </div>
      <div id="tests">
        <div
          v-for="categ in categories_format"
          :key="categ.id"
          class="test_group"
          :id="`categ${categ.id}`"
        >
          <h1>
            <i class="toggleCategIco"></i>
            <a href="#" class="toggleCateg">
              {{ categ.title.auto }}
            </a>
            <span class="count">-/-</span>
            <a href="#" class="toggleAllItem" data-view="all">
              <translate>all</translate>
            </a>
            <a href="#" class="toggleAllItem" data-view="nothing">
              <translate>nothing</translate>
            </a>
          </h1>
          <ul>
            <li
              v-for="item in categ.items"
              :key="item.item"
              :id="`item_desc${item.item}`"
              class="item"
              :title="item.class_format"
            >
              <div :class="`marker-l marker-l-${item.item}`"></div>
              <div class="level">
                <template v-for="level in 3">
                  <div
                    v-if="item.levels_format[level]"
                    :key="level"
                    :class="`level-${level}`"
                  >
                    <span>{{ item.levels_format[level] }}</span>
                  </div>
                  <div v-else :key="level"></div>
                </template>
              </div>
              <input
                type="checkbox"
                :id="`item${item.item_format}`"
                :name="`item${item.item_format}`"
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

export default Vue.extend({
  props: ["tags", "categories"],
  computed: {
    categories_format() {
      return this.categories.map((categorie) => {
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
});
</script>
