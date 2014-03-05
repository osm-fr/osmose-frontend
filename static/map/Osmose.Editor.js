OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  _editedObjectStack: {},

  _deletedObjectStack: {},

  initialize: function (placeholder, options) {
    this._$container = $("#" + placeholder);

    var self = this;
    $("#menu-editor-save").click(function () {
      self._save(this);
    });

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  edit: function (error, type, id) {
    var self = this;
    $.ajax({
      url: '../api/0.2/error/' + error + '/fresh_elems',
      dataType: 'json'
    }).done(function (data) {
      var template = $('#editorTpl').html(),
        content = $(Mustache.render(template, data));
      self._$container.html(content);
      $("#validate", self._$container).click(function () {
        self._validate(this);
      });
      $("#cancel", self._$container).click(function () {
        self._cancel(this);
      });

      $.each(data.elems, function (i, elem) {
        var reftags = {};
        $.each(elem.tags, function (i, e) {
          reftags[e.k] = e.v;
        });
        self._build(elem.type, elem.id, reftags, reftags);
        $('.tags[data-type="' + elem.type + '"][data-id="' + elem.id + '"]', self._$container).data('reftags', reftags);
      });
      $('form .tags[data-type="' + type + '"][data-id="' + id + '"] input[type="text"]:last', self._$container).focus();
      self.show();
    });
  },

  _save: function (e) {
    var self = this,
      dialog = $('#dialog_editor_save_popup');

    dialog.find('#editor-edited-count').text(Object.keys(this._editedObjectStack).length);
    dialog.find('#editor-deleted-count').text(Object.keys(this._deletedObjectStack).length);

    dialog.dialog({
      modal: true,
      buttons: [{
        text: dialog.attr('data-button_cancel'),
        click: function () {
          $(this).dialog('close');
        }
      }, {
        text: dialog.attr('data-button_save'),
        click: function () {
          var t = this;
          $.ajax({
            url: '../editor/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
              comment: document.forms.editor_save_form.elements.comment.value,
              source: document.forms.editor_save_form.elements.source.value,
              type: document.forms.editor_save_form.elements.type.value,
              edited: self._editedObjectStack,
              deleted: self._deletedObjectStack
            }),
          }).done(function () {
            self._editedObjectStack = {};
            self._deletedObjectStack = {};
            self._count_touched();
            $(t).dialog('close');
          }).fail(function (xhr, err) {
            alert("readyState: " + xhr.readyState + "\nstatus: " + xhr.status);
          });
        },
      }]
    });
  },

  _cancel: function (e) {
    this.hide();
  },

  _validate: function (e) {
    var self = this;
    $.each(this._extractData(), function (i, e) {
      if (e.touched) {
        self._editedObjectStack[i] = e;
        delete self._editedObjectStack[i]['touched'];
      }
    });
    this.hide();
    this._count_touched();
  },

  _count_touched: function () {
    var n = Object.keys(this._editedObjectStack).length + Object.keys(this._deletedObjectStack).length,
      es = $("#menu-editor-save");
    if (n > 0) {
      es.show();
      es.find("#menu-editor-save-number").text(Object.keys(this._editedObjectStack).length);
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
        touched: eee.dataset.touched == "true",
        tags: elem
      };
    });
    return data;
  },

  _change: function (e) {
    var cur_value = e.target.value.trim();
    if (cur_value.indexOf("=") < 0 || cur_value.startsWith("=") || cur_value.endsWith("=")) {
      cur_value = "";
    } else {
      var edited = cur_value.split("="),
        k = edited[0].trim();
        edited_key = e.target.dataset.key;
      if (!edited_key || k != edited_key) {
        edited_key = k;
        $("input[type='text'][data-key='" + edited_key + "'", this._$container).attr('data-key', null);
        e.target.dataset.key = edited_key;
      }
    }

    var tags = $(e.target).closest(".tags");
    this._build(tags.data('type'), tags.data('id'), tags.data('reftags'), this._extractData()[tags.data('type') + tags.data('id')].tags);
  },

  _build: function (type, id, reftags, data) {
    var tags = $('.tags[data-type="' + type + '"][data-id="' + id + '"]', this._$container),
      touched = false;

    var del = $('.del', tags);
    del.empty();
    $.each(reftags, function (e) {
      if (!data[e]) {
        var value = $('<div/>').text(e + '=' + reftags[e]).html(),
          key = $('<div/>').text(e).html();
        del.append($('<span class="line"><span>-</span><input type="text" name="tags_del[]" value="' + value + '" data-key="' + key + '"/></span>'));
        touched = true;
      }
    });

    var same = $('.same', tags);
    same.empty();
    $.each(reftags, function (e) {
      if (data[e] && data[e] == reftags[e]) {
        var value = $('<div/>').text(e + '=' + reftags[e]).html(),
          key = $('<div/>').text(e).html();
        same.append($('<span class="line"><span>=</span><input type="text" name="tags_del[]" value="' + value + '" data-key="' + key + '"/></span>'));
      }
    });

    var mod = $('.mod', tags);
    mod.empty();
    $.each(reftags, function (e) {
      if (data[e] && data[e] != reftags[e]) {
        var value = $('<div/>').text(e + '=' + data[e]).html(),
          key = $('<div/>').text(e).html(),
          old = $('<div/>').text(reftags[e]).html();
        mod.append($('<span class="line"><span>~</span><input type="text" name="tags_mod[]" value="' + value + '" data-key="' + key + '"/><span class="old">(' + old + ')</span></span>'));
        touched = true;
      }
    });

    var add = $('.add', tags);
    add.empty();
    $.each(data, function (e) {
      if (!reftags[e]) {
        var value = $('<div/>').text(e + '=' + data[e]).html(),
          key = $('<div/>').text(e).html();
        add.append($('<span class="line"><span>+</span><input type="text" name="tags_add[]" value="' + value + '" data-key="' + key + '"/></span>'));
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
  },

  _keypress: function (e) {
    if (e.key == "Up") {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) - 1).focus();
    } else if (e.key == "Down" || e.key == "Enter") {
      var inputs = $(e.target).closest('form').find("input[type='text']");
      inputs.eq(inputs.index(e.target) + 1).focus();
    } else if (e.key == "Backspace" && e.ctrlKey) { // Ctrl + Backspace
      e.target.value = '';
      this._change(e);
    }
  },
});
