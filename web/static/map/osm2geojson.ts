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
  const result: Record<number, NodeObject> = {}

  const nodes = xml.getElementsByTagName('node')
  for (const i = 0; i < nodes.length; i++) {
    const node = nodes[i],
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
  const result: WayObject[] = []

  const ways = xml.getElementsByTagName('way')
  for (const i = 0; i < ways.length; i++) {
    const way = ways[i],
      nds = [...way.getElementsByTagName('nd')]
    const way_object: WayObject = {
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
  const result: RelationObject[] = []

  const rels = xml.getElementsByTagName('relation')
  for (const i = 0; i < rels.length; i++) {
    const rel = rels[i],
      members = [...rel.getElementsByTagName('member')]
    const rel_object: RelationObject = {
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
  const result: Record<string, string> = {}

  const tags = xml.getElementsByTagName('tag')
  if (tags) {
    for (const j = 0; j < tags.length; j++) {
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
        const geom: GeoJSON.Feature | undefined = undefined

        if (feature.type === 'node') {
          geom = {
            type: 'Feature',
            properties: { index },
            geometry: { type: 'Point', coordinates: feature.lngLat },
          }
        } else if (feature.type === 'way') {
          const lngLats = new Array(feature.nodes.length)

          for (const j = 0; j < feature.nodes.length; j++) {
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
  const features: OsmObject[] = [],
    nodes = getNodes(xml),
    ways = getWays(xml, nodes),
    relations = getRelations(xml, nodes, ways)

  for (const node_id in nodes) {
    const node = nodes[node_id]
    if (interestingNode(node, ways, relations)) {
      features.push(node)
    }
  }

  for (const i = 0; i < ways.length; i++) {
    const way = ways[i]
    features.push(way)
  }

  return features
}

function isWayArea(way: WayObject): boolean {
  if (way.nodes[0] != way.nodes[way.nodes.length - 1]) {
    return false
  }

  for (const key in way.tags) {
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
  const used = false

  for (const i = 0; i < ways.length; i++) {
    if (ways[i].nodes.indexOf(node) >= 0) {
      used = true
      break
    }
  }

  if (!used) {
    return true
  }

  for (const i = 0; i < relations.length; i++) {
    if (relations[i].members.indexOf(node) >= 0) return true
  }

  for (const key in node.tags) {
    if (options.uninterestingTags.indexOf(key) < 0) {
      return true
    }
  }

  return false
}
