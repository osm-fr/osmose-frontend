<template>
  <div id="editor" :data-user="!!user">
    <div v-if="!user">
      <p>
        <translate>You must be logged in order to use the tag editor</translate>
      </p>
      <a href="../login"><translate>Login</translate></a>
    </div>
    <div v-if="status == 'error'">{{ error }}</div>
    <div v-if="status == 'loading'">
      <center>
        <img src="~../../../static/images/throbbler.gif" alt="downloading" />
      </center>
    </div>
    <div v-if="status == 'editor'">
      <h1><translate>Tags Editor</translate></h1>
      <form id="editor_form">
        <div
          v-for="[type_id, elem] in Object.entries(elems)"
          :key="`${elem.type}/${elem.id}`"
        >
          <a
            target="_blank"
            :href="main_website + `${elem.type}/${elem.id}`"
            class="object_link"
          >
            {{ elem.type }} {{ elem.id }}
          </a>
          <div class="tags">
            <template v-for="tag in elems_deleted[type_id]">
              <div
                is="editor-tag"
                :tag_key.sync="tag.key"
                :tag_value.sync="tag.value"
                action="del"
                :key="tag.id"
                v-on:delete="delete_tag(type_id, tag.key)"
              />
            </template>
            <template v-for="tag in elem.tags">
              <div
                is="editor-tag"
                :tag_key.sync="tag.key"
                :tag_value.sync="tag.value"
                :leading_equal.sync="tag.leading_equal"
                :action="elems_action[type_id][tag.key]"
                :key="tag.id"
                v-on:delete="delete_tag(type_id, tag.key)"
              />
            </template>
          </div>
        </div>
        <br />
        <div id="buttons">
          <input
            type="button"
            v-on:click="cancel()"
            class="btn btn-secondary"
            :value="$t('Cancel')"
          />
          <input
            type="button"
            v-on:click="validate(uuid)"
            class="btn btn-primary"
            :value="$t('Done')"
          />
        </div>
      </form>
    </div>

    <div v-if="status == 'saving'">
      <editor-modal
        :edition_stack="edition_stack"
        v-on:cancel="status = null"
        v-on:saved="
          edition_stack = [];
          status = null;
        "
      />
    </div>
  </div>
</template>

<script>
import Vue from "vue";

import ExternalVueAppEvent from "../../ExternalVueAppEvent.js";
import EditorTag from "./editor-tag.vue";
import EditorModal from "./editor-modal.vue";

export default Vue.extend({
  props: ["user", "main_website", "editor"],
  data() {
    return {
      status: null,
      uuid: null,
      elems: {},
      elems_action: {},
      elems_deleted: {},
      edition_stack: [],
    };
  },
  watch: {
    status: function () {
      this.status ? this.editor.show() : this.editor.hide();
    },
    elems: {
      deep: true,
      handler() {
        this.set_action();
      },
    },
    edition_stack: function () {
      ExternalVueAppEvent.$emit("editor-count", this.edition_stack.length);
    },
  },
  components: {
    EditorTag,
    EditorModal,
  },
  beforeMount() {
    window.addEventListener("beforeunload", this.beforeunload);
  },
  beforeDestroy() {
    window.removeEventListener("beforeunload", this.beforeunload);
  },
  mounted() {
    ExternalVueAppEvent.$on("editor-load", this.load);
    ExternalVueAppEvent.$on("editor-save", () => {
      this.status = "saving";
    });
  },
  methods: {
    load(uuid, fix) {
      this.status = "loading";

      fetch(
        API_URL +
          `/api/0.3/issue/${uuid}/fresh_elems${
            typeof fix !== "undefined" ? `/${fix}` : ""
          }`,
        {
          headers: new Headers({
            "Accept-Language": this.$route.params.lang,
          }),
        }
      )
        .then((response) => response.json())
        .then((response) => {
          Object.assign(this, response);
          this.uuid = uuid;
          this.status = "editor";
          this._setTags(response.elems, response.fix);
        })
        .catch((error) => {
          this.error = error.message;
          this.status = "error";
        });
    },
    validate(uuid) {
      Object.entries(JSON.parse(JSON.stringify(this.elems))).forEach(
        ([type_id, elem]) => {
          const changed = elem.tags.some(
            (tag) =>
              ["mod", "add"].indexOf(this.elems_action[type_id][tag.key]) >= 0
          );
          if (changed) {
            elem.tags = Object.fromEntries(
              elem.tags
                .filter((tag) => tag.key != "" && tag.value != "")
                .map((tag) => [tag.key, tag.value])
            );
            this.edition_stack.push(elem);
          }
        }
      );

      fetch(API_URL + `/api/0.3/issue/${uuid}/done`).then(() => {
        this.editor._validate(uuid);
      });

      this.status = null;
    },
    cancel() {
      this.status = null;
    },
    _setTags(elems, fix) {
      this.elems_base = {};
      this.elems_action_base = {};
      this.elems = {};
      elems.forEach((elem) => {
        const type_id = `${elem.type}${elem.id}`;
        this.elems_base[type_id] = {
          type: elem.type,
          id: elem.id,
          version: elem.version,
          tags: elem.tags.map((tag) => ({
            key: tag.k,
            value: tag.v,
            id: Math.random(),
          })),
        };
        this.elems_action_base[type_id] = {};
        elem.tags.forEach((tag) => {
          this.elems_action_base[type_id][tag.k] = fix ? "del" : "same";
        });
      });
      this.elems = JSON.parse(JSON.stringify(this.elems_base));
      if (fix) {
        Object.entries(fix).forEach(([type_id, tags]) => {
          Object.entries(tags).forEach(([key, value]) => {
            const tag = this.elems[type_id].tags.find((tag) => tag.key == key);
            if (tag) {
              tag.value = value;
            } else {
              this.elems[type_id].tags.push({ key, value, id: Math.random() });
            }
          });

          this.elems[type_id].tags = this.elems[type_id].tags.filter(
            (tag) => tag.key in tags
          );
        });
      }

      this.set_action();
      this.focus();
    },
    focus() {
      // Set focus on last input
      this.$nextTick(() => {
        const inputs = Array.from(
          document
            .getElementById("editor_form")
            .querySelectorAll('input[type="text"]')
        );
        inputs[inputs.length - 1].focus();
      });
    },
    set_action() {
      this.elems_action = JSON.parse(JSON.stringify(this.elems_action_base));
      this.elems_deleted = {};
      Object.entries(this.elems).forEach(([type_id, elem]) => {
        this.elems_deleted[type_id] = [];
        this.elems_base[type_id].tags.forEach((tag) => {
          const edit_tag = this.elems[type_id].tags.find(
            (edit_tag) => edit_tag.key == tag.key && edit_tag.value != ""
          );
          if (!edit_tag) {
            tag.id = Math.random();
            this.elems_deleted[type_id].push(tag);
            this.elems_deleted[type_id].sort();
          }
        });

        const empty = elem.tags.find((tag) => tag.key == "" && tag.value == "");
        if (!empty) {
          this.elems[type_id].tags.push({
            key: "",
            value: "",
            id: Math.random(),
          });
        }

        const elem_action = this.elems_action[type_id];
        elem.tags.forEach((tag) => {
          const base_tag = this.elems_base[type_id].tags.find(
            (base_tag) => base_tag.key == tag.key
          );
          elem_action[tag.key] = !base_tag
            ? "add"
            : base_tag.value != tag.value
            ? "mod"
            : "same";
        });
      });
    },
    delete_tag(type_id, key) {
      if (this.elems_action[type_id][key] == "del") {
        const tag = this.elems_base[type_id].tags.find((tag) => tag.key == key);
        this.elems[type_id].tags.unshift(tag);
      } else {
        const index = this.elems[type_id].tags.findIndex(
          (tag) => tag.key == key
        );
        this.elems[type_id].tags.splice(index, 1);
      }
      this.focus();
    },
    beforeunload(event) {
      if (this.edition_stack.length > 0) {
        event.preventDefault();
        event.returnValue = "";
      }
    },
  },
});
</script>

<style scoped>
#editor {
  padding: 5px;
}

#editor h1 {
  margin: 0;
}

#editor a.object_link {
  display: block;
  text-align: right;
  font-size: 80%;
}

#editor .tags {
  border: solid 1px gray;
  background: #e7e7e7;
}

#editor #buttons {
  float: right;
}
</style>
