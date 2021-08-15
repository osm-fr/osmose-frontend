import 'leaflet';


const OsmoseEditor = L.Control.Sidebar.extend({
  options: {
    closeButton: false,
    autoPan: false,
  },
});


export { OsmoseEditor as default };
