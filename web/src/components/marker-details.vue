<template>
  <table
    id="table_marker"
    class="table table-striped table-bordered table-hover table-sm"
  >
    <thead class="thead-dark">
      <tr>
        <th scope="col"><translate>key</translate></th>
        <th scope="col"><translate>value</translate></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>source</td>
        <td>
          <router-link
            :to="`../issues/open?item=xxxx&amp;source=${marker.source_id}`"
          >
            {{ marker.source_id }}
          </router-link>
        </td>
      </tr>
      <tr>
        <td>item</td>
        <td>
          <router-link :to="`../issues/open?item=${marker.item}`">
            {{ marker.item }}
          </router-link>
        </td>
      </tr>
      <tr>
        <td>class</td>
        <td>
          <router-link
            :to="`../issues/open?item=${marker.item}&amp;class=${marker.class}`"
          >
            {{ marker.class }}
          </router-link>
        </td>
      </tr>
      <tr>
        <td>lat lon</td>
        <td>
          <router-link
            :to="`../map/#item=${marker.item}&amp;zoom=17&amp;lat=${marker.lat}&amp;lon=${marker.lon}&amp;issue_uuid=${uuid}`"
          >
            {{ marker.lat }}&nbsp;{{ marker.lon }}
          </router-link>
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
          <a :href="marker.source_code">
            {{ marker.source_code }}
          </a>
        </td>
      </tr>
      <tr v-if="marker.resource">
        <td>resource</td>
        <td>
          <a :href="marker.resource">
            {{ marker.resource }}
          </a>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'

import ShowDict from './show-dict.vue'

interface Marker {
  source_id: string
  item: string
  class: string
  lat: string
  lon: string
  title: string
  subtitle: string
  timestamp: string
  detail: string
  fix: string
  trap: string
  example: string
  source_code: string
  resource: string
}

export default Vue.extend({
  components: {
    ShowDict,
  },
  props: {
    marker: {
      type: Object as PropType<Marker>,
      required: true,
    },
    uuid: {
      type: String,
      required: true,
    },
  },
})
</script>
