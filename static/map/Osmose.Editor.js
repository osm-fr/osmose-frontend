require('leaflet');
require('mustache');

require('./Osmose.Editor.css');


export var OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  _modifiyObjectStack: {},

  _deleteObjectStack: {},

  initialize(placeholder, options) {
    this._$container = $(`#${placeholder}`);
    const self = this;
    $('#menu-editor-save').click(function () {
      self._save(this);
      return false;
    });

    this.saveModal = $('#dialog_editor_save_modal');
    this.saveModal.on('shown.bs.modal', function () {
      $('#save_button', this.saveModal).trigger('focus');
    });
    $('#save_button', this.saveModal).click(() => {
      const comment = document.forms.editor_save_form.elements.comment.value;
      const source = document.forms.editor_save_form.elements.source.value;
      const type = document.forms.editor_save_form.elements.type.value;
      const reuse_changeset = document.forms.editor_save_form.elements.reuse_changeset.checked;
      self.saveModal.find('#save_changeset').hide();
      self.saveModal.find('#save_uploading').show();
      self.saveModal.find('.modal-footer').hide();

      self._upload(comment, source, type, reuse_changeset, () => {
        self.saveModal.find('#save_changeset').show();
        self.saveModal.find('#save_uploading').hide();
        self.saveModal.find('.modal-footer').show();
      });
    });

    $(window).on('beforeunload', L.Util.bind(this._beforeunload, this));

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  edit(layer, error, type, id, fix) {
    this.show();
    if (this._$container.data().user != 'True') {
      return;
    }

    this._$container.html("<center><img src='../images/throbbler.gif' alt='downloading'></center>");
    const self = this;
    const url = `../api/0.2/error/${error}/fresh_elems${fix ? `/${fix}` : ''}`;
    $.ajax({
      url,
      dataType: 'json',
    }).done((data) => {
      const template = $('#editorTpl').html();
      const content = $(Mustache.render(template, data));
      self._$container.html(content);
      $('#validate', self._$container).click(function () {
        self._validate(this);
        $.ajax({
          url: `../api/0.2/error/${error}/done`,
        }).done((data) => {
          self.errors.corrected(layer);
        });
      });
      $('#cancel', self._$container).click(function () {
        self._cancel(this);
      });

      $.each(data.elems, (i, elem) => {
        const reftags = {};
        $.each(elem.tags, (i, e) => {
          reftags[e.k] = e.v;
        });
        self._build(elem.type, elem.id, reftags, (data.fix && data.fix[elem.type + elem.id]) || reftags);
        $(`.tags[data-type="${elem.type}"][data-id="${elem.id}"]`, self._$container).data('reftags', reftags);
      });
      $(`form .tags[data-type="${type}"][data-id="${id}"] input[type="text"]:last`, self._$container).focus();
    }).fail((xhr, err) => {
      self._$container.html(`Fails get ${url}</br>readyState: ${xhr.readyState}</br>status: ${xhr.status}`);
    });
  },

  _beforeunload() {
    const n = Object.keys(this._modifiyObjectStack).length + Object.keys(this._deleteObjectStack).length;
    if (n > 0) {
      return 'Quit ?';
    }
  },

  _upload(comment, source, type, reuse_changeset, always) {
    const self = this;
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
        reuse_changeset,
        modify: self._modifiyObjectStack,
        delete: self._deleteObjectStack,
      }),
    }).done(() => {
      self._modifiyObjectStack = {};
      self._deleteObjectStack = {};
      self._count_touched();
      self.saveModal.modal('hide');
    }).fail((xhr, err) => {
      alert(`Fails post to ${url}\nreadyState: ${xhr.readyState}\nstatus: ${xhr.status}`);
    }).always(always);
  },

  _save(e) {
    this.saveModal.find('#editor-modify-count').val(Object.keys(this._modifiyObjectStack).length);
    this.saveModal.find('#editor-delete-count').val(Object.keys(this._deleteObjectStack).length);
    this.saveModal.modal('show');
  },

  _cancel(e) {
    this.hide();
  },

  _validate(e) {
    const self = this;
    $.each(this._extractData(), (i, e) => {
      if (e.touched) {
        self._modifiyObjectStack[i] = e;
        delete self._modifiyObjectStack[i].touched;
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
            elem[e.dataset.key] = e.value.split('=')[1];
          }
        });
      });
      data[eee.dataset.type + eee.dataset.id] = {
        type: eee.dataset.type,
        id: eee.dataset.id,
        version: eee.dataset.version,
        touched: eee.dataset.touched == 'true',
        tag: elem,
      };
    });
    return data;
  },

  _change(e) {
    let cur_value = e.target.value.trim();
    if (cur_value.indexOf('=') < 0 || cur_value[0] == '=' || cur_value[cur_value.length - 1] == '=') {
      cur_value = '';
    } else {
      const edited = cur_value.split('=');
      const k = edited[0].trim();
      let edited_key = e.target.dataset.key;
      if (!edited_key || k != edited_key) {
        edited_key = k;
        $(`input[type='text'][data-key='${edited_key}']`, this._$container).attr('data-key', null);
        e.target.dataset.key = edited_key;
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
    $.each(reftags, (e) => {
      if (data[e] == undefined) {
        const value = String($('<div/>').text(`${e}=${reftags[e]}`).html()).replace('"', '&quot;');
        const key = String($('<div/>').text(e).html()).replace('"', '&quot;');
        del.append($(`<span class="line"><span>-</span><input type="text" name="tags_del[]" value="${value}" data-key="${key}"/><a href="#">×</a></span>`));
        touched = true;
      }
    });

    const same = $('.same', tags);
    same.empty();
    $.each(reftags, (e) => {
      if (data[e] != undefined && data[e] == reftags[e]) {
        const value = String($('<div/>').text(`${e}=${reftags[e]}`).html()).replace('"', '&quot;');
        const key = String($('<div/>').text(e).html()).replace('"', '&quot;');
        same.append($(`<span class="line"><span>=</span><input type="text" name="tags_del[]" value="${value}" data-key="${key}"/><a href="#">×</a></span>`));
      }
    });

    const mod = $('.mod', tags);
    mod.empty();
    $.each(reftags, (e) => {
      if (data[e] != undefined && data[e] != reftags[e]) {
        const value = String($('<div/>').text(`${e}=${data[e]}`).html()).replace('"', '&quot;');
        const key = String($('<div/>').text(e).html()).replace('"', '&quot;');
        const old = String($('<div/>').text(reftags[e]).html()).replace('"', '&quot;');
        mod.append($(`<span class="line"><span>~</span><input type="text" name="tags_mod[]" value="${value}" data-key="${key}" title="${old}"/><a href="#">×</a></span>`));
        touched = true;
      }
    });

    const add = $('.add', tags);
    add.empty();
    $.each(data, (e) => {
      if (reftags[e] == undefined) {
        const value = String($('<div/>').text(`${e}=${data[e]}`).html()).replace('"', '&quot;');
        const key = String($('<div/>').text(e).html()).replace('"', '&quot;');
        add.append($(`<span class="line"><span>+</span><input type="text" name="tags_add[]" value="${value}" data-key="${key}"/><a href="#">×</a></span>`));
        touched = true;
      }
    });
    add.append($('<span class="line"><span>+</span><input type="text" name="tags_add[]" value=""></span>'));

    tags.attr('data-touched', touched);

    const self = this;
    $("input[type='text']", tags).change((e) => {
      self._change(e);
    });
    $("input[type='text']", tags).keypress((e) => {
      self._keypress(e);
    });
    $('a', tags).click((e) => {
      self._delete_tag(e);
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
    if (e.key == 'Up') {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) - 1).focus();
    } else if (e.key == 'Down' || e.key == 'Enter') {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) + 1).focus();
    } else if (e.key == 'Backspace' && e.ctrlKey) { // Ctrl + Backspace
      this._delete_tag(e);
    }
  },
});
