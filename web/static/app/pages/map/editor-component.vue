
<template>
  <div>
    <div id="editor" v-if="!user">
      <p>
        <translate>You must be logged in order to use the tag editor</translate>
      </p>
      <a href="../login"><translate>Login</translate></a>
    </div>

    <div
      v-else
      class="modal"
      id="dialog_editor_save_modal"
      data-backdrop="static"
      tabindex="-1"
      role="dialog"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title"><translate>Save changeset</translate></h5>
          </div>
          <div class="modal-body" id="save_changeset">
            <form id="editor_save_form">
              <div class="form-group row">
                <label
                  for="editor-modify-count"
                  class="col-sm-4 col-form-label"
                >
                  <translate>Objects edited</translate>
                </label>
                <div class="col-sm-8">
                  <input
                    type="text"
                    readonly
                    class="form-control-plaintext"
                    id="editor-modify-count"
                    value=""
                  />
                </div>
              </div>
              <div class="form-group row">
                <label
                  for="editor-delete-count"
                  class="col-sm-4 col-form-label"
                >
                  <translate>Objects deleted</translate>
                </label>
                <div class="col-sm-8">
                  <input
                    type="text"
                    readonly
                    class="form-control-plaintext"
                    id="editor-delete-count"
                    value=""
                  />
                </div>
              </div>
              <div class="form-group row">
                <label for="comment" class="col-sm-4 col-form-label">
                  <translate>Comment</translate>
                </label>
                <div class="col-sm-8">
                  <input
                    class="form-control"
                    type="text"
                    name="comment"
                    id="comment"
                    :value="$t('Fixed with Osmose')"
                  />
                </div>
              </div>
              <div class="form-group row">
                <label for="source" class="col-sm-4 col-form-label">
                  <translate>Source</translate>
                </label>
                <div class="col-sm-8">
                  <input
                    class="form-control"
                    type="text"
                    name="source"
                    id="source"
                    value=""
                  />
                </div>
              </div>
              <div class="form-group row">
                <label for="type" class="col-sm-4 col-form-label">
                  <translate>Type</translate>
                </label>
                <div class="col-sm-8">
                  <input
                    class="form-control"
                    type="text"
                    name="type"
                    id="type"
                    value="fix"
                  />
                </div>
              </div>
              <div class="form-group" row>
                <div class="col-sm-12">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    name="reuse_changeset"
                    id="reuse_changeset"
                    checked="checked"
                  />
                  <label class="form-check-label" for="reuse_changeset">
                    <translate>Reuse changeset</translate>
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-body" id="save_uploading" style="display: none">
            <center>
              <img src="../../../images/throbbler.gif" alt="downloading" />
            </center>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              <translate>Cancel</translate>
            </button>
            <button type="button" class="btn btn-primary" id="save_button">
              <translate>Save</translate>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  props: ["user"],
});
</script>
