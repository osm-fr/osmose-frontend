OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  _editedObjectStack: {},

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
      url: '../api/0.2/error/' + error,
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
    var self = this;
    $.ajax({
      url: "../editor/save",
      type: "POST",
      data: JSON.stringify(self._editedObjectStack),
    }).done(function () {
      alert("Save OK"); //////////////////// TODO
    }).fail(function () {
      alert("Save Fail"); ////////////////// TODO
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
    var n = Object.keys(this._editedObjectStack).length,
      es = $("#menu-editor-save");
    if (n > 0) {
      es.show();
      es.find("#menu-editor-save-number").text(Object.keys(this._editedObjectStack).length);
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
    }

    var edited_key = e.target.dataset.key;
    if (!edited_key && cur_value.indexOf("=") >= 0) {
      var edited = cur_value.split("=");
      edited_key = edited[0].trim();
      $("input[type='text'][data-key='" + edited_key + "'", this._$container).attr('data-key', null);
      e.target.dataset.key = edited_key;
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
