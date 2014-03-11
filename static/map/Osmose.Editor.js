OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  _modifiyObjectStack: {},

  _deleteObjectStack: {},

  initialize: function (placeholder, options) {
    this._$container = $("#" + placeholder);

    var self = this;
    $("#menu-editor-save").click(function () {
      self._save(this);
    });

    this.saveDialog = $('#dialog_editor_save_popup');
    this.saveDialog.dialog({
      autoOpen: false,
      modal: true,
      buttons: [{
        text: self.saveDialog.attr('data-button_cancel'),
        click: function () {
          self.saveDialog.dialog('close');
        }
      }, {
        text: self.saveDialog.attr('data-button_save'),
        click: function () {
          var dialog_content = self.saveDialog.html(),
            comment = document.forms.editor_save_form.elements.comment.value,
            source = document.forms.editor_save_form.elements.source.value,
            type = document.forms.editor_save_form.elements.type.value
            reuse_changeset = document.forms.editor_save_form.elements.reuse_changeset.checked;
          self.saveDialog.html("<center><img src='../images/throbbler.gif' alt='downloading'></center>");
          self.saveDialog.parent().find('.ui-dialog-buttonpane').hide();

          self._upload(comment, source, type, reuse_changeset, function () {
            self.saveDialog.html(dialog_content);
            self.saveDialog.parent().find('.ui-dialog-buttonpane').show();
          });
        },
      }]
    });

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  edit: function (layer, error, type, id, fix) {
    this.show();
    if (this._$container.data().user != "True") {
      return;
    }

    this._$container.html("<center><img src='../images/throbbler.gif' alt='downloading'></center>");
    var self = this;
    $.ajax({
      url: '../api/0.2/error/' + error + '/fresh_elems' + (fix ? '/' + fix : ''),
      dataType: 'json'
    }).done(function (data) {
      var template = $('#editorTpl').html(),
        content = $(Mustache.render(template, data));
      self._$container.html(content);
      $("#validate", self._$container).click(function () {
        self._validate(this);
      });
      $("#corrected", self._$container).click(function () {
        self._validate(this);
        $.ajax({
          url: '../api/0.2/error/' + error + '/done'
        }).done(function (data) {
          self.errors.corrected(layer);
        });
      });
      $("#cancel", self._$container).click(function () {
        self._cancel(this);
      });

      $.each(data.elems, function (i, elem) {
        var reftags = {};
        $.each(elem.tags, function (i, e) {
          reftags[e.k] = e.v;
        });
        self._build(elem.type, elem.id, reftags, (data.fix && data.fix[elem.type + elem.id]) || reftags);
        $('.tags[data-type="' + elem.type + '"][data-id="' + elem.id + '"]', self._$container).data('reftags', reftags);
      });
      $('form .tags[data-type="' + type + '"][data-id="' + id + '"] input[type="text"]:last', self._$container).focus();
    }).fail(function (xhr, err) {
      self._$container.html("readyState: " + xhr.readyState + "\nstatus: " + xhr.status);
    });
  },

  _upload: function (comment, source, type, reuse_changeset, always) {
    var self = this;
    $.ajax({
      url: '../editor/save',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        tag: {
          comment: comment,
          source: source,
          type: type
        },
        reuse_changeset: reuse_changeset,
        modify: self._modifiyObjectStack,
        delete: self._deleteObjectStack
      }),
    }).done(function () {
      self._modifiyObjectStack = {};
      self._deleteObjectStack = {};
      self._count_touched();
      self.saveDialog.dialog('close');
    }).fail(function (xhr, err) {
      alert("readyState: " + xhr.readyState + "\nstatus: " + xhr.status);
    }).always(always);
  },

  _save: function (e) {
    this.saveDialog.find('#editor-modify-count').text(Object.keys(this._modifiyObjectStack).length);
    this.saveDialog.find('#editor-delete-count').text(Object.keys(this._deleteObjectStack).length);
    this.saveDialog.dialog('open');
  },

  _cancel: function (e) {
    this.hide();
  },

  _validate: function (e) {
    var self = this;
    $.each(this._extractData(), function (i, e) {
      if (e.touched) {
        self._modifiyObjectStack[i] = e;
        delete self._modifiyObjectStack[i].touched;
      }
    });
    this.hide();
    this._count_touched();
  },

  _count_touched: function () {
    var n = Object.keys(this._modifiyObjectStack).length + Object.keys(this._deleteObjectStack).length,
      es = $("#menu-editor-save");
    if (n > 0) {
      es.show();
      es.find("#menu-editor-save-number").text(Object.keys(this._modifiyObjectStack).length);
    } else {
      es.hide();
    }
  },

  _extractData: function () {
    var data = {};
    $('.tags', this._$container).each(function (iii, eee) {
      var elem = {};
      $("div:not(.del)", eee).each(function (ii, ee) {
        $(" input[type='text']", ee).each(function (i, e) {
          if (e.value && e.dataset.key) {
            elem[e.dataset.key] = e.value.split("=")[1];
          }
        });
      });
      data[eee.dataset.type + eee.dataset.id] = {
        type: eee.dataset.type,
        id: eee.dataset.id,
        version: eee.dataset.version,
        touched: eee.dataset.touched == "true",
        tag: elem
      };
    });
    return data;
  },

  _change: function (e) {
    var cur_value = e.target.value.trim();
    if (cur_value.indexOf("=") < 0 || cur_value[0] == "=" || cur_value[cur_value.length - 1] == "=") {
      cur_value = "";
    } else {
      var edited = cur_value.split("="),
        k = edited[0].trim(),
        edited_key = e.target.dataset.key;
      if (!edited_key || k != edited_key) {
        edited_key = k;
        $("input[type='text'][data-key='" + edited_key + "'", this._$container).attr('data-key', null);
        e.target.dataset.key = edited_key;
      }
    }

    var tags = $(e.target).closest(".tags");
    this._build(tags.data('type'), tags.data('id'), tags.data('reftags'), this._extractData()[tags.data('type') + tags.data('id')].tag);
  },

  _build: function (type, id, reftags, data) {
    var tags = $('.tags[data-type="' + type + '"][data-id="' + id + '"]', this._$container),
      touched = false;

    var del = $('.del', tags);
    del.empty();
    $.each(reftags, function (e) {
      if (data[e] == undefined) {
        var value = $('<div/>').text(e + '=' + reftags[e]).html(),
          key = $('<div/>').text(e).html();
        del.append($('<span class="line"><span>-</span><input type="text" name="tags_del[]" value="' + value + '" data-key="' + key + '"/><a href="#">×</a></span>'));
        touched = true;
      }
    });

    var same = $('.same', tags);
    same.empty();
    $.each(reftags, function (e) {
      if (data[e] != undefined && data[e] == reftags[e]) {
        var value = $('<div/>').text(e + '=' + reftags[e]).html(),
          key = $('<div/>').text(e).html();
        same.append($('<span class="line"><span>=</span><input type="text" name="tags_del[]" value="' + value + '" data-key="' + key + '"/><a href="#">×</a></span>'));
      }
    });

    var mod = $('.mod', tags);
    mod.empty();
    $.each(reftags, function (e) {
      if (data[e] != undefined && data[e] != reftags[e]) {
        var value = $('<div/>').text(e + '=' + data[e]).html(),
          key = $('<div/>').text(e).html(),
          old = $('<div/>').text(reftags[e]).html();
        mod.append($('<span class="line"><span>~</span><input type="text" name="tags_mod[]" value="' + value + '" data-key="' + key + '" title="' + old + '"/><a href="#">×</a></span>'));
        touched = true;
      }
    });

    var add = $('.add', tags);
    add.empty();
    $.each(data, function (e) {
      if (reftags[e] == undefined) {
        var value = $('<div/>').text(e + '=' + data[e]).html(),
          key = $('<div/>').text(e).html();
        add.append($('<span class="line"><span>+</span><input type="text" name="tags_add[]" value="' + value + '" data-key="' + key + '"/><a href="#">×</a></span>'));
        touched = true;
      }
    });
    add.append($('<span class="line"><span>+</span><input type="text" name="tags_add[]" value=""></span>'));

    tags.attr('data-touched', touched);

    var self = this;
    $("input[type='text']", tags).change(function (e) {
      self._change(e);
    });
    $("input[type='text']", tags).keypress(function (e) {
      self._keypress(e);
    });
    $("a", tags).click(function (e) {
      self._delete_tag(e);
      return false;
    });
  },

  _delete_tag: function (e) {
    var action = $(e.target).closest('div'),
      span = $(e.target).closest('span'),
      input = span.find('input').get()[0],
      tags = $(e.target).closest(".tags"),
      reftags = tags.data('reftags');
    if (action.hasClass('del')) {
      span.appendTo(tags.find('.add'));
    } else if (action.hasClass('mod')) {
      input.value = input.dataset.key + '=' + reftags[input.dataset.key];
    } else if (action.hasClass('same') || action.hasClass('add')) {
      input.value = '';
    }
    this._change({
      target: input
    });
  },

  _keypress: function (e) {
    if (e.key == "Up") {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) - 1).focus();
    } else if (e.key == "Down" || e.key == "Enter") {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) + 1).focus();
    } else if (e.key == "Backspace" && e.ctrlKey) { // Ctrl + Backspace
      this._delete_tag(e);
    }
  },
});
