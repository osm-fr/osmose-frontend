// Based on https://github.com/openstreetmap/leaflet-osm
// BSD

import { LayerOptions } from 'leaflet'

declare type OsmObjectBase = {
  id: number
  tags: Record<string, string>
}

declare type NodeObject = OsmObjectBase & {
  type: "node"
  latLng: any
}

declare type WayObject = OsmObjectBase & {
  type: "way"
  nodes: NodeObject[]
}

declare type RelationObject = OsmObjectBase & {
  type: "relation"
  members: (NodeObject | null)[]
}

declare type OsmObject = NodeObject | WayObject | RelationObject


function getNodes(xml: Document): Record<number, NodeObject> {
  var result: Record<number, NodeObject> = {}

  var nodes = xml.getElementsByTagName("node")
  for (var i = 0; i < nodes.length; i++) {
    var node = nodes[i], id = node.getAttribute("id")
    if (node && id) {
      result[id] = {
        id: id,
        type: "node",
        latLng: L.latLng(
          node.getAttribute("lat") as unknown as number,
          node.getAttribute("lon") as unknown as number
        ),
        tags: getTags(node)
      }
    }
  }

  return result
}

function getWays(xml: Document, nodes: Record<number, NodeObject>): WayObject[] {
  var result: WayObject[] = []

  var ways = xml.getElementsByTagName("way")
  for (var i = 0; i < ways.length; i++) {
    var way = ways[i], nds = [...way.getElementsByTagName("nd")]
    var way_object: WayObject = {
      id: way.getAttribute("id") as unknown as number,
      type: "way",
      nodes: nds.map((nd) => nodes[nd.getAttribute("ref") as unknown as number]),
      tags: getTags(way)
    }

    result.push(way_object)
  }

  return result
}

function getRelations(xml: Document, nodes: Record<number, NodeObject>, ways: WayObject[]): RelationObject[] {
  var result: RelationObject[] = []

  var rels = xml.getElementsByTagName("relation")
  for (var i = 0; i < rels.length; i++) {
    var rel = rels[i], members = [...rel.getElementsByTagName("member")]
    var rel_object: RelationObject = {
      id: rel.getAttribute("id") as unknown as number,
      type: "relation",
      members: members.map((member) => (
        member.getAttribute("type") === "node" ?
          nodes[member.getAttribute("ref") as unknown as number] :
          null)
      ),
      tags: getTags(rel)
    }

    result.push(rel_object)
  }

  return result
}

function getTags(xml: Element): Record<string, string> {
  var result: Record<string, string> = {}

  var tags = xml.getElementsByTagName("tag")
  if (tags) {
    for (var j = 0; j < tags.length; j++) {
      const k = tags[j].getAttribute("k")
      const v = tags[j].getAttribute("v")
      if (k !== null && v !== null) {
        result[k] = v
      }
    }
  }

  return result
}


export default class OsmDataLayer extends L.FeatureGroup {
  options = {
    areaTags: ['area', 'building', 'leisure', 'tourism', 'ruins', 'historic', 'landuse', 'military', 'natural', 'sport'],
    uninterestingTags: ['source', 'source_ref', 'source:ref', 'history', 'attribution', 'created_by', 'tiger:county', 'tiger:tlid', 'tiger:upload_uuid'],
    styles: {}
  } as {
    areaTags: string[]
    uninterestingTags: string[]
    styles: Object
  }

  constructor(xml: Document, options?: LayerOptions) {
    super([], options)
    L.Util.setOptions(this, options)
    this.addData(this.buildFeatures(xml))
  }

  addData(features: OsmObject[]): void {
    for (var i = 0; i < features.length; i++) {
      var feature = features[i], layer

      if (feature.type === "node") {
        layer = L.circleMarker(feature.latLng, this.options.styles.node)
      } else if (feature.type === "way") {
        var latLngs = new Array(feature.nodes.length)

        for (var j = 0; j < feature.nodes.length; j++) {
          latLngs[j] = feature.nodes[j].latLng
        }

        if (this.isWayArea(feature)) {
          latLngs.pop(); // Remove last == first.
          layer = L.polygon(latLngs, this.options.styles.area)
        } else {
          layer = L.polyline(latLngs, this.options.styles.way)
        }
      }

      layer.addTo(this)
      layer.feature = feature
    }
  }

  buildFeatures(xml: Document): OsmObject[] {
    var features: OsmObject[] = [],
      nodes = getNodes(xml),
      ways = getWays(xml, nodes),
      relations = getRelations(xml, nodes, ways)

    for (var node_id in nodes) {
      var node = nodes[node_id]
      if (this.interestingNode(node, ways, relations)) {
        features.push(node)
      }
    }

    for (var i = 0; i < ways.length; i++) {
      var way = ways[i]
      features.push(way)
    }

    return features
  }

  isWayArea(way: WayObject): boolean {
    if (way.nodes[0] != way.nodes[way.nodes.length - 1]) {
      return false
    }

    for (var key in way.tags) {
      if (~this.options.areaTags.indexOf(key)) {
        return true
      }
    }

    return false
  }

  interestingNode(node: NodeObject, ways: WayObject[], relations: RelationObject[]): boolean {
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
      if (relations[i].members.indexOf(node) >= 0)
        return true
    }

    for (var key in node.tags) {
      if (this.options.uninterestingTags.indexOf(key) < 0) {
        return true
      }
    }

    return false
  }
}
