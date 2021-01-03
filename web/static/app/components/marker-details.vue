<template>
  <table
    class="table table-striped table-bordered table-hover table-sm"
    id="table_marker"
  >
    <thead class="thead-dark">
      <tr>
        <th scope="col">{{ $t("key") }}</th>
        <th scope="col">{{ $t("value") }}</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>source</td>
        <td>
          <a
            target="_blank"
            :href="`../errors/?item=xxxx&amp;source=${marker.source_id}`"
            >{{ marker.source_id }}</a
          >
        </td>
      </tr>
      <tr>
        <td>item</td>
        <td>
          <a target="_blank" :href="`../errors/?item=${marker.item}`">{{
            marker.item
          }}</a>
        </td>
      </tr>
      <tr>
        <td>class</td>
        <td>
          <a
            target="_blank"
            :href="`../errors/?item=${marker.item}&amp;class=${marker.class}`"
            >{{ marker.class }}</a
          >
        </td>
      </tr>
      <tr>
        <td>lat lon</td>
        <td>
          <a
            target="_blank"
            :href="`../map/?item=${marker.item}&amp;zoom=17&amp;lat=${marker.lat}&amp;lon=${marker.lon}&amp;issue_uuid=${uuid}`"
            >{{ marker.lat }}&nbsp;{{ marker.lon }}</a
          >
        </td>
      </tr>
      <tr>
        <td>title</td>
        <td>
          <show-dict :dict="marker.title"></show-dict>
        </td>
      </tr>
      <tr>
        <td>subtitle</td>
        <td>
          <show-dict :dict="marker.subtitle"></show-dict>
        </td>
      </tr>
      <tr>
        <td>timestamp</td>
        <td>{{ marker.timestamp }}</td>
      </tr>
      <tr v-if="marker.detail">
        <td>detail</td>
        <td>
          <show-dict :dict="marker.detail"></show-dict>
        </td>
      </tr>
      <tr v-if="marker.fix">
        <td>fix</td>
        <td>
          <show-dict :dict="marker.fix"></show-dict>
        </td>
      </tr>
      <tr v-if="marker.trap">
        <td>trap</td>
        <td>
          <show-dict :dict="marker.trap"></show-dict>
        </td>
      </tr>
      <tr v-if="marker.example">
        <td>example</td>
        <td>
          <show-dict :dict="marker.example"></show-dict>
        </td>
      </tr>
      <tr v-if="marker.source_code">
        <td>source code</td>
        <td>
          <a :href="marker.source_code" target_="_blank">{{
            marker.source_code
          }}</a>
        </td>
      </tr>
      <tr v-if="marker.resource">
        <td>resource</td>
        <td>
          <a :href="marker.resource" target_="_blank">{{ marker.resource }}</a>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import Vue from "vue";

import ShowDict from "../components/show-dict.vue";

export default Vue.extend({
  props: ["marker", "uuid"],
  components: {
    "show-dict": ShowDict,
  },
});
</script>
