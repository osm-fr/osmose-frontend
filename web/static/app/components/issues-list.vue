<template>
  <div>
    <sorted-table
      :values="errors"
      class="table table-striped table-bordered table-hover table-sm"
    >
      <thead class="thead-dark">
        <tr>
          <th scope="col" title="source">
            <sort-link name="source">
              <translate>source</translate>
            </sort-link>
          </th>
          <th scope="col" title="level">
            <sort-link name="level">
              <!-- {{ TRANSLATORS: this should be replaced by a abbreviation for level }} -->
              <translate>level (abbreviation)</translate>
            </sort-link>
          </th>
          <th scope="col">
            <sort-link name="item"><translate>item</translate></sort-link>
          </th>
          <th scope="col" title="class">
            <sort-link name="class">
              <!-- {{ TRANSLATORS: this should be replaced by a abbreviation for class }} -->
              <translate>class (abbreviation)</translate>
            </sort-link>
          </th>
          <th scope="col" :title="$t('information on issue')">E</th>
          <th scope="col" :title="$t('position')">
            <translate>position (abbreviation)</translate>
          </th>
          <th scope="col">
            <translate>elements (abbreviation)</translate>
          </th>
          <th scope="col">
            <sort-link name="subtitle">
              <translate>subtitle</translate>
            </sort-link>
          </th>
          <th v-if="opt_date" scope="col">
            <sort-link name="date"><translate>date</translate></sort-link>
          </th>
          <th
            v-if="['error', 'info'].includes(gen)"
            :title="$t('False positive / Done')"
          >
            ✘/✔
          </th>
          <th v-if="gen == 'false-positive'" :title="$t('delete issue')">✘</th>
        </tr>
      </thead>
      <template #body="sort">
        <tbody>
          <tr v-for="res in sort.values" :key="res.uuid">
            <td :title="`${res.country}-${res.analyser}`">
              <a :href="`?${page_args}source=${res.source_id}`">
                {{ res.source_id }}
              </a>
            </td>
            <td>{{ res.level }}</td>
            <td>
              <img
                :src="`../images/markers/marker-l-${res.item}.png`"
                :alt="res.item"
              />
              <a :href="`?${page_args}item=${res.item}`">{{ res.item }}</a>
              <span v_if="res.menu">{{ res["menu"] }}</span>
            </td>
            <td>{{ res.class }}</td>
            <td :title="$t('issue n°') + res.uuid">
              <a
                :href="`../${
                  'false-positive' == gen ? 'false-positive' : 'error'
                }/${res.uuid}`"
              >
                E
              </a>
            </td>
            <td>
              <a
                v-if="res.lat !== undefined && res.lon !== undefined"
                :href="`/map/#${query}&amp;item=${res.item}&amp;zoom=17&amp;lat=${res.lat}&amp;lon=${res.lon}&amp;level=${res.level}&tags=&fixable=&issue_uuid=${res.uuid}`"
              >
                {{ res.lon.toFixed(2) }}&nbsp;{{ res.lat.toFixed(2) }}
              </a>
            </td>
            <td v-if="res.elems">
              <span v-for="e in res.elems" :key="e.id">
                <a
                  target="_blank"
                  :href="`${main_website}${e.type_long}/${e.id}`"
                  >{{ e.type.toLocaleLowerCase() }}{{ e.id }}</a
                >&nbsp;<a
                  v-if="e.type == 'R'"
                  title="josm"
                  :href="`../josm_proxy?import?url=${remote_url_read}api/0.6/relation/${e.id}/full`"
                  target="hiddenIframe"
                  :onclick="`$.get('http://localhost:8111/zoom?left=${
                    res.lon - 0.002
                  }&bottom=${res.lat - 0.002}&right=${res.lon + 0.002}&top=${
                    res.lat + 0.002
                  }'); return true;`"
                >
                  (j)
                </a>
                <a
                  v-else
                  title="josm"
                  :href="`../josm_proxy?load_object?objects=${e.type.toLocaleLowerCase()}${
                    e.id
                  }`"
                  target="hiddenIframe"
                >
                  (j)
                </a>
              </span>
            </td>
            <td v-else>
              <a
                :href="`http://localhost:8111/load_and_zoom?left=${
                  res.lon - 0.002
                }&amp;bottom=${lat - 0.002}&amp;right=${lon + 0.002}&amp;top=${
                  lat + 0.002
                }`"
              >
                josm
              </a>
            </td>
            <td>{{ res.subtitle || res.title || "" }}</td>
            <td v-if="opt_date">
              {{ res.date.substring(0, 10) }}&nbsp;{{
                res.date.substring(11, 16)
              }}
            </td>
            <td v-if="['error', 'info'].includes(gen)">
              <a
                href="#"
                v-on:click="issue_action"
                :id="`GET=issue/${res.uuid}/false`"
                :title="
                  $t('Mark issue #{uuid} as false positive', { uuid: res.uuid })
                "
              >
                ✘ </a
              >/
              <a
                href="#"
                v-on:click="issue_action"
                :id="`GET=issue/${res.uuid}/done`"
                :title="$t('Mark issue #{uuid} as fixed', { uuid: res.uuid })"
              >
                ✔
              </a>
            </td>
            <td
              v-if="gen == 'false-positive'"
              :title="$t('delete issue #{uuid}', { uuid: res.uuid })"
            >
              <a
                href="#"
                v-on:click="issue_action"
                :id="`DELETE=${gen}/${res.uuid}`"
              >
                ✘
              </a>
            </td>
          </tr>
        </tbody>
      </template>
    </sorted-table>
    <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: {
    query: { default: "" },
    errors: null,
    gen: null,
    opt_date: { default: false },
    main_website: null,
    remote_url_read: null,
    page_args: { default: "" },
  },
  methods: {
    issue_action: (event) => {
      $("#load").fadeIn();
      const Container = $(event.currentTarget).parent();
      const id = $(event.currentTarget).attr("id").split("=");
      const verb = id[0];
      const path = id[1];

      $.ajax({
        type: verb,
        url: `/api/0.3/${path}`,
        cache: false,
        beforeSend() {
          Container.parent().css({ backgroundColor: "red" });
        },
        success: (response) => {
          Container.parent()
            .find("td")
            .wrapInner('<div style="display: block;" />')
            .parent()
            .find("td > div")
            .slideUp(700, () =>
              $(event.currentTarget).parent().parent().remove()
            );
        },
        error: (xhr, ajaxOptions, thrownError) => {
          Container.parent().css({ backgroundColor: "" });
        },
      });

      return false;
    },
  },
});
</script>
