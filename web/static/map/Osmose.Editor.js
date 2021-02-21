require('leaflet');

require('./Osmose.Editor.css');
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


const OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  _modifiyObjectStack: {},

  _deleteObjectStack: {},

  initialize(placeholder, options) {
    this._$container = $(`#${placeholder}`);
    $('#menu-editor-save').click((event) => {
      this._save(event.currentTarget);
      return false;
    });

    this.saveModal = $('#dialog_editor_save_modal');
    this.saveModal.on('shown.bs.modal', (event) => {
      $('#save_button', this.saveModal).trigger('focus');
    });
    $('#save_button', this.saveModal).click(() => {
      const comment = document.forms.editor_save_form.elements.comment.value;
      const source = document.forms.editor_save_form.elements.source.value;
      const type = document.forms.editor_save_form.elements.type.value;
      const reuseChangeset = document.forms.editor_save_form.elements.reuse_changeset.checked;
      this.saveModal.find('#save_changeset').hide();
      this.saveModal.find('#save_uploading').show();
      this.saveModal.find('.modal-footer').hide();

      this._upload(comment, source, type, reuseChangeset, () => {
        this.saveModal.find('#save_changeset').show();
        this.saveModal.find('#save_uploading').hide();
        this.saveModal.find('.modal-footer').show();
      });
    });

    $(window).on('beforeunload', L.Util.bind(this._beforeunload, this));

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  edit(layer, uuid, fix) {
    this.show();
    if (this._$container.data().user != true) {
      return;
    }

    this.layer = layer;
    ExternalVueAppEvent.$emit('editor-load', uuid, fix);
  },

  _setTags(data) {
    data.elems.forEach((elem) => {
      const reftags = {};
      elem.tags.forEach((ee) => {
        reftags[ee.k] = ee.v;
      });
      this._build(elem.type, elem.id, reftags, (data.fix && data.fix[elem.type + elem.id]) || reftags);
      $(`.tags[data-type="${elem.type}"][data-id="${elem.id}"]`, this._$container).data('reftags', reftags);
    });
    $('#editor form input[type="text"]:last').focus();
  },

  _beforeunload() {
    const n = Object.keys(this._modifiyObjectStack).length + Object.keys(this._deleteObjectStack).length;
    if (n > 0) {
      return 'Quit ?';
    }
  },

  _upload(comment, source, type, reuseChangeset, always) {
    const url = '../editor/save';
    $.ajax({
      url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        tag: {
          comment,
          source,
          type,
        },
        reuseChangeset,
        modify: this._modifiyObjectStack,
        delete: this._deleteObjectStack,
      }),
    }).done(() => {
      this._modifiyObjectStack = {};
      this._deleteObjectStack = {};
      this._count_touched();
      this.saveModal.modal('hide');
    }).fail((xhr, err) => {
      alert(`Fails post to ${url}\nreadyState: ${xhr.readyState}\nstatus: ${xhr.status}`);
    }).always(always);
  },

  _save() {
    this.saveModal.find('#editor-modify-count').val(Object.keys(this._modifiyObjectStack).length);
    this.saveModal.find('#editor-delete-count').val(Object.keys(this._deleteObjectStack).length);
    this.saveModal.modal('show');
  },

  _cancel() {
    this.hide();
  },

  _validate(uuid) {
    $.ajax({
      url: API_URL + `/api/0.3/issue/${uuid}/done`,
    }).done((d) => {
      this.errors.corrected(this.layer);
    });

    $.each(this._extractData(), (i, elem) => {
      if (elem.touched) {
        this._modifiyObjectStack[i] = elem;
        delete this._modifiyObjectStack[i].touched;
      }
    });
    this.hide();
    this._count_touched();
  },

  _count_touched() {
    const n = Object.keys(this._modifiyObjectStack).length + Object.keys(this._deleteObjectStack).length;
    const es = $('#menu-editor-save');
    if (n > 0) {
      es.show();
      es.find('#menu-editor-save-number').text(Object.keys(this._modifiyObjectStack).length);
    } else {
      es.hide();
    }
  },

  _extractData() {
    const data = {};
    $('.tags', this._$container).each((iii, eee) => {
      const elem = {};
      $('div:not(.del)', eee).each((ii, ee) => {
        $(" input[type='text']", ee).each((i, e) => {
          if (e.value && e.dataset.key) {
            elem[e.dataset.key] = e.value.split('=').splice(1).join('=');
          }
        });
      });
      data[eee.dataset.type + eee.dataset.id] = {
        type: eee.dataset.type,
        id: eee.dataset.id,
        version: eee.dataset.version,
        touched: eee.dataset.touched === 'true',
        tag: elem,
      };
    });
    return data;
  },

  _change(e) {
    let curValue = e.target.value.trim();
    if (curValue.indexOf('=') < 0 || curValue[0] === '=' || curValue[curValue.length - 1] === '=') {
      curValue = '';
    } else {
      const edited = curValue.split('=');
      const k = edited[0].trim();
      let editedKey = e.target.dataset.key;
      if (!editedKey || k !== editedKey) {
        editedKey = k;
        $(`input[type='text'][data-key='${editedKey}']`, this._$container).attr('data-key', null);
        e.target.dataset.key = editedKey;
      }
    }

    const tags = $(e.target).closest('.tags');
    this._build(tags.data('type'), tags.data('id'), tags.data('reftags'), this._extractData()[tags.data('type') + tags.data('id')].tag);
  },

  _build(type, id, reftags, data) {
    const tags = $(`.tags[data-type="${type}"][data-id="${id}"]`, this._$container);
    let touched = false;
    const del = $('.del', tags);
    del.empty();
    Object.keys(reftags).forEach((e) => {
      if (data[e] === undefined) {
        var h = $(`<span class="line"><span>-</span><input type="text" name="tags_del[]"/><a href="#">×</a></span>`)
        $('input', h).attr('value', `${e}=${reftags[e]}`);
        $('input', h).attr('data-key', e);
        del.append(h);
        touched = true;
      }
    });

    const same = $('.same', tags);
    same.empty();
    Object.keys(reftags).forEach((e) => {
      if (data[e] !== undefined && data[e] === reftags[e]) {
        var h = $(`<span class="line"><span>=</span><input type="text" name="tags_del[]"/><a href="#">×</a></span>`);
        $('input', h).attr('value', `${e}=${reftags[e]}`);
        $('input', h).attr('data-key', e);
        same.append(h);
      }
    });

    const mod = $('.mod', tags);
    mod.empty();
    Object.keys(reftags).forEach((e) => {
      if (data[e] !== undefined && data[e] !== reftags[e]) {
        var h = $(`<span class="line"><span>~</span><input type="text" name="tags_mod[]"/><a href="#">×</a></span>`);
        $('input', h).attr('value', `${e}=${data[e]}`);
        $('input', h).attr('data-key', e);
        $('input', h).attr('title', reftags[e]);
        mod.append(h);
        touched = true;
      }
    });

    const add = $('.add', tags);
    add.empty();
    Object.keys(data).forEach((e) => {
      if (reftags[e] === undefined) {
        var h = $(`<span class="line"><span>+</span><input type="text" name="tags_add[]"/><a href="#">×</a></span>`);
        $('input', h).attr('value', `${e}=${data[e]}`);
        $('input', h).attr('data-key', e);
        add.append(h);
        touched = true;
      }
    });
    add.append($('<span class="line"><span>+</span><input type="text" name="tags_add[]" value=""></span>'));

    tags.attr('data-touched', touched);

    $("input[type='text']", tags).change((e) => {
      this._change(e);
    });
    $("input[type='text']", tags).keypress((e) => {
      this._keypress(e);
    });
    $('a', tags).click((e) => {
      this._delete_tag(e);
      return false;
    });
  },

  _delete_tag(e) {
    const action = $(e.target).closest('div');
    const span = $(e.target).closest('span');
    const input = span.find('input').get()[0];
    const tags = $(e.target).closest('.tags');
    const reftags = tags.data('reftags');
    if (action.hasClass('del')) {
      span.appendTo(tags.find('.add'));
    } else if (action.hasClass('mod')) {
      input.value = `${input.dataset.key}=${reftags[input.dataset.key]}`;
    } else if (action.hasClass('same') || action.hasClass('add')) {
      input.value = '';
    }
    this._change({
      target: input,
    });
  },

  _keypress(e) {
    if (e.key === 'Up') {
      const inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) - 1).focus();
    } else if (e.key === 'Down' || e.key === 'Enter') {
      const inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) + 1).focus();
    } else if (e.key === 'Backspace' && e.ctrlKey) { // Ctrl + Backspace
      this._delete_tag(e);
    }
  },
});


export { OsmoseEditor as default };
