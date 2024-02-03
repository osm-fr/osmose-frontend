// Devirated from Leaflet Control.Layers.js

import { Control, Util, DomEvent, DomUtil } from 'leaflet'
import { Map as MapGl, Source } from 'maplibre-gl'

export class ControlLayers extends Control {
    private _mapGl: MapGl

    constructor(mapGl: MapGl, baseLayers: Source, overlays: Record<string, string>) {
        super()
        this._mapGl = mapGl
        this.options = {
            // @option collapsed: Boolean = true
            // If `true`, the control will be collapsed into an icon and expanded on mouse hover, touch, or keyboard activation.
            collapsed: true,
            position: 'topright',

            sortFunction(layerA, layerB, nameA, nameB) {
                return nameA < nameB ? -1 : (nameB < nameA ? 1 : 0)
            }
        }

        this._layerControlInputs = []
        this._layers = []
        this._lastZIndex = 0
        this._handlingClick = false
        this._preventClick = false

        for (const i in baseLayers) {
            if (Object.hasOwn(baseLayers, i)) {
                this._addLayer(baseLayers[i], i)
            }
        }

        Object.entries(overlays).forEach(([overlay, name]) => this._addLayer(overlay, name, true))
    }

    onAdd(map) {
        this._initLayout()
        this._update()

        this._map = map

        if (!this.options.collapsed) {
            // update the height of the container after resizing the window
            map.on('resize', this._expandIfNotCollapsed, this)
        }

        return this._container
    }

    addTo(map) {
        Control.prototype.addTo.call(this, map)
        // Trigger expand after Layers Control has been inserted into DOM so that is now has an actual height.
        return this._expandIfNotCollapsed()
    }

    // @method expand(): this
    // Expand the control container if collapsed.
    expand() {
        this._container.classList.add('leaflet-control-layers-expanded')
        this._section.style.height = null
        const acceptableHeight = this._map.getSize().y - (this._container.offsetTop + 50)
        if (acceptableHeight < this._section.clientHeight) {
            this._section.classList.add('leaflet-control-layers-scrollbar')
            this._section.style.height = `${acceptableHeight}px`
        } else {
            this._section.classList.remove('leaflet-control-layers-scrollbar')
        }
        return this
    }

    // @method collapse(): this
    // Collapse the control container if expanded.
    collapse(ev) {
        // On touch devices `pointerleave` is fired while clicking on a checkbox.
        // The control was collapsed instead of adding the layer to the map.
        // So we allow collapse if it is not touch and pointerleave.
        if (!ev || !(ev.type === 'pointerleave' && ev.pointerType === 'touch')) {
            this._container.classList.remove('leaflet-control-layers-expanded')
        }
        return this
    }

    _initLayout() {
        const className = 'leaflet-control-layers',
            container = this._container = DomUtil.create('div', className),
            collapsed = this.options.collapsed

        // makes this work on IE touch devices by stopping it from firing a mouseout event when the touch is released
        container.setAttribute('aria-haspopup', true)

        DomEvent.disableClickPropagation(container)
        DomEvent.disableScrollPropagation(container)

        const section = this._section = DomUtil.create('fieldset', `${className}-list`)

        if (collapsed) {
            this._map.on('click', this.collapse, this)

            DomEvent.on(container, {
                pointerenter: this._expandSafely,
                pointerleave: this.collapse
            }, this)
        }

        const link = this._layersLink = DomUtil.create('a', `${className}-toggle`, container)
        link.href = '#'
        link.title = 'Layers'
        link.setAttribute('role', 'button')

        DomEvent.on(link, {
            keydown(e) {
                if (e.code === 'Enter') {
                    this._expandSafely()
                }
            },
            // Certain screen readers intercept the key event and instead send a click event
            click(e) {
                DomEvent.preventDefault(e)
                this._expandSafely()
            }
        }, this)

        if (!collapsed) {
            this.expand()
        }

        this._baseLayersList = DomUtil.create('div', `${className}-base`, section)
        this._separator = DomUtil.create('div', `${className}-separator`, section)
        this._overlaysList = DomUtil.create('div', `${className}-overlays`, section)

        container.appendChild(section)
    }

    _getLayer(id) {
        for (let i = 0; i < this._layers.length; i++) {

            if (this._layers[i] && this._layers[i].layer === id) {
                return this._layers[i]
            }
        }
    }

    _addLayer(layer, name, overlay = false) {
        this._layers.push({
            layer,
            name,
            overlay
        })

        this._expandIfNotCollapsed()
    }

    _update() {
        if (!this._container) { return this }

        this._baseLayersList.replaceChildren()
        this._overlaysList.replaceChildren()

        this._layerControlInputs = []
        let baseLayersPresent, overlaysPresent, i, obj, baseLayersCount = 0

        for (i = 0; i < this._layers.length; i++) {
            obj = this._layers[i]
            this._addItem(obj)
            overlaysPresent = overlaysPresent || obj.overlay
            baseLayersPresent = baseLayersPresent || !obj.overlay
            baseLayersCount += !obj.overlay ? 1 : 0
        }

        // Hide base layers section if there's only one layer.
        if (this.options.hideSingleBase) {
            baseLayersPresent = baseLayersPresent && baseLayersCount > 1
            this._baseLayersList.style.display = baseLayersPresent ? '' : 'none'
        }

        this._separator.style.display = overlaysPresent && baseLayersPresent ? '' : 'none'

        return this
    }

    // IE7 bugs out if you create a radio dynamically, so you have to do it this hacky way (see https://stackoverflow.com/a/119079)
    _createRadioElement(name, checked) {
        const radioHtml = `<input type="radio" class="leaflet-control-layers-selector" name="${name}"${checked ? ' checked="checked"' : ''}/>`

        const radioFragment = document.createElement('div')
        radioFragment.innerHTML = radioHtml

        return radioFragment.firstChild
    }

    _addItem(obj) {
        const label = document.createElement('label')
        let input

        if (obj.overlay) {
            const checked = obj.layer == 'markers'

            input = document.createElement('input')
            input.type = 'checkbox'
            input.className = 'leaflet-control-layers-selector'
            input.defaultChecked = checked
        } else {
            const checked = this._mapGl.getSource('background').tiles[0] === obj.layer?.tiles[0]
            input = this._createRadioElement(`leaflet-base-layers_${Util.stamp(this)}`, checked)
        }

        this._layerControlInputs.push(input)
        input.layerId = obj.layer

        DomEvent.on(input, 'click', this._onInputClick, this)

        const name = document.createElement('span')
        name.innerHTML = ` ${obj.name}`

        // Helps from preventing layer control flicker when checkboxes are disabled
        // https://github.com/Leaflet/Leaflet/issues/2771
        const holder = document.createElement('span')

        label.appendChild(holder)
        holder.appendChild(input)
        holder.appendChild(name)

        const container = obj.overlay ? this._overlaysList : this._baseLayersList
        container.appendChild(label)

        return label
    }

    _onInputClick() {
        // expanding the control on mobile with a click can cause adding a layer - we don't want this
        if (this._preventClick) {
            return
        }

        const inputs = this._layerControlInputs

        this._handlingClick = true

        // Background
        inputs.filter((input) => input.checked && !this._getLayer(input.layerId).overlay).forEach((input) => {
            const source = this._mapGl.getSource('background')
            const layer = this._getLayer(input.layerId).layer
            if (source.tiles !== layer.tiles) {
                source.tileSize = layer.tileSize
                source.attribution = layer.attribution
                source.minzoom = layer.minzoom
                source.maxzoom = layer.maxzoom
                source.setTiles(layer.tiles)
            }
        })

        // Overlays
        const checkedOverlays = Object.fromEntries(inputs.filter((input) => this._getLayer(input.layerId).overlay).map((input) => [this._getLayer(input.layerId).layer, input.checked]))
        this._mapGl.getLayersOrder().forEach((layerId) => {
            const layer = this._mapGl.getLayer(layerId)
            if(layer?.source && layer.source in checkedOverlays) {
                /////////// ÇA MARCHE DÉJÀ Mais le refresh de la carte ne se fait pas, mais avec this._mapGl.redraw() plus bas
                // console.error(layerId, layer.source, layer.visibility)
                // layer.setLayoutProperty('visibility', checkedOverlays[layer.source] ? 'visible' : 'none')
                layer.visibility = checkedOverlays[layer.source] ? undefined : 'none'
            }
        })

        this._mapGl.redraw()

        this._handlingClick = false

        this._refocusOnMap()
    }

    _expandIfNotCollapsed() {
        if (this._map && !this.options.collapsed) {
            this.expand()
        }
        return this
    }

    _expandSafely() {
        const section = this._section
        this._preventClick = true
        DomEvent.on(section, 'click', DomEvent.preventDefault)
        this.expand()
        setTimeout(() => {
            DomEvent.off(section, 'click', DomEvent.preventDefault)
            this._preventClick = false
        })
    }
}


// @factory L.control.layers(baselayers?: Object, overlays?: Object, options?: Control.Layers options)
// Creates a layers control with the given layers. Base layers will be switched with radio buttons, while overlays will be switched with checkboxes. Note that all base layers should be passed in the base layers object, but only one should be added to the map during map instantiation.
export const controlLayers = function (mapGl, baseLayers, overlays) {
    return new ControlLayers(mapGl, baseLayers, overlays)
}
