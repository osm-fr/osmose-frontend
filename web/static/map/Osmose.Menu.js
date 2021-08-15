import * as Cookies from 'js-cookie';

import './Osmose.Menu.css';
import SidebarToggle from './SidebarToggle.js';
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


const OsmoseMenu = SidebarToggle.extend({

  options: {
    closeButton: false,
    localStorageProperty: "menu.show",
  },

  initialize(placeholder, permalink, params, options) {
    this._permalink = permalink;
    this._params = params;

    SidebarToggle.prototype.initialize.call(this, placeholder, options);
  },

  init() {
    this._setParams({ params: this._params });
    this._permalink.on('update', this._setParams, this);
  },

  _itemChanged(item_mask, level, fixable, tags) {
    const cookiesOptions = {
      expires: 365,
      path: '/',
    };

    if (!level) {
      Cookies.remove('last_level', cookiesOptions);
    } else {
      Cookies.set('last_level', level, cookiesOptions);
    }

    if (!item_mask) {
      Cookies.set('last_item', '', cookiesOptions);
    } else {
      Cookies.set('last_item', item_mask, cookiesOptions);
    }

    if (!tags) {
      Cookies.remove('last_tags', cookiesOptions);
    } else {
      Cookies.set('last_tags', tags, cookiesOptions);
    }

    if (!fixable) {
      Cookies.remove('last_fixable', cookiesOptions);
    } else {
      Cookies.set('last_fixable', fixable, cookiesOptions);
    }

    this._permalink.update_item({
      item: item_mask,
      level,
      tags,
      fixable,
    });
  },

  _setParams(e) {
    const { params } = e;
    ExternalVueAppEvent.$emit("item-params-changed", params);
  },
});

export { OsmoseMenu as default };
