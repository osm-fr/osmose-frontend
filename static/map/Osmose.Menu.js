OsmoseMenu = L.Control.Sidebar.extend({

  includes: L.Mixin.Events,

  initialize: function (placeholder, options) {
    this._$container = $("#"+placeholder);

    this._openMenu();
    this._countItemAll();
    this._change_level();

    var self = this;
    $("div#tests input[type='checkbox']").change(function() {
      self._checkbox_click(this);
    });
    $(".toggleAllItem").click(function() {
      self._toggleAllItem(this);
    });
    $(".invertAllItem").click(function() {
      self._invertAllItem();
    });
    $(".toggleCateg").click(function() {
      self._toggleCateg(this);
    });
    $("#level").click(function() {
      self._change_level();
    });
    $("#togglemenu").click(function() {
      self._toggleMenu();
    });

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  // Menu
  _openMenu: function () {
    this._$container.data('opened', true);
    $("div#tests").show();
    $("#togglemenu").html('-');
  },

  _closeMenu: function () {
    this._$container.data('opened', false);
    $("div#tests").hide();
    $("#togglemenu").html('+');
  },

  _toggleMenu: function () {
    if (!this._$container.data('opened')) {
      this._openMenu();
    } else {
      this._closeMenu();
    }
  },

  // Update checkbox count
  _countItem: function (test_group) {
    var count_checked = 0,
      count_tests = 0;
    $.each($("input[type='checkbox']", test_group), function(index, checkbox) {
      if($(checkbox).is(':checked')) {
        count_checked++;
      }
      count_tests++;
    });
    $(".count", test_group).html(count_checked + '/' + count_tests);
  },

  _countItemAll: function () {
    var self = this;
    $(".test_group").each( function(i, group) {
      self._countItem(group);
    });
  },

  // Click on a checkbox
  _checkbox_click: function (cb) {
    this._countItem($(cb).closest(".test_group"));
    this._itemChanged();
  },

  // Show or hide a group of tests
  _toggleCateg: function (id) {
    var ul = $("ul", $(id).closest(".test_group"));
    if (ul.is(':visible')) {
      ul.slideUp(200);
      $(id).addClass('folded');
    } else {
      ul.slideDown(200);
      $(id).removeClass('folded');
    }
  },

  // Check or uncheck a categ of tests.
  _toggleAllItem: function (link) {
    var test_group = $(link).closest(".test_group, body"),
      checkbox = $("input[type='checkbox']", test_group);
    if($(link).data().view == "all"){
      checkbox.attr('checked', true);
    } else {
      checkbox.attr('checked', false);
    }

    if(test_group.prop("tagName") == "BODY") {
      this._countItemAll(test_group);
    } else {
      this._countItem(test_group);
    }
    this._itemChanged();
  },

  // Invert item check
  _invertAllItem: function () {
    $("input[type='checkbox']").each( function() {
      $(this).attr('checked', !$(this).attr('checked'));
    });

    this._countItemAll();
    this._itemChanged();
  },

  // Change level
  _change_item_display: function (l) {
    $("div#tests li").each(function () {
      var id = parseInt($(this).attr('id').replace(/item_desc/, ''));
      if (jQuery.inArray(id, item_levels[l]) >= 0) {
        $("#item_desc" + id).show();
      } else {
        $("#item_desc" + id).hide();
      }
    });
    var ll = l.split(',');
    for (var i = 1; i <= 3; i++) {
      if ($.inArray(i.toString(), ll) >= 0) {
        $(".level-" + i).removeClass("disabled");
      } else {
        $(".level-" + i).addClass("disabled");
      }
    }
  },

  _change_level: function change_level() {
    var new_level = $("#level").val();
    this._change_item_display(new_level? new_level : "1,2,3");

    this._itemChanged();
  },

  _itemChanged: function () {
    this._urlPart = this._buildUrlPart();
    this.fire('itemchanged', {urlPart: this._urlPart});
  },

  urlPart: function () {
    return this._urlPart;
  },

  _buildUrlPart: function () {
    // items list
    var ch = "";
    if ($(".test_group :checkbox:not(:checked)").length == 0) {
      ch = "xxxx";
    } else {
      $(".test_group").each(function () {
        var id = this.id;
        v = $("h1 span", this).text().split("/");
        if (v[0] == v[1]) {
          ch += id.substring(5, 6) + "xxx,";
        } else {
          $(":checked", this).each(function () {
            ch += this.name.substr(4) + ",";
          })
        }
      })
    }
    ch = ch.replace(/,$/, '');

    return {
      item: ch,
      level: document.myform.level.value,
    };
  },
});
