require('leaflet');
require('leaflet-sidebar');
require('leaflet-sidebar/src/L.Control.Sidebar.css');
const Cookies = require('js-cookie');
const Marked = require('marked');
const path = require('path');

require('./Osmose.Doc.css');


export const OsmoseDoc = L.Control.Sidebar.extend({

  options: {
//    closeButton: false,
    autoPan: false,
  },

  initialize(placeholder, options) {
    this._$container = $(`#${placeholder}`);
    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);

    let show = localStorage.getItem('doc.show');
    if (show !== null && JSON.parse(show) === false) {
      L.Control.Sidebar.prototype.hide.call(this);
    } else {
      this.show();
    }
  },

  toggle() {
    localStorage.setItem('doc.show', !JSON.parse(localStorage.getItem('doc.show')));
    L.Control.Sidebar.prototype.toggle.call(this);
    if ($('.leaflet-active-area').css('right') === '0px') {
      $('.leaflet-active-area').css('right', '');
    } else {
      $('.leaflet-active-area').css('right', '0px');
    }
  },

  show(item, classs) {
    localStorage.setItem('doc.show', true);
    L.Control.Sidebar.prototype.show.call(this);
    if (item !== undefined) {
      this._load(item, classs);
    }
  },

  load(item, classs) {
    if (this.isVisible()) {
      this._load(item, classs);
    }
  },

  _load(item, classs) {
    if (item == this._last_item && classs == this._last_classs) {
      return;
    }

    const template = $('#docTpl').html().replace('&amp;', '&');
    this._$container.html('');

    $.ajax({
      url: API_URL + `/api/0.3/items/${item}/class/${classs}?langs=auto`,
      dataType: 'json',
      success: (data) => {
        this._last_item = item;
        this._last_classs = classs;

        data = data['categories'][0]['items'][0]['class'][0];

        var resource_url;
        try {
          if (data['resource']) {
            resource_url = new URL(data['resource']);
          }
        } catch { }

        data = {
          title: data['title'] && data['title']['auto'],
          detail: data['detail'] && Marked(data['detail']['auto']),
          fix: data['fix'] && Marked(data['fix']['auto']),
          trap: data['trap'] && Marked(data['trap']['auto']),
          example: data['example'] && Marked(data['example']['auto']),
          source_link: data['source'],
          source_title: data['source'] && path.basename(data['source']),
          resource_link: data['resource'],
          resource_title: resource_url ? `${resource_url.protocol}//${resource_url.host}` : data['resource'],
        };

        const content = Mustache.render(template, data);
        this._$container.html(content);
      }
    });
  },
});

export const OsmoseDocToggle = L.Control.extend({

  options: {
    position: 'topright',
    menuText: 'ℹ',
    menuTitle: 'Doc',
  },

  initialize(menu, options) {
    L.Control.prototype.initialize.call(this, options);
    this._menu = menu;
  },


  onAdd(map) {
    const menuName = 'leaflet-control-menu-toggle';
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`);
    this._map = map;
    this._zoomInButton = this._createButton(this.options.menuText, this.options.menuTitle, `${menuName}-in`, container, this._menuToggle, this);
    return container;
  },

  _menuToggle() {
    this._menu.toggle();
  },

  _createButton(html, title, className, container, fn, context) {
    const link = L.DomUtil.create('a', className, container);
    link.innerHTML = html;
    link.href = '#';
    link.title = title;

    const stop = L.DomEvent.stopPropagation;

    L.DomEvent
      .on(link, 'click', stop)
      .on(link, 'mousedown', stop)
      .on(link, 'dblclick', stop)
      .on(link, 'click', L.DomEvent.preventDefault)
      .on(link, 'click', fn, context)
      .on(link, 'click', this._refocusOnMap, context);

    return link;
  },
});
