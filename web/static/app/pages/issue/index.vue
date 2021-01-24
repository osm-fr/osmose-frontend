<template>
  <div>
    <h2><translate>Marker</translate></h2>
    <marker-details :marker="marker" :uuid="uuid" />
    <br />

    <h2><translate>Elements</translate></h2>
    <template v-if="marker.elems">
      <div v-for="(element, elem_index) in marker.elems" :key="element.id">
        <table
          class="table table-striped table-bordered table-hover table-sm"
          id="table_marker"
        >
          <thead class="thead-dark">
            <tr>
              <th scope="col"><translate>key</translate></th>
              <th scope="col"><translate>value</translate></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>elem_index</td>
              <td>{{ elem_index }}</td>
            </tr>
            <tr>
              <td>type id</td>
              <td>
                <a
                  target="_blank"
                  :href="`${main_website}${data_type(element.type)}/${
                    element.id
                  }`"
                  >{{ element.type }}&nbsp;{{ element.id }}</a
                >
              </td>
            </tr>
            <tr>
              <td>tags</td>
              <td>
                <show-tags :tags="element.tags"></show-tags>
              </td>
            </tr>
            <tr v-if="element.username">
              <td>username</td>
              <td>
                <a
                  target="_blank"
                  :href="`${main_website}user/${element.username}`"
                  >{{ element.username }}</a
                >
              </td>
            </tr>
          </tbody>
        </table>
        <br />
      </div>
    </template>

    <h2><translate>Fixes</translate></h2>
    <template v-if="marker.fixes">
      <div v-for="(fix_group, fix_index) in marker.fixes" :key="fix_index">
        <h3>#{{ fix_index }}</h3>
        <div v-for="(fix, fix_index) in fix_group" :key="'fix|' + fix_index">
          <table
            class="table table-striped table-bordered table-hover table-sm"
            id="table_marker"
          >
            <thead class="thead-dark">
              <tr>
                <th scope="col"><translate>key</translate></th>
                <th scope="col"><translate>value</translate></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>fix_index</td>
                <td>{{ fix_index }}</td>
              </tr>
              <tr>
                <td>type id</td>
                <td>
                  <a
                    target="_blank"
                    :href="`${main_website}${data_type(fix.type)}/${fix.id}`"
                    >{{ fix.type }}&nbsp;{{ fix.id }}</a
                  >
                </td>
              </tr>
              <tr>
                <td>create</td>
                <td>
                  <show-tags :tags="fix.create"></show-tags>
                </td>
              </tr>
              <tr>
                <td>modify</td>
                <td>
                  <show-tags :tags="fix.modify"></show-tags>
                </td>
              </tr>
              <tr>
                <td>delete</td>
                <td>
                  <show-tags :tags="fix.delete"></show-tags>
                </td>
              </tr>
            </tbody>
          </table>
          <br />
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import Vue from "vue";

import MarkerDetails from "../../components/marker-details.vue";
import ShowTags from "../../components/show-tags.vue";

export default Vue.extend({
  data() {
    return {
      uuid: "",
      marker: {
        elems: [],
        fixes: [],
      },
    };
  },
  components: {
    MarkerDetails,
    ShowTags,
  },
  created() {
    fetch(window.location.pathname + ".json" + window.location.search, {
      headers: new Headers({
        "Accept-Language": this.$route.params.lang,
      }),
    })
      .then((response) => response.json())
      .then((response) => {
        Object.assign(this, response);
        document.title =
          "Osmose - " +
          this.$t("Information on issue {uuid}", { uuid: this.uuid });

        const favicon = document.getElementById("favicon");
        favicon.href = `../images/markers/marker-l-${this.marker.item}.png`;
      });
  },
  methods: {
    data_type: (type) =>
      ({ N: "node", W: "way", R: "relation", I: "infos" }[type]),
  },
});
</script>
