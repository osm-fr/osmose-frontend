// Based on https://github.com/openstreetmap/leaflet-osm
// BSD

declare type OsmObjectBase = {
  id: number
  tags: Record<string, string>
}

declare type NodeObject = OsmObjectBase & {
  type: 'node'
  lngLat: [number, number]
}

declare type WayObject = OsmObjectBase & {
  type: 'way'
  nodes: NodeObject[]
}

declare type RelationObject = OsmObjectBase & {
  type: 'relation'
  members: (NodeObject | null)[]
}

declare type OsmObject = NodeObject | WayObject | RelationObject

function getNodes(xml: Document): Record<number, NodeObject> {
  var result: Record<number, NodeObject> = {}

  var nodes = xml.getElementsByTagName('node')
  for (var i = 0; i < nodes.length; i++) {
    var node = nodes[i],
      id = node.getAttribute('id')
    if (node && id) {
      result[id] = {
        id: id,
        type: 'node',
        lngLat: [
          parseFloat(node.getAttribute('lon')!),
          parseFloat(node.getAttribute('lat')!),
        ],
        tags: getTags(node),
      }
    }
  }

  return result
}

function getWays(
  xml: Document,
  nodes: Record<number, NodeObject>
): WayObject[] {
  var result: WayObject[] = []

  var ways = xml.getElementsByTagName('way')
  for (var i = 0; i < ways.length; i++) {
    var way = ways[i],
      nds = [...way.getElementsByTagName('nd')]
    var way_object: WayObject = {
      id: way.getAttribute('id') as unknown as number,
      type: 'way',
      nodes: nds.map(
        (nd) => nodes[nd.getAttribute('ref') as unknown as number]
      ),
      tags: getTags(way),
    }

    result.push(way_object)
  }

  return result
}

function getRelations(
  xml: Document,
  nodes: Record<number, NodeObject>,
  ways: WayObject[]
): RelationObject[] {
  var result: RelationObject[] = []

  var rels = xml.getElementsByTagName('relation')
  for (var i = 0; i < rels.length; i++) {
    var rel = rels[i],
      members = [...rel.getElementsByTagName('member')]
    var rel_object: RelationObject = {
      id: rel.getAttribute('id') as unknown as number,
      type: 'relation',
      members: members.map((member) =>
        member.getAttribute('type') === 'node'
          ? nodes[member.getAttribute('ref') as unknown as number]
          : null
      ),
      tags: getTags(rel),
    }

    result.push(rel_object)
  }

  return result
}

function getTags(xml: Element): Record<string, string> {
  var result: Record<string, string> = {}

  var tags = xml.getElementsByTagName('tag')
  if (tags) {
    for (var j = 0; j < tags.length; j++) {
      const k = tags[j].getAttribute('k')
      const v = tags[j].getAttribute('v')
      if (k !== null && v !== null) {
        result[k] = v
      }
    }
  }

  return result
}

const options = {
  areaTags: [
    'area',
    'building',
    'leisure',
    'tourism',
    'ruins',
    'historic',
    'landuse',
    'military',
    'natural',
    'sport',
  ],
  uninterestingTags: [
    'source',
    'source_ref',
    'source:ref',
    'history',
    'attribution',
    'created_by',
    'tiger:county',
    'tiger:tlid',
    'tiger:upload_uuid',
  ],
} as {
  areaTags: string[]
  uninterestingTags: string[]
}

export default function osm2geojson(xml: Document): GeoJSON.FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: buildFeatures(xml)
      .map((feature, index) => {
        var geom: GeoJSON.Feature | undefined = undefined

        if (feature.type === 'node') {
          geom = {
            type: 'Feature',
            properties: { index },
            geometry: { type: 'Point', coordinates: feature.lngLat },
          }
        } else if (feature.type === 'way') {
          var lngLats = new Array(feature.nodes.length)

          for (var j = 0; j < feature.nodes.length; j++) {
            lngLats[j] = feature.nodes[j].lngLat
          }

          if (isWayArea(feature)) {
            geom = {
              type: 'Feature',
              properties: { index },
              geometry: { type: 'Polygon', coordinates: [lngLats] },
            }
          } else {
            geom = {
              type: 'Feature',
              properties: { index },
              geometry: { type: 'LineString', coordinates: lngLats },
            }
          }
        }

        return geom
      })
      .filter((geom) => !!geom),
  }
}

function buildFeatures(xml: Document): OsmObject[] {
  var features: OsmObject[] = [],
    nodes = getNodes(xml),
    ways = getWays(xml, nodes),
    relations = getRelations(xml, nodes, ways)

  for (var node_id in nodes) {
    var node = nodes[node_id]
    if (interestingNode(node, ways, relations)) {
      features.push(node)
    }
  }

  for (var i = 0; i < ways.length; i++) {
    var way = ways[i]
    features.push(way)
  }

  return features
}

function isWayArea(way: WayObject): boolean {
  if (way.nodes[0] != way.nodes[way.nodes.length - 1]) {
    return false
  }

  for (var key in way.tags) {
    if (~options.areaTags.indexOf(key)) {
      return true
    }
  }

  return false
}

function interestingNode(
  node: NodeObject,
  ways: WayObject[],
  relations: RelationObject[]
): boolean {
  var used = false

  for (var i = 0; i < ways.length; i++) {
    if (ways[i].nodes.indexOf(node) >= 0) {
      used = true
      break
    }
  }

  if (!used) {
    return true
  }

  for (var i = 0; i < relations.length; i++) {
    if (relations[i].members.indexOf(node) >= 0) return true
  }

  for (var key in node.tags) {
    if (options.uninterestingTags.indexOf(key) < 0) {
      return true
    }
  }

  return false
}
