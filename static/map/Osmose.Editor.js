OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  includes: L.Mixin.Events,

  initialize: function (placeholder, options) {
    this._$container = $("#" + placeholder);

    var self = this;
    $(".validate").click(function () {
      self._validate(this);
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
        content = $(Mustache.render(template, data)),
        reftags = {};
      $.each(data.elems[0].tags, function (i, e) {
        reftags[e.k] = e.v;
      });
      self._$container.html(content);
      $("form", self._$container).data('reftags', reftags);
      self._build(reftags, reftags);
      self.toggle();
    });
  },

  validate: function (e) {},

  _change: function (e) {
    var cur_value = e.target.value.trim();
    if (cur_value.indexOf("=") < 0 || cur_value.startsWith("=") || cur_value.endsWith("=")) {
      cur_value = "";
    }

    var edited = cur_value.split("=");
    var edited_key = e.target.dataset.key;
    if (!edited_key && cur_value.indexOf("=") >= 0) {
      edited_key = edited[0].trim();
    }

    var data = {};
    $("form div div:not(.del) input[type='text']", this._$container).each(function (i, e) {
      if (e.value && e.dataset.key && e.dataset.key != edited_key) {
        data[e.dataset.key] = e.value.split("=")[1];
      }
    });

    if (edited[1]) {
      data[edited_key] = edited[1].trim();
    }

    var reftags = $("form", this._$container).data('reftags');

    this._build(reftags, data);
  },

  _build: function (reftags, data) {
    var del = $('.del', this._$container);
    del.empty();
    $.each(reftags, function (e) {
      if (!data[e]) {
        //////////:::: FIXME "
        del.append($('<span>-</span><input type="text" name="tags_del[]" value="' + e + '=' + reftags[e] + '" data-key="' + e + '"/>'));
      }
    });

    var same = $('.same', this._$container);
    same.empty();
    $.each(reftags, function (e) {
      if (data[e] && data[e] == reftags[e]) {
        //////////:::: FIXME "
        same.append($('<span>=</span><input type="text" name="tags_del[]" value="' + e + '=' + reftags[e] + '" data-key="' + e + '"/>'));
      }
    });

    var mod = $('.mod', this._$container);
    mod.empty();
    $.each(reftags, function (e) {
      if (data[e] && data[e] != reftags[e]) {
        //////////:::: FIXME "
        mod.append($('<span>~</span><input type="text" name="tags_mod[]" value="' + e + '=' + data[e] + '" data-key="' + e + '"/><span class="old">(' + reftags[e] + ')</span>'));
      }
    });

    var add = $('.add', this._$container);
    add.empty();
    $.each(data, function (e) {
      if (!reftags[e]) {
        //////////:::: FIXME "
        add.append($('<span>+</span><input type="text" name="tags_add[]" value="' + e + '=' + data[e] + '" data-key="' + e + '"/>'));
      }
    });
    add.append($('<span>+</span><input type="text" name="tags_add[]" value="">'));

    var self = this;
    $("input[type='text']", this._$container).change(function (e) {
      self._change(e);
    });
    $("input[type='text']", this._$container).keypress(function (e) {
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
