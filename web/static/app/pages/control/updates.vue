<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <p>
      <translate>Median delay:</translate>
      <time-ago v-if="median_delay" :datetime="median_delay" tooltip />
    </p>
    <virtual-scroller
      page-mode
      class="scroller"
      :items="list"
      :item-size="30"
      v-if="list"
      style="display: table; width: 100%;"
    >
      <template #before>
        <header style="display: table-row; width: 100%;">
            <div style="display: table-cell; width: 20%;"><translate>source</translate></div>
            <div style="display: table-cell; width: 20%;"><translate>country</translate></div>
            <div style="display: table-cell; width: 20%;"><translate>analyser</translate></div>
            <div style="display: table-cell; width: 20%;">
              <translate>last generation</translate>
            </div>
            <div style="display: table-cell; width: 20%;"><translate>history</translate></div>
        </header>
      </template>

      <template v-slot="{ item }">
        <div style="display: table-row;"
          :key="item.source + '|' + item.timestamp"
        >
          <div style="display: table-cell; width: 20%;">
            <a :href="`../errors/?source=${item.id}`">
              {{ item.id }}
            </a>
          </div>
          <div style="display: table-cell; width: 20%;">{{ item.country }}</div>
          <div style="display: table-cell; width: 20%;">{{ item.analyser }}</div>
          <div style="display: table-cell; width: 20%;">
            <time-ago
              v-if="item.timestamp"
              :datetime="item.timestamp"
              tooltip
            />
            <span v-else><translate>never generated</translate></span>
          </div>
          <div style="display: table-cell; width: 20%;">
            <a :href="`update/{{item[4]}}`"><translate>history</translate></a>
          </div>
        </div>
      </template>
    </virtual-scroller>
  </div>
</template>

<script>
import Vue from "vue";
import TimeAgo from "vue2-timeago";
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import { RecycleScroller } from 'vue-virtual-scroller'

export default Vue.extend({
  data() {
    return {
      list: null,
    };
  },
  computed: {
    median_delay() {
      return this.list && this.list.length > 0
        ? this.list[Math.trunc(this.list.length / 2)].timestamp
        : null;
    },
  },
  components: {
    TimeAgo,
    'virtual-scroller': RecycleScroller
  },
  mounted() {
    this.$refs.topProgress.start();
    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        this.$refs.topProgress.done();

        Object.assign(this, response);
      });
    document.title = "Osmose - " + this.$t("Last updates");
  },
});
</script>
