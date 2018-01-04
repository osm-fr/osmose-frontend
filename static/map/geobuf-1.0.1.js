!function(e){if("object"==typeof exports&&"undefined"!=typeof module)module.exports=e();else if("function"==typeof define&&define.amd)define([],e);else{var f;"undefined"!=typeof window?f=window:"undefined"!=typeof global?f=global:"undefined"!=typeof self&&(f=self),f.geobuf=e()}}(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

module.exports = decode;

var keys, values, lengths, dim, e, isTopo, transformed, names;

var geometryTypes = ['Point', 'MultiPoint', 'LineString', 'MultiLineString',
                      'Polygon', 'MultiPolygon', 'GeometryCollection'];

function decode(pbf) {
    dim = 2;
    e = Math.pow(10, 6);
    isTopo = false;
    transformed = false;
    lengths = null;

    keys = [];
    values = [];
    var obj = pbf.readFields(readDataField, {});
    keys = null;

    return obj;
}

function readDataField(tag, obj, pbf) {
    if (tag === 1) keys.push(pbf.readString());
    else if (tag === 2) dim = pbf.readVarint();
    else if (tag === 3) e = Math.pow(10, pbf.readVarint());

    else if (tag === 4) readFeatureCollection(pbf, obj);
    else if (tag === 5) readFeature(pbf, obj);
    else if (tag === 6) readGeometry(pbf, obj);
    else if (tag === 7) readTopology(pbf, obj);
}

function readFeatureCollection(pbf, obj) {
    obj.type = 'FeatureCollection';
    obj.features = [];
    return pbf.readMessage(readFeatureCollectionField, obj);
}

function readFeature(pbf, feature) {
    feature.type = 'Feature';
    return pbf.readMessage(readFeatureField, feature);
}

function readGeometry(pbf, geom) {
    return pbf.readMessage(readGeometryField, geom);
}

function readTopology(pbf, topology) {
    isTopo = true;
    topology.type = 'Topology';
    topology.objects = {};
    names = [];
    pbf.readMessage(readTopologyField, topology);
    names = null;
    return topology;
}

function readTopologyField(tag, topology, pbf) {
    if (tag === 1) {
        topology.transform = pbf.readMessage(readTransformField, {scale: [], translate: []});
        transformed = true;
    }
    else if (tag === 2) names.push(pbf.readString());
    else if (tag === 3) topology.objects[names.shift()] = pbf.readMessage(readGeometryField, {});

    else if (tag === 4) lengths = pbf.readPackedVarint();
    else if (tag === 5) topology.arcs = readArcs(pbf);

    else if (tag === 13) values.push(readValue(pbf));
    else if (tag === 15) readProps(pbf, topology);
}

function readFeatureCollectionField(tag, obj, pbf) {
    if (tag === 1) obj.features.push(readFeature(pbf, {}));

    else if (tag === 13) values.push(readValue(pbf));
    else if (tag === 15) readProps(pbf, obj);
}

function readFeatureField(tag, feature, pbf) {
    if (tag === 1) feature.geometry = readGeometry(pbf, {});

    else if (tag === 11) feature.id = pbf.readString();
    else if (tag === 12) feature.id = pbf.readSVarint();

    else if (tag === 13) values.push(readValue(pbf));
    else if (tag === 14) feature.properties = readProps(pbf, {});
    else if (tag === 15) readProps(pbf, feature);
}

function readGeometryField(tag, geom, pbf) {
    if (tag === 1) geom.type = geometryTypes[pbf.readVarint()];

    else if (tag === 2) lengths = pbf.readPackedVarint();
    else if (tag === 3) readCoords(geom, pbf, geom.type);
    else if (tag === 4) {
        geom.geometries = geom.geometries || [];
        geom.geometries.push(readGeometry(pbf, {}));
    }

    else if (tag === 11) geom.id = pbf.readString();
    else if (tag === 12) geom.id = pbf.readSVarint();

    else if (tag === 13) values.push(readValue(pbf));
    else if (tag === 14) geom.properties = readProps(pbf, {});
    else if (tag === 15) readProps(pbf, geom);
}

function readCoords(geom, pbf, type) {
    var coordsOrArcs = isTopo ? 'arcs' : 'coordinates';
    if (type === 'Point') geom.coordinates = readPoint(pbf);
    else if (type === 'MultiPoint') geom.coordinates = readLine(pbf, true);
    else if (type === 'LineString') geom[coordsOrArcs] = readLine(pbf);
    else if (type === 'MultiLineString' || type === 'Polygon') geom[coordsOrArcs] = readMultiLine(pbf);
    else if (type === 'MultiPolygon') geom[coordsOrArcs] = readMultiPolygon(pbf);
}

function readValue(pbf) {
    var end = pbf.readVarint() + pbf.pos,
        value = null;

    while (pbf.pos < end) {
        var val = pbf.readVarint(),
            tag = val >> 3;

        if (tag === 1) value = pbf.readString();
        else if (tag === 2) value = pbf.readDouble();
        else if (tag === 3) value = pbf.readVarint();
        else if (tag === 4) value = -pbf.readVarint();
        else if (tag === 5) value = pbf.readBoolean();
        else if (tag === 6) value = JSON.parse(pbf.readString());
    }
    return value;
}

function readProps(pbf, props) {
    var end = pbf.readVarint() + pbf.pos;
    while (pbf.pos < end) props[keys[pbf.readVarint()]] = values[pbf.readVarint()];
    values = [];
    return props;
}

function readTransformField(tag, tr, pbf) {
    if (tag === 1) tr.scale[0] = pbf.readDouble();
    else if (tag === 2) tr.scale[1] = pbf.readDouble();
    else if (tag === 3) tr.translate[0] = pbf.readDouble();
    else if (tag === 4) tr.translate[1] = pbf.readDouble();
}

function readPoint(pbf) {
    var end = pbf.readVarint() + pbf.pos,
        coords = [];
    while (pbf.pos < end) coords.push(transformCoord(pbf.readSVarint()));
    return coords;
}

function readLinePart(pbf, end, len, isMultiPoint) {
    var i = 0,
        coords = [],
        p, d;

    if (isTopo && !isMultiPoint) {
        p = 0;
        while (len ? i < len : pbf.pos < end) {
            p += pbf.readSVarint();
            coords.push(p);
            i++;
        }

    } else {
        var prevP = [];
        for (d = 0; d < dim; d++) prevP[d] = 0;

        while (len ? i < len : pbf.pos < end) {
            p = [];
            for (d = 0; d < dim; d++) {
                prevP[d] += pbf.readSVarint();
                p[d] = transformCoord(prevP[d]);
            }
            coords.push(p);
            i++;
        }
    }

    return coords;
}

function readLine(pbf, isMultiPoint) {
    return readLinePart(pbf, pbf.readVarint() + pbf.pos, null, isMultiPoint);
}

function readMultiLine(pbf) {
    var end = pbf.readVarint() + pbf.pos;
    if (!lengths) return [readLinePart(pbf, end)];

    var coords = [];
    for (var i = 0; i < lengths.length; i++) coords.push(readLinePart(pbf, end, lengths[i]));
    lengths = null;
    return coords;
}

function readMultiPolygon(pbf) {
    var end = pbf.readVarint() + pbf.pos;
    if (!lengths) return [[readLinePart(pbf, end)]];

    var coords = [];
    var j = 1;
    for (var i = 0; i < lengths[0]; i++) {
        var rings = [];
        for (var k = 0; k < lengths[j]; k++) rings.push(readLinePart(pbf, end, lengths[j + 1 + k]));
        j += lengths[j] + 1;
        coords.push(rings);
    }
    lengths = null;
    return coords;
}

function readArcs(pbf) {
    var lines = [],
        end = pbf.readVarint() + pbf.pos;

    for (var i = 0; i < lengths.length; i++) {
        var ring = [];
        for (var j = 0; j < lengths[i]; j++) {
            var p = [];
            for (var d = 0; d < dim && pbf.pos < end; d++) p[d] = transformCoord(pbf.readSVarint());
            ring.push(p);
        }
        lines.push(ring);
    }

    return lines;
}

function transformCoord(x) {
    return transformed ? x : x / e;
}

},{}],2:[function(require,module,exports){
'use strict';

module.exports = encode;

var keys, keysNum, dim, e, isTopo, transformed,
    maxPrecision = 1e6;

var geometryTypes = {
    'Point': 0,
    'MultiPoint': 1,
    'LineString': 2,
    'MultiLineString': 3,
    'Polygon': 4,
    'MultiPolygon': 5,
    'GeometryCollection': 6
};

function encode(obj, pbf) {
    keys = {};
    keysNum = 0;
    dim = 0;
    e = 1;
    transformed = false;
    isTopo = false;

    analyze(obj);

    e = Math.min(e, maxPrecision);
    var precision = Math.ceil(Math.log(e) / Math.LN10);

    var keysArr = Object.keys(keys);

    for (var i = 0; i < keysArr.length; i++) pbf.writeStringField(1, keysArr[i]);
    if (dim !== 2) pbf.writeVarintField(2, dim);
    if (precision !== 6) pbf.writeVarintField(3, precision);

    if (obj.type === 'FeatureCollection') pbf.writeMessage(4, writeFeatureCollection, obj);
    else if (obj.type === 'Feature') pbf.writeMessage(5, writeFeature, obj);
    else if (obj.type === 'Topology') pbf.writeMessage(7, writeTopology, obj);
    else pbf.writeMessage(6, writeGeometry, obj);

    keys = null;

    return pbf.finish();
}

function analyze(obj) {
    var i, key;

    if (obj.type === 'FeatureCollection') {
        for (i = 0; i < obj.features.length; i++) analyze(obj.features[i]);
        for (key in obj) if (key !== 'type' && key !== 'features') saveKey(key);

    } else if (obj.type === 'Feature') {
        analyze(obj.geometry);
        for (key in obj.properties) saveKey(key);
        for (key in obj) {
            if (key !== 'type' && key !== 'id' && key !== 'properties' && key !== 'geometry') saveKey(key);
        }

    } else if (obj.type === 'Topology') {
        isTopo = true;

        for (key in obj) {
            if (key !== 'type' && key !== 'transform' && key !== 'arcs' && key !== 'objects') saveKey(key);
        }
        analyzeMultiLine(obj.arcs);

        for (key in obj.objects) {
            analyze(obj.objects[key]);
        }

    } else {
        if (obj.type === 'Point') analyzePoint(obj.coordinates);
        else if (obj.type === 'MultiPoint') analyzePoints(obj.coordinates);
        else if (obj.type === 'GeometryCollection') {
            for (i = 0; i < obj.geometries.length; i++) analyze(obj.geometries[i]);
        }
        else if (!isTopo) {
            if (obj.type === 'LineString') analyzePoints(obj.coordinates);
            else if (obj.type === 'Polygon' || obj.type === 'MultiLineString') analyzeMultiLine(obj.coordinates);
            else if (obj.type === 'MultiPolygon') {
                for (i = 0; i < obj.coordinates.length; i++) analyzeMultiLine(obj.coordinates[i]);
            }
        }

        for (key in obj.properties) saveKey(key);
        for (key in obj) {
            if (key !== 'type' && key !== 'id' && key !== 'coordinates' && key !== 'arcs' &&
                key !== 'geometries' && key !== 'properties') saveKey(key);
        }
    }
}

function analyzeMultiLine(coords) {
    for (var i = 0; i < coords.length; i++) analyzePoints(coords[i]);
}

function analyzePoints(coords) {
    for (var i = 0; i < coords.length; i++) analyzePoint(coords[i]);
}

function analyzePoint(point) {
    dim = Math.max(dim, point.length);

    // find max precision
    for (var i = 0; i < point.length; i++) {
        while (Math.round(point[i] * e) / e !== point[i] && e < maxPrecision) e *= 10;
    }
}

function saveKey(key) {
    if (keys[key] === undefined) keys[key] = keysNum++;
}

function writeFeatureCollection(obj, pbf) {
    for (var i = 0; i < obj.features.length; i++) {
        pbf.writeMessage(1, writeFeature, obj.features[i]);
    }
    writeProps(obj, pbf, true);
}

function writeFeature(feature, pbf) {
    pbf.writeMessage(1, writeGeometry, feature.geometry);

    if (feature.id !== undefined) {
        if (typeof feature.id === 'number' && feature.id % 1 === 0) pbf.writeSVarintField(12, feature.id);
        else pbf.writeStringField(11, feature.id);
    }

    if (feature.properties) writeProps(feature.properties, pbf);
    writeProps(feature, pbf, true);
}

function writeGeometry(geom, pbf) {
    pbf.writeVarintField(1, geometryTypes[geom.type]);

    var coords = geom.coordinates,
        coordsOrArcs = isTopo ? geom.arcs : coords;

    if (geom.type === 'Point') writePoint(coords, pbf);
    else if (geom.type === 'MultiPoint') writeLine(coords, pbf, true);
    else if (geom.type === 'LineString') writeLine(coordsOrArcs, pbf);
    if (geom.type === 'MultiLineString' || geom.type === 'Polygon') writeMultiLine(coordsOrArcs, pbf);
    else if (geom.type === 'MultiPolygon') writeMultiPolygon(coordsOrArcs, pbf);
    else if (geom.type === 'GeometryCollection') {
        for (var i = 0; i < geom.geometries.length; i++) pbf.writeMessage(4, writeGeometry, geom.geometries[i]);
    }

    if (isTopo && geom.id !== undefined) {
        if (typeof geom.id === 'number' && geom.id % 1 === 0) pbf.writeSVarintField(12, geom.id);
        else pbf.writeStringField(11, geom.id);
    }

    if (isTopo && geom.properties) writeProps(geom.properties, pbf);
    writeProps(geom, pbf, true);
}

function writeTopology(topology, pbf) {
    if (topology.transform) {
        pbf.writeMessage(1, writeTransform, topology.transform);
        transformed = true;
    }

    var names = Object.keys(topology.objects),
        i, j, d;

    for (i = 0; i < names.length; i++) pbf.writeStringField(2, names[i]);
    for (i = 0; i < names.length; i++) {
        pbf.writeMessage(3, writeGeometry, topology.objects[names[i]]);
    }

    var lengths = [],
        coords = [];

    for (i = 0; i < topology.arcs.length; i++) {
        var arc = topology.arcs[i];
        lengths.push(arc.length);

        for (j = 0; j < arc.length; j++) {
            for (d = 0; d < dim; d++) coords.push(transformCoord(arc[j][d]));
        }
    }

    pbf.writePackedVarint(4, lengths);
    pbf.writePackedSVarint(5, coords);

    writeProps(topology, pbf, true);
}

function writeProps(props, pbf, isCustom) {
    var indexes = [],
        valueIndex = 0;

    for (var key in props) {
        if (isCustom) {
            if (key === 'type') continue;
            else if (props.type === 'FeatureCollection') {
                if (key === 'features') continue;
            } else if (props.type === 'Feature') {
                if (key === 'id' || key === 'properties' || key === 'geometry') continue;
            } else if (props.type === 'Topology')  {
                if (key === 'transform' || key === 'arcs' || key === 'objects') continue;
            } else if (key === 'id' || key === 'coordinates' || key === 'arcs' ||
                       key === 'geometries' || key === 'properties') continue;
        }
        pbf.writeMessage(13, writeValue, props[key]);
        indexes.push(keys[key], valueIndex++);
    }
    pbf.writePackedVarint(isCustom ? 15 : 14, indexes);
}

function writeValue(value, pbf) {
    var type = typeof value;

    if (type === 'string') pbf.writeStringField(1, value);
    else if (type === 'boolean') pbf.writeBooleanField(5, value);
    else if (type === 'object') pbf.writeStringField(6, JSON.stringify(value));
    else if (type === 'number') {
       if (value % 1 !== 0) pbf.writeDoubleField(2, value);
       else if (value >= 0) pbf.writeVarintField(3, value);
       else pbf.writeVarintField(4, -value);
    }
}

function writePoint(point, pbf) {
    var coords = [];
    for (var i = 0; i < dim; i++) coords.push(transformCoord(point[i]));
    pbf.writePackedSVarint(3, coords);
}

function writeLine(line, pbf, isMultiPoint) {
    var coords = [];
    populateLine(coords, line, isMultiPoint);
    pbf.writePackedSVarint(3, coords);
}

function writeMultiLine(lines, pbf) {
    var len = lines.length,
        i;
    if (len !== 1) {
        var lengths = [];
        for (i = 0; i < len; i++) lengths.push(lines[i].length);
        pbf.writePackedVarint(2, lengths);
        // TODO faster with custom writeMessage?
    }
    var coords = [];
    for (i = 0; i < len; i++) populateLine(coords, lines[i]);
    pbf.writePackedSVarint(3, coords);
}

function writeMultiPolygon(polygons, pbf) {
    var len = polygons.length,
        i, j;
    if (len !== 1 || polygons[0].length !== 1 || polygons[0][0].length !== 1) {
        var lengths = [len];
        for (i = 0; i < len; i++) {
            lengths.push(polygons[i].length);
            for (j = 0; j < polygons[i].length; j++) lengths.push(polygons[i][j].length);
        }
        pbf.writePackedVarint(2, lengths);
    }

    var coords = [];
    for (i = 0; i < len; i++) {
        for (j = 0; j < polygons[i].length; j++) populateLine(coords, polygons[i][j]);
    }
    pbf.writePackedSVarint(3, coords);
}

function populateLine(coords, line, isMultiPoint) {
    var i, j;
    for (i = 0; i < line.length; i++) {
        if (isTopo && !isMultiPoint) coords.push(i ? line[i] - line[i - 1] : line[i]);
        else for (j = 0; j < dim; j++) coords.push(transformCoord(line[i][j] - (i ? line[i - 1][j] : 0)));
    }
}

function transformCoord(x) {
    return transformed ? x : Math.round(x * e);
}

function writeTransform(tr, pbf) {
    pbf.writeDoubleField(1, tr.scale[0]);
    pbf.writeDoubleField(2, tr.scale[1]);
    pbf.writeDoubleField(3, tr.translate[0]);
    pbf.writeDoubleField(4, tr.translate[1]);
}

},{}],3:[function(require,module,exports){
'use strict';

exports.encode = require('./encode');
exports.decode = require('./decode');

},{"./decode":1,"./encode":2}]},{},[3])(3)
});
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJkZWNvZGUuanMiLCJlbmNvZGUuanMiLCJpbmRleC5qcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtBQ0FBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ2hQQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNoU0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIndXNlIHN0cmljdCc7XG5cbm1vZHVsZS5leHBvcnRzID0gZGVjb2RlO1xuXG52YXIga2V5cywgdmFsdWVzLCBsZW5ndGhzLCBkaW0sIGUsIGlzVG9wbywgdHJhbnNmb3JtZWQsIG5hbWVzO1xuXG52YXIgZ2VvbWV0cnlUeXBlcyA9IFsnUG9pbnQnLCAnTXVsdGlQb2ludCcsICdMaW5lU3RyaW5nJywgJ011bHRpTGluZVN0cmluZycsXG4gICAgICAgICAgICAgICAgICAgICAgJ1BvbHlnb24nLCAnTXVsdGlQb2x5Z29uJywgJ0dlb21ldHJ5Q29sbGVjdGlvbiddO1xuXG5mdW5jdGlvbiBkZWNvZGUocGJmKSB7XG4gICAgZGltID0gMjtcbiAgICBlID0gTWF0aC5wb3coMTAsIDYpO1xuICAgIGlzVG9wbyA9IGZhbHNlO1xuICAgIHRyYW5zZm9ybWVkID0gZmFsc2U7XG4gICAgbGVuZ3RocyA9IG51bGw7XG5cbiAgICBrZXlzID0gW107XG4gICAgdmFsdWVzID0gW107XG4gICAgdmFyIG9iaiA9IHBiZi5yZWFkRmllbGRzKHJlYWREYXRhRmllbGQsIHt9KTtcbiAgICBrZXlzID0gbnVsbDtcblxuICAgIHJldHVybiBvYmo7XG59XG5cbmZ1bmN0aW9uIHJlYWREYXRhRmllbGQodGFnLCBvYmosIHBiZikge1xuICAgIGlmICh0YWcgPT09IDEpIGtleXMucHVzaChwYmYucmVhZFN0cmluZygpKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDIpIGRpbSA9IHBiZi5yZWFkVmFyaW50KCk7XG4gICAgZWxzZSBpZiAodGFnID09PSAzKSBlID0gTWF0aC5wb3coMTAsIHBiZi5yZWFkVmFyaW50KCkpO1xuXG4gICAgZWxzZSBpZiAodGFnID09PSA0KSByZWFkRmVhdHVyZUNvbGxlY3Rpb24ocGJmLCBvYmopO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gNSkgcmVhZEZlYXR1cmUocGJmLCBvYmopO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gNikgcmVhZEdlb21ldHJ5KHBiZiwgb2JqKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDcpIHJlYWRUb3BvbG9neShwYmYsIG9iaik7XG59XG5cbmZ1bmN0aW9uIHJlYWRGZWF0dXJlQ29sbGVjdGlvbihwYmYsIG9iaikge1xuICAgIG9iai50eXBlID0gJ0ZlYXR1cmVDb2xsZWN0aW9uJztcbiAgICBvYmouZmVhdHVyZXMgPSBbXTtcbiAgICByZXR1cm4gcGJmLnJlYWRNZXNzYWdlKHJlYWRGZWF0dXJlQ29sbGVjdGlvbkZpZWxkLCBvYmopO1xufVxuXG5mdW5jdGlvbiByZWFkRmVhdHVyZShwYmYsIGZlYXR1cmUpIHtcbiAgICBmZWF0dXJlLnR5cGUgPSAnRmVhdHVyZSc7XG4gICAgcmV0dXJuIHBiZi5yZWFkTWVzc2FnZShyZWFkRmVhdHVyZUZpZWxkLCBmZWF0dXJlKTtcbn1cblxuZnVuY3Rpb24gcmVhZEdlb21ldHJ5KHBiZiwgZ2VvbSkge1xuICAgIHJldHVybiBwYmYucmVhZE1lc3NhZ2UocmVhZEdlb21ldHJ5RmllbGQsIGdlb20pO1xufVxuXG5mdW5jdGlvbiByZWFkVG9wb2xvZ3kocGJmLCB0b3BvbG9neSkge1xuICAgIGlzVG9wbyA9IHRydWU7XG4gICAgdG9wb2xvZ3kudHlwZSA9ICdUb3BvbG9neSc7XG4gICAgdG9wb2xvZ3kub2JqZWN0cyA9IHt9O1xuICAgIG5hbWVzID0gW107XG4gICAgcGJmLnJlYWRNZXNzYWdlKHJlYWRUb3BvbG9neUZpZWxkLCB0b3BvbG9neSk7XG4gICAgbmFtZXMgPSBudWxsO1xuICAgIHJldHVybiB0b3BvbG9neTtcbn1cblxuZnVuY3Rpb24gcmVhZFRvcG9sb2d5RmllbGQodGFnLCB0b3BvbG9neSwgcGJmKSB7XG4gICAgaWYgKHRhZyA9PT0gMSkge1xuICAgICAgICB0b3BvbG9neS50cmFuc2Zvcm0gPSBwYmYucmVhZE1lc3NhZ2UocmVhZFRyYW5zZm9ybUZpZWxkLCB7c2NhbGU6IFtdLCB0cmFuc2xhdGU6IFtdfSk7XG4gICAgICAgIHRyYW5zZm9ybWVkID0gdHJ1ZTtcbiAgICB9XG4gICAgZWxzZSBpZiAodGFnID09PSAyKSBuYW1lcy5wdXNoKHBiZi5yZWFkU3RyaW5nKCkpO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gMykgdG9wb2xvZ3kub2JqZWN0c1tuYW1lcy5zaGlmdCgpXSA9IHBiZi5yZWFkTWVzc2FnZShyZWFkR2VvbWV0cnlGaWVsZCwge30pO1xuXG4gICAgZWxzZSBpZiAodGFnID09PSA0KSBsZW5ndGhzID0gcGJmLnJlYWRQYWNrZWRWYXJpbnQoKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDUpIHRvcG9sb2d5LmFyY3MgPSByZWFkQXJjcyhwYmYpO1xuXG4gICAgZWxzZSBpZiAodGFnID09PSAxMykgdmFsdWVzLnB1c2gocmVhZFZhbHVlKHBiZikpO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTUpIHJlYWRQcm9wcyhwYmYsIHRvcG9sb2d5KTtcbn1cblxuZnVuY3Rpb24gcmVhZEZlYXR1cmVDb2xsZWN0aW9uRmllbGQodGFnLCBvYmosIHBiZikge1xuICAgIGlmICh0YWcgPT09IDEpIG9iai5mZWF0dXJlcy5wdXNoKHJlYWRGZWF0dXJlKHBiZiwge30pKTtcblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTMpIHZhbHVlcy5wdXNoKHJlYWRWYWx1ZShwYmYpKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDE1KSByZWFkUHJvcHMocGJmLCBvYmopO1xufVxuXG5mdW5jdGlvbiByZWFkRmVhdHVyZUZpZWxkKHRhZywgZmVhdHVyZSwgcGJmKSB7XG4gICAgaWYgKHRhZyA9PT0gMSkgZmVhdHVyZS5nZW9tZXRyeSA9IHJlYWRHZW9tZXRyeShwYmYsIHt9KTtcblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTEpIGZlYXR1cmUuaWQgPSBwYmYucmVhZFN0cmluZygpO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTIpIGZlYXR1cmUuaWQgPSBwYmYucmVhZFNWYXJpbnQoKTtcblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTMpIHZhbHVlcy5wdXNoKHJlYWRWYWx1ZShwYmYpKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDE0KSBmZWF0dXJlLnByb3BlcnRpZXMgPSByZWFkUHJvcHMocGJmLCB7fSk7XG4gICAgZWxzZSBpZiAodGFnID09PSAxNSkgcmVhZFByb3BzKHBiZiwgZmVhdHVyZSk7XG59XG5cbmZ1bmN0aW9uIHJlYWRHZW9tZXRyeUZpZWxkKHRhZywgZ2VvbSwgcGJmKSB7XG4gICAgaWYgKHRhZyA9PT0gMSkgZ2VvbS50eXBlID0gZ2VvbWV0cnlUeXBlc1twYmYucmVhZFZhcmludCgpXTtcblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMikgbGVuZ3RocyA9IHBiZi5yZWFkUGFja2VkVmFyaW50KCk7XG4gICAgZWxzZSBpZiAodGFnID09PSAzKSByZWFkQ29vcmRzKGdlb20sIHBiZiwgZ2VvbS50eXBlKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDQpIHtcbiAgICAgICAgZ2VvbS5nZW9tZXRyaWVzID0gZ2VvbS5nZW9tZXRyaWVzIHx8IFtdO1xuICAgICAgICBnZW9tLmdlb21ldHJpZXMucHVzaChyZWFkR2VvbWV0cnkocGJmLCB7fSkpO1xuICAgIH1cblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTEpIGdlb20uaWQgPSBwYmYucmVhZFN0cmluZygpO1xuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTIpIGdlb20uaWQgPSBwYmYucmVhZFNWYXJpbnQoKTtcblxuICAgIGVsc2UgaWYgKHRhZyA9PT0gMTMpIHZhbHVlcy5wdXNoKHJlYWRWYWx1ZShwYmYpKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDE0KSBnZW9tLnByb3BlcnRpZXMgPSByZWFkUHJvcHMocGJmLCB7fSk7XG4gICAgZWxzZSBpZiAodGFnID09PSAxNSkgcmVhZFByb3BzKHBiZiwgZ2VvbSk7XG59XG5cbmZ1bmN0aW9uIHJlYWRDb29yZHMoZ2VvbSwgcGJmLCB0eXBlKSB7XG4gICAgdmFyIGNvb3Jkc09yQXJjcyA9IGlzVG9wbyA/ICdhcmNzJyA6ICdjb29yZGluYXRlcyc7XG4gICAgaWYgKHR5cGUgPT09ICdQb2ludCcpIGdlb20uY29vcmRpbmF0ZXMgPSByZWFkUG9pbnQocGJmKTtcbiAgICBlbHNlIGlmICh0eXBlID09PSAnTXVsdGlQb2ludCcpIGdlb20uY29vcmRpbmF0ZXMgPSByZWFkTGluZShwYmYsIHRydWUpO1xuICAgIGVsc2UgaWYgKHR5cGUgPT09ICdMaW5lU3RyaW5nJykgZ2VvbVtjb29yZHNPckFyY3NdID0gcmVhZExpbmUocGJmKTtcbiAgICBlbHNlIGlmICh0eXBlID09PSAnTXVsdGlMaW5lU3RyaW5nJyB8fCB0eXBlID09PSAnUG9seWdvbicpIGdlb21bY29vcmRzT3JBcmNzXSA9IHJlYWRNdWx0aUxpbmUocGJmKTtcbiAgICBlbHNlIGlmICh0eXBlID09PSAnTXVsdGlQb2x5Z29uJykgZ2VvbVtjb29yZHNPckFyY3NdID0gcmVhZE11bHRpUG9seWdvbihwYmYpO1xufVxuXG5mdW5jdGlvbiByZWFkVmFsdWUocGJmKSB7XG4gICAgdmFyIGVuZCA9IHBiZi5yZWFkVmFyaW50KCkgKyBwYmYucG9zLFxuICAgICAgICB2YWx1ZSA9IG51bGw7XG5cbiAgICB3aGlsZSAocGJmLnBvcyA8IGVuZCkge1xuICAgICAgICB2YXIgdmFsID0gcGJmLnJlYWRWYXJpbnQoKSxcbiAgICAgICAgICAgIHRhZyA9IHZhbCA+PiAzO1xuXG4gICAgICAgIGlmICh0YWcgPT09IDEpIHZhbHVlID0gcGJmLnJlYWRTdHJpbmcoKTtcbiAgICAgICAgZWxzZSBpZiAodGFnID09PSAyKSB2YWx1ZSA9IHBiZi5yZWFkRG91YmxlKCk7XG4gICAgICAgIGVsc2UgaWYgKHRhZyA9PT0gMykgdmFsdWUgPSBwYmYucmVhZFZhcmludCgpO1xuICAgICAgICBlbHNlIGlmICh0YWcgPT09IDQpIHZhbHVlID0gLXBiZi5yZWFkVmFyaW50KCk7XG4gICAgICAgIGVsc2UgaWYgKHRhZyA9PT0gNSkgdmFsdWUgPSBwYmYucmVhZEJvb2xlYW4oKTtcbiAgICAgICAgZWxzZSBpZiAodGFnID09PSA2KSB2YWx1ZSA9IEpTT04ucGFyc2UocGJmLnJlYWRTdHJpbmcoKSk7XG4gICAgfVxuICAgIHJldHVybiB2YWx1ZTtcbn1cblxuZnVuY3Rpb24gcmVhZFByb3BzKHBiZiwgcHJvcHMpIHtcbiAgICB2YXIgZW5kID0gcGJmLnJlYWRWYXJpbnQoKSArIHBiZi5wb3M7XG4gICAgd2hpbGUgKHBiZi5wb3MgPCBlbmQpIHByb3BzW2tleXNbcGJmLnJlYWRWYXJpbnQoKV1dID0gdmFsdWVzW3BiZi5yZWFkVmFyaW50KCldO1xuICAgIHZhbHVlcyA9IFtdO1xuICAgIHJldHVybiBwcm9wcztcbn1cblxuZnVuY3Rpb24gcmVhZFRyYW5zZm9ybUZpZWxkKHRhZywgdHIsIHBiZikge1xuICAgIGlmICh0YWcgPT09IDEpIHRyLnNjYWxlWzBdID0gcGJmLnJlYWREb3VibGUoKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDIpIHRyLnNjYWxlWzFdID0gcGJmLnJlYWREb3VibGUoKTtcbiAgICBlbHNlIGlmICh0YWcgPT09IDMpIHRyLnRyYW5zbGF0ZVswXSA9IHBiZi5yZWFkRG91YmxlKCk7XG4gICAgZWxzZSBpZiAodGFnID09PSA0KSB0ci50cmFuc2xhdGVbMV0gPSBwYmYucmVhZERvdWJsZSgpO1xufVxuXG5mdW5jdGlvbiByZWFkUG9pbnQocGJmKSB7XG4gICAgdmFyIGVuZCA9IHBiZi5yZWFkVmFyaW50KCkgKyBwYmYucG9zLFxuICAgICAgICBjb29yZHMgPSBbXTtcbiAgICB3aGlsZSAocGJmLnBvcyA8IGVuZCkgY29vcmRzLnB1c2godHJhbnNmb3JtQ29vcmQocGJmLnJlYWRTVmFyaW50KCkpKTtcbiAgICByZXR1cm4gY29vcmRzO1xufVxuXG5mdW5jdGlvbiByZWFkTGluZVBhcnQocGJmLCBlbmQsIGxlbiwgaXNNdWx0aVBvaW50KSB7XG4gICAgdmFyIGkgPSAwLFxuICAgICAgICBjb29yZHMgPSBbXSxcbiAgICAgICAgcCwgZDtcblxuICAgIGlmIChpc1RvcG8gJiYgIWlzTXVsdGlQb2ludCkge1xuICAgICAgICBwID0gMDtcbiAgICAgICAgd2hpbGUgKGxlbiA/IGkgPCBsZW4gOiBwYmYucG9zIDwgZW5kKSB7XG4gICAgICAgICAgICBwICs9IHBiZi5yZWFkU1ZhcmludCgpO1xuICAgICAgICAgICAgY29vcmRzLnB1c2gocCk7XG4gICAgICAgICAgICBpKys7XG4gICAgICAgIH1cblxuICAgIH0gZWxzZSB7XG4gICAgICAgIHZhciBwcmV2UCA9IFtdO1xuICAgICAgICBmb3IgKGQgPSAwOyBkIDwgZGltOyBkKyspIHByZXZQW2RdID0gMDtcblxuICAgICAgICB3aGlsZSAobGVuID8gaSA8IGxlbiA6IHBiZi5wb3MgPCBlbmQpIHtcbiAgICAgICAgICAgIHAgPSBbXTtcbiAgICAgICAgICAgIGZvciAoZCA9IDA7IGQgPCBkaW07IGQrKykge1xuICAgICAgICAgICAgICAgIHByZXZQW2RdICs9IHBiZi5yZWFkU1ZhcmludCgpO1xuICAgICAgICAgICAgICAgIHBbZF0gPSB0cmFuc2Zvcm1Db29yZChwcmV2UFtkXSk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBjb29yZHMucHVzaChwKTtcbiAgICAgICAgICAgIGkrKztcbiAgICAgICAgfVxuICAgIH1cblxuICAgIHJldHVybiBjb29yZHM7XG59XG5cbmZ1bmN0aW9uIHJlYWRMaW5lKHBiZiwgaXNNdWx0aVBvaW50KSB7XG4gICAgcmV0dXJuIHJlYWRMaW5lUGFydChwYmYsIHBiZi5yZWFkVmFyaW50KCkgKyBwYmYucG9zLCBudWxsLCBpc011bHRpUG9pbnQpO1xufVxuXG5mdW5jdGlvbiByZWFkTXVsdGlMaW5lKHBiZikge1xuICAgIHZhciBlbmQgPSBwYmYucmVhZFZhcmludCgpICsgcGJmLnBvcztcbiAgICBpZiAoIWxlbmd0aHMpIHJldHVybiBbcmVhZExpbmVQYXJ0KHBiZiwgZW5kKV07XG5cbiAgICB2YXIgY29vcmRzID0gW107XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBsZW5ndGhzLmxlbmd0aDsgaSsrKSBjb29yZHMucHVzaChyZWFkTGluZVBhcnQocGJmLCBlbmQsIGxlbmd0aHNbaV0pKTtcbiAgICBsZW5ndGhzID0gbnVsbDtcbiAgICByZXR1cm4gY29vcmRzO1xufVxuXG5mdW5jdGlvbiByZWFkTXVsdGlQb2x5Z29uKHBiZikge1xuICAgIHZhciBlbmQgPSBwYmYucmVhZFZhcmludCgpICsgcGJmLnBvcztcbiAgICBpZiAoIWxlbmd0aHMpIHJldHVybiBbW3JlYWRMaW5lUGFydChwYmYsIGVuZCldXTtcblxuICAgIHZhciBjb29yZHMgPSBbXTtcbiAgICB2YXIgaiA9IDE7XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBsZW5ndGhzWzBdOyBpKyspIHtcbiAgICAgICAgdmFyIHJpbmdzID0gW107XG4gICAgICAgIGZvciAodmFyIGsgPSAwOyBrIDwgbGVuZ3Roc1tqXTsgaysrKSByaW5ncy5wdXNoKHJlYWRMaW5lUGFydChwYmYsIGVuZCwgbGVuZ3Roc1tqICsgMSArIGtdKSk7XG4gICAgICAgIGogKz0gbGVuZ3Roc1tqXSArIDE7XG4gICAgICAgIGNvb3Jkcy5wdXNoKHJpbmdzKTtcbiAgICB9XG4gICAgbGVuZ3RocyA9IG51bGw7XG4gICAgcmV0dXJuIGNvb3Jkcztcbn1cblxuZnVuY3Rpb24gcmVhZEFyY3MocGJmKSB7XG4gICAgdmFyIGxpbmVzID0gW10sXG4gICAgICAgIGVuZCA9IHBiZi5yZWFkVmFyaW50KCkgKyBwYmYucG9zO1xuXG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBsZW5ndGhzLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIHZhciByaW5nID0gW107XG4gICAgICAgIGZvciAodmFyIGogPSAwOyBqIDwgbGVuZ3Roc1tpXTsgaisrKSB7XG4gICAgICAgICAgICB2YXIgcCA9IFtdO1xuICAgICAgICAgICAgZm9yICh2YXIgZCA9IDA7IGQgPCBkaW0gJiYgcGJmLnBvcyA8IGVuZDsgZCsrKSBwW2RdID0gdHJhbnNmb3JtQ29vcmQocGJmLnJlYWRTVmFyaW50KCkpO1xuICAgICAgICAgICAgcmluZy5wdXNoKHApO1xuICAgICAgICB9XG4gICAgICAgIGxpbmVzLnB1c2gocmluZyk7XG4gICAgfVxuXG4gICAgcmV0dXJuIGxpbmVzO1xufVxuXG5mdW5jdGlvbiB0cmFuc2Zvcm1Db29yZCh4KSB7XG4gICAgcmV0dXJuIHRyYW5zZm9ybWVkID8geCA6IHggLyBlO1xufVxuIiwiJ3VzZSBzdHJpY3QnO1xuXG5tb2R1bGUuZXhwb3J0cyA9IGVuY29kZTtcblxudmFyIGtleXMsIGtleXNOdW0sIGRpbSwgZSwgaXNUb3BvLCB0cmFuc2Zvcm1lZCxcbiAgICBtYXhQcmVjaXNpb24gPSAxZTY7XG5cbnZhciBnZW9tZXRyeVR5cGVzID0ge1xuICAgICdQb2ludCc6IDAsXG4gICAgJ011bHRpUG9pbnQnOiAxLFxuICAgICdMaW5lU3RyaW5nJzogMixcbiAgICAnTXVsdGlMaW5lU3RyaW5nJzogMyxcbiAgICAnUG9seWdvbic6IDQsXG4gICAgJ011bHRpUG9seWdvbic6IDUsXG4gICAgJ0dlb21ldHJ5Q29sbGVjdGlvbic6IDZcbn07XG5cbmZ1bmN0aW9uIGVuY29kZShvYmosIHBiZikge1xuICAgIGtleXMgPSB7fTtcbiAgICBrZXlzTnVtID0gMDtcbiAgICBkaW0gPSAwO1xuICAgIGUgPSAxO1xuICAgIHRyYW5zZm9ybWVkID0gZmFsc2U7XG4gICAgaXNUb3BvID0gZmFsc2U7XG5cbiAgICBhbmFseXplKG9iaik7XG5cbiAgICBlID0gTWF0aC5taW4oZSwgbWF4UHJlY2lzaW9uKTtcbiAgICB2YXIgcHJlY2lzaW9uID0gTWF0aC5jZWlsKE1hdGgubG9nKGUpIC8gTWF0aC5MTjEwKTtcblxuICAgIHZhciBrZXlzQXJyID0gT2JqZWN0LmtleXMoa2V5cyk7XG5cbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IGtleXNBcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZVN0cmluZ0ZpZWxkKDEsIGtleXNBcnJbaV0pO1xuICAgIGlmIChkaW0gIT09IDIpIHBiZi53cml0ZVZhcmludEZpZWxkKDIsIGRpbSk7XG4gICAgaWYgKHByZWNpc2lvbiAhPT0gNikgcGJmLndyaXRlVmFyaW50RmllbGQoMywgcHJlY2lzaW9uKTtcblxuICAgIGlmIChvYmoudHlwZSA9PT0gJ0ZlYXR1cmVDb2xsZWN0aW9uJykgcGJmLndyaXRlTWVzc2FnZSg0LCB3cml0ZUZlYXR1cmVDb2xsZWN0aW9uLCBvYmopO1xuICAgIGVsc2UgaWYgKG9iai50eXBlID09PSAnRmVhdHVyZScpIHBiZi53cml0ZU1lc3NhZ2UoNSwgd3JpdGVGZWF0dXJlLCBvYmopO1xuICAgIGVsc2UgaWYgKG9iai50eXBlID09PSAnVG9wb2xvZ3knKSBwYmYud3JpdGVNZXNzYWdlKDcsIHdyaXRlVG9wb2xvZ3ksIG9iaik7XG4gICAgZWxzZSBwYmYud3JpdGVNZXNzYWdlKDYsIHdyaXRlR2VvbWV0cnksIG9iaik7XG5cbiAgICBrZXlzID0gbnVsbDtcblxuICAgIHJldHVybiBwYmYuZmluaXNoKCk7XG59XG5cbmZ1bmN0aW9uIGFuYWx5emUob2JqKSB7XG4gICAgdmFyIGksIGtleTtcblxuICAgIGlmIChvYmoudHlwZSA9PT0gJ0ZlYXR1cmVDb2xsZWN0aW9uJykge1xuICAgICAgICBmb3IgKGkgPSAwOyBpIDwgb2JqLmZlYXR1cmVzLmxlbmd0aDsgaSsrKSBhbmFseXplKG9iai5mZWF0dXJlc1tpXSk7XG4gICAgICAgIGZvciAoa2V5IGluIG9iaikgaWYgKGtleSAhPT0gJ3R5cGUnICYmIGtleSAhPT0gJ2ZlYXR1cmVzJykgc2F2ZUtleShrZXkpO1xuXG4gICAgfSBlbHNlIGlmIChvYmoudHlwZSA9PT0gJ0ZlYXR1cmUnKSB7XG4gICAgICAgIGFuYWx5emUob2JqLmdlb21ldHJ5KTtcbiAgICAgICAgZm9yIChrZXkgaW4gb2JqLnByb3BlcnRpZXMpIHNhdmVLZXkoa2V5KTtcbiAgICAgICAgZm9yIChrZXkgaW4gb2JqKSB7XG4gICAgICAgICAgICBpZiAoa2V5ICE9PSAndHlwZScgJiYga2V5ICE9PSAnaWQnICYmIGtleSAhPT0gJ3Byb3BlcnRpZXMnICYmIGtleSAhPT0gJ2dlb21ldHJ5Jykgc2F2ZUtleShrZXkpO1xuICAgICAgICB9XG5cbiAgICB9IGVsc2UgaWYgKG9iai50eXBlID09PSAnVG9wb2xvZ3knKSB7XG4gICAgICAgIGlzVG9wbyA9IHRydWU7XG5cbiAgICAgICAgZm9yIChrZXkgaW4gb2JqKSB7XG4gICAgICAgICAgICBpZiAoa2V5ICE9PSAndHlwZScgJiYga2V5ICE9PSAndHJhbnNmb3JtJyAmJiBrZXkgIT09ICdhcmNzJyAmJiBrZXkgIT09ICdvYmplY3RzJykgc2F2ZUtleShrZXkpO1xuICAgICAgICB9XG4gICAgICAgIGFuYWx5emVNdWx0aUxpbmUob2JqLmFyY3MpO1xuXG4gICAgICAgIGZvciAoa2V5IGluIG9iai5vYmplY3RzKSB7XG4gICAgICAgICAgICBhbmFseXplKG9iai5vYmplY3RzW2tleV0pO1xuICAgICAgICB9XG5cbiAgICB9IGVsc2Uge1xuICAgICAgICBpZiAob2JqLnR5cGUgPT09ICdQb2ludCcpIGFuYWx5emVQb2ludChvYmouY29vcmRpbmF0ZXMpO1xuICAgICAgICBlbHNlIGlmIChvYmoudHlwZSA9PT0gJ011bHRpUG9pbnQnKSBhbmFseXplUG9pbnRzKG9iai5jb29yZGluYXRlcyk7XG4gICAgICAgIGVsc2UgaWYgKG9iai50eXBlID09PSAnR2VvbWV0cnlDb2xsZWN0aW9uJykge1xuICAgICAgICAgICAgZm9yIChpID0gMDsgaSA8IG9iai5nZW9tZXRyaWVzLmxlbmd0aDsgaSsrKSBhbmFseXplKG9iai5nZW9tZXRyaWVzW2ldKTtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIGlmICghaXNUb3BvKSB7XG4gICAgICAgICAgICBpZiAob2JqLnR5cGUgPT09ICdMaW5lU3RyaW5nJykgYW5hbHl6ZVBvaW50cyhvYmouY29vcmRpbmF0ZXMpO1xuICAgICAgICAgICAgZWxzZSBpZiAob2JqLnR5cGUgPT09ICdQb2x5Z29uJyB8fCBvYmoudHlwZSA9PT0gJ011bHRpTGluZVN0cmluZycpIGFuYWx5emVNdWx0aUxpbmUob2JqLmNvb3JkaW5hdGVzKTtcbiAgICAgICAgICAgIGVsc2UgaWYgKG9iai50eXBlID09PSAnTXVsdGlQb2x5Z29uJykge1xuICAgICAgICAgICAgICAgIGZvciAoaSA9IDA7IGkgPCBvYmouY29vcmRpbmF0ZXMubGVuZ3RoOyBpKyspIGFuYWx5emVNdWx0aUxpbmUob2JqLmNvb3JkaW5hdGVzW2ldKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIGZvciAoa2V5IGluIG9iai5wcm9wZXJ0aWVzKSBzYXZlS2V5KGtleSk7XG4gICAgICAgIGZvciAoa2V5IGluIG9iaikge1xuICAgICAgICAgICAgaWYgKGtleSAhPT0gJ3R5cGUnICYmIGtleSAhPT0gJ2lkJyAmJiBrZXkgIT09ICdjb29yZGluYXRlcycgJiYga2V5ICE9PSAnYXJjcycgJiZcbiAgICAgICAgICAgICAgICBrZXkgIT09ICdnZW9tZXRyaWVzJyAmJiBrZXkgIT09ICdwcm9wZXJ0aWVzJykgc2F2ZUtleShrZXkpO1xuICAgICAgICB9XG4gICAgfVxufVxuXG5mdW5jdGlvbiBhbmFseXplTXVsdGlMaW5lKGNvb3Jkcykge1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY29vcmRzLmxlbmd0aDsgaSsrKSBhbmFseXplUG9pbnRzKGNvb3Jkc1tpXSk7XG59XG5cbmZ1bmN0aW9uIGFuYWx5emVQb2ludHMoY29vcmRzKSB7XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBjb29yZHMubGVuZ3RoOyBpKyspIGFuYWx5emVQb2ludChjb29yZHNbaV0pO1xufVxuXG5mdW5jdGlvbiBhbmFseXplUG9pbnQocG9pbnQpIHtcbiAgICBkaW0gPSBNYXRoLm1heChkaW0sIHBvaW50Lmxlbmd0aCk7XG5cbiAgICAvLyBmaW5kIG1heCBwcmVjaXNpb25cbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IHBvaW50Lmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIHdoaWxlIChNYXRoLnJvdW5kKHBvaW50W2ldICogZSkgLyBlICE9PSBwb2ludFtpXSAmJiBlIDwgbWF4UHJlY2lzaW9uKSBlICo9IDEwO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gc2F2ZUtleShrZXkpIHtcbiAgICBpZiAoa2V5c1trZXldID09PSB1bmRlZmluZWQpIGtleXNba2V5XSA9IGtleXNOdW0rKztcbn1cblxuZnVuY3Rpb24gd3JpdGVGZWF0dXJlQ29sbGVjdGlvbihvYmosIHBiZikge1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgb2JqLmZlYXR1cmVzLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIHBiZi53cml0ZU1lc3NhZ2UoMSwgd3JpdGVGZWF0dXJlLCBvYmouZmVhdHVyZXNbaV0pO1xuICAgIH1cbiAgICB3cml0ZVByb3BzKG9iaiwgcGJmLCB0cnVlKTtcbn1cblxuZnVuY3Rpb24gd3JpdGVGZWF0dXJlKGZlYXR1cmUsIHBiZikge1xuICAgIHBiZi53cml0ZU1lc3NhZ2UoMSwgd3JpdGVHZW9tZXRyeSwgZmVhdHVyZS5nZW9tZXRyeSk7XG5cbiAgICBpZiAoZmVhdHVyZS5pZCAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgIGlmICh0eXBlb2YgZmVhdHVyZS5pZCA9PT0gJ251bWJlcicgJiYgZmVhdHVyZS5pZCAlIDEgPT09IDApIHBiZi53cml0ZVNWYXJpbnRGaWVsZCgxMiwgZmVhdHVyZS5pZCk7XG4gICAgICAgIGVsc2UgcGJmLndyaXRlU3RyaW5nRmllbGQoMTEsIGZlYXR1cmUuaWQpO1xuICAgIH1cblxuICAgIGlmIChmZWF0dXJlLnByb3BlcnRpZXMpIHdyaXRlUHJvcHMoZmVhdHVyZS5wcm9wZXJ0aWVzLCBwYmYpO1xuICAgIHdyaXRlUHJvcHMoZmVhdHVyZSwgcGJmLCB0cnVlKTtcbn1cblxuZnVuY3Rpb24gd3JpdGVHZW9tZXRyeShnZW9tLCBwYmYpIHtcbiAgICBwYmYud3JpdGVWYXJpbnRGaWVsZCgxLCBnZW9tZXRyeVR5cGVzW2dlb20udHlwZV0pO1xuXG4gICAgdmFyIGNvb3JkcyA9IGdlb20uY29vcmRpbmF0ZXMsXG4gICAgICAgIGNvb3Jkc09yQXJjcyA9IGlzVG9wbyA/IGdlb20uYXJjcyA6IGNvb3JkcztcblxuICAgIGlmIChnZW9tLnR5cGUgPT09ICdQb2ludCcpIHdyaXRlUG9pbnQoY29vcmRzLCBwYmYpO1xuICAgIGVsc2UgaWYgKGdlb20udHlwZSA9PT0gJ011bHRpUG9pbnQnKSB3cml0ZUxpbmUoY29vcmRzLCBwYmYsIHRydWUpO1xuICAgIGVsc2UgaWYgKGdlb20udHlwZSA9PT0gJ0xpbmVTdHJpbmcnKSB3cml0ZUxpbmUoY29vcmRzT3JBcmNzLCBwYmYpO1xuICAgIGlmIChnZW9tLnR5cGUgPT09ICdNdWx0aUxpbmVTdHJpbmcnIHx8IGdlb20udHlwZSA9PT0gJ1BvbHlnb24nKSB3cml0ZU11bHRpTGluZShjb29yZHNPckFyY3MsIHBiZik7XG4gICAgZWxzZSBpZiAoZ2VvbS50eXBlID09PSAnTXVsdGlQb2x5Z29uJykgd3JpdGVNdWx0aVBvbHlnb24oY29vcmRzT3JBcmNzLCBwYmYpO1xuICAgIGVsc2UgaWYgKGdlb20udHlwZSA9PT0gJ0dlb21ldHJ5Q29sbGVjdGlvbicpIHtcbiAgICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBnZW9tLmdlb21ldHJpZXMubGVuZ3RoOyBpKyspIHBiZi53cml0ZU1lc3NhZ2UoNCwgd3JpdGVHZW9tZXRyeSwgZ2VvbS5nZW9tZXRyaWVzW2ldKTtcbiAgICB9XG5cbiAgICBpZiAoaXNUb3BvICYmIGdlb20uaWQgIT09IHVuZGVmaW5lZCkge1xuICAgICAgICBpZiAodHlwZW9mIGdlb20uaWQgPT09ICdudW1iZXInICYmIGdlb20uaWQgJSAxID09PSAwKSBwYmYud3JpdGVTVmFyaW50RmllbGQoMTIsIGdlb20uaWQpO1xuICAgICAgICBlbHNlIHBiZi53cml0ZVN0cmluZ0ZpZWxkKDExLCBnZW9tLmlkKTtcbiAgICB9XG5cbiAgICBpZiAoaXNUb3BvICYmIGdlb20ucHJvcGVydGllcykgd3JpdGVQcm9wcyhnZW9tLnByb3BlcnRpZXMsIHBiZik7XG4gICAgd3JpdGVQcm9wcyhnZW9tLCBwYmYsIHRydWUpO1xufVxuXG5mdW5jdGlvbiB3cml0ZVRvcG9sb2d5KHRvcG9sb2d5LCBwYmYpIHtcbiAgICBpZiAodG9wb2xvZ3kudHJhbnNmb3JtKSB7XG4gICAgICAgIHBiZi53cml0ZU1lc3NhZ2UoMSwgd3JpdGVUcmFuc2Zvcm0sIHRvcG9sb2d5LnRyYW5zZm9ybSk7XG4gICAgICAgIHRyYW5zZm9ybWVkID0gdHJ1ZTtcbiAgICB9XG5cbiAgICB2YXIgbmFtZXMgPSBPYmplY3Qua2V5cyh0b3BvbG9neS5vYmplY3RzKSxcbiAgICAgICAgaSwgaiwgZDtcblxuICAgIGZvciAoaSA9IDA7IGkgPCBuYW1lcy5sZW5ndGg7IGkrKykgcGJmLndyaXRlU3RyaW5nRmllbGQoMiwgbmFtZXNbaV0pO1xuICAgIGZvciAoaSA9IDA7IGkgPCBuYW1lcy5sZW5ndGg7IGkrKykge1xuICAgICAgICBwYmYud3JpdGVNZXNzYWdlKDMsIHdyaXRlR2VvbWV0cnksIHRvcG9sb2d5Lm9iamVjdHNbbmFtZXNbaV1dKTtcbiAgICB9XG5cbiAgICB2YXIgbGVuZ3RocyA9IFtdLFxuICAgICAgICBjb29yZHMgPSBbXTtcblxuICAgIGZvciAoaSA9IDA7IGkgPCB0b3BvbG9neS5hcmNzLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIHZhciBhcmMgPSB0b3BvbG9neS5hcmNzW2ldO1xuICAgICAgICBsZW5ndGhzLnB1c2goYXJjLmxlbmd0aCk7XG5cbiAgICAgICAgZm9yIChqID0gMDsgaiA8IGFyYy5sZW5ndGg7IGorKykge1xuICAgICAgICAgICAgZm9yIChkID0gMDsgZCA8IGRpbTsgZCsrKSBjb29yZHMucHVzaCh0cmFuc2Zvcm1Db29yZChhcmNbal1bZF0pKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIHBiZi53cml0ZVBhY2tlZFZhcmludCg0LCBsZW5ndGhzKTtcbiAgICBwYmYud3JpdGVQYWNrZWRTVmFyaW50KDUsIGNvb3Jkcyk7XG5cbiAgICB3cml0ZVByb3BzKHRvcG9sb2d5LCBwYmYsIHRydWUpO1xufVxuXG5mdW5jdGlvbiB3cml0ZVByb3BzKHByb3BzLCBwYmYsIGlzQ3VzdG9tKSB7XG4gICAgdmFyIGluZGV4ZXMgPSBbXSxcbiAgICAgICAgdmFsdWVJbmRleCA9IDA7XG5cbiAgICBmb3IgKHZhciBrZXkgaW4gcHJvcHMpIHtcbiAgICAgICAgaWYgKGlzQ3VzdG9tKSB7XG4gICAgICAgICAgICBpZiAoa2V5ID09PSAndHlwZScpIGNvbnRpbnVlO1xuICAgICAgICAgICAgZWxzZSBpZiAocHJvcHMudHlwZSA9PT0gJ0ZlYXR1cmVDb2xsZWN0aW9uJykge1xuICAgICAgICAgICAgICAgIGlmIChrZXkgPT09ICdmZWF0dXJlcycpIGNvbnRpbnVlO1xuICAgICAgICAgICAgfSBlbHNlIGlmIChwcm9wcy50eXBlID09PSAnRmVhdHVyZScpIHtcbiAgICAgICAgICAgICAgICBpZiAoa2V5ID09PSAnaWQnIHx8IGtleSA9PT0gJ3Byb3BlcnRpZXMnIHx8IGtleSA9PT0gJ2dlb21ldHJ5JykgY29udGludWU7XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHByb3BzLnR5cGUgPT09ICdUb3BvbG9neScpICB7XG4gICAgICAgICAgICAgICAgaWYgKGtleSA9PT0gJ3RyYW5zZm9ybScgfHwga2V5ID09PSAnYXJjcycgfHwga2V5ID09PSAnb2JqZWN0cycpIGNvbnRpbnVlO1xuICAgICAgICAgICAgfSBlbHNlIGlmIChrZXkgPT09ICdpZCcgfHwga2V5ID09PSAnY29vcmRpbmF0ZXMnIHx8IGtleSA9PT0gJ2FyY3MnIHx8XG4gICAgICAgICAgICAgICAgICAgICAgIGtleSA9PT0gJ2dlb21ldHJpZXMnIHx8IGtleSA9PT0gJ3Byb3BlcnRpZXMnKSBjb250aW51ZTtcbiAgICAgICAgfVxuICAgICAgICBwYmYud3JpdGVNZXNzYWdlKDEzLCB3cml0ZVZhbHVlLCBwcm9wc1trZXldKTtcbiAgICAgICAgaW5kZXhlcy5wdXNoKGtleXNba2V5XSwgdmFsdWVJbmRleCsrKTtcbiAgICB9XG4gICAgcGJmLndyaXRlUGFja2VkVmFyaW50KGlzQ3VzdG9tID8gMTUgOiAxNCwgaW5kZXhlcyk7XG59XG5cbmZ1bmN0aW9uIHdyaXRlVmFsdWUodmFsdWUsIHBiZikge1xuICAgIHZhciB0eXBlID0gdHlwZW9mIHZhbHVlO1xuXG4gICAgaWYgKHR5cGUgPT09ICdzdHJpbmcnKSBwYmYud3JpdGVTdHJpbmdGaWVsZCgxLCB2YWx1ZSk7XG4gICAgZWxzZSBpZiAodHlwZSA9PT0gJ2Jvb2xlYW4nKSBwYmYud3JpdGVCb29sZWFuRmllbGQoNSwgdmFsdWUpO1xuICAgIGVsc2UgaWYgKHR5cGUgPT09ICdvYmplY3QnKSBwYmYud3JpdGVTdHJpbmdGaWVsZCg2LCBKU09OLnN0cmluZ2lmeSh2YWx1ZSkpO1xuICAgIGVsc2UgaWYgKHR5cGUgPT09ICdudW1iZXInKSB7XG4gICAgICAgaWYgKHZhbHVlICUgMSAhPT0gMCkgcGJmLndyaXRlRG91YmxlRmllbGQoMiwgdmFsdWUpO1xuICAgICAgIGVsc2UgaWYgKHZhbHVlID49IDApIHBiZi53cml0ZVZhcmludEZpZWxkKDMsIHZhbHVlKTtcbiAgICAgICBlbHNlIHBiZi53cml0ZVZhcmludEZpZWxkKDQsIC12YWx1ZSk7XG4gICAgfVxufVxuXG5mdW5jdGlvbiB3cml0ZVBvaW50KHBvaW50LCBwYmYpIHtcbiAgICB2YXIgY29vcmRzID0gW107XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBkaW07IGkrKykgY29vcmRzLnB1c2godHJhbnNmb3JtQ29vcmQocG9pbnRbaV0pKTtcbiAgICBwYmYud3JpdGVQYWNrZWRTVmFyaW50KDMsIGNvb3Jkcyk7XG59XG5cbmZ1bmN0aW9uIHdyaXRlTGluZShsaW5lLCBwYmYsIGlzTXVsdGlQb2ludCkge1xuICAgIHZhciBjb29yZHMgPSBbXTtcbiAgICBwb3B1bGF0ZUxpbmUoY29vcmRzLCBsaW5lLCBpc011bHRpUG9pbnQpO1xuICAgIHBiZi53cml0ZVBhY2tlZFNWYXJpbnQoMywgY29vcmRzKTtcbn1cblxuZnVuY3Rpb24gd3JpdGVNdWx0aUxpbmUobGluZXMsIHBiZikge1xuICAgIHZhciBsZW4gPSBsaW5lcy5sZW5ndGgsXG4gICAgICAgIGk7XG4gICAgaWYgKGxlbiAhPT0gMSkge1xuICAgICAgICB2YXIgbGVuZ3RocyA9IFtdO1xuICAgICAgICBmb3IgKGkgPSAwOyBpIDwgbGVuOyBpKyspIGxlbmd0aHMucHVzaChsaW5lc1tpXS5sZW5ndGgpO1xuICAgICAgICBwYmYud3JpdGVQYWNrZWRWYXJpbnQoMiwgbGVuZ3Rocyk7XG4gICAgICAgIC8vIFRPRE8gZmFzdGVyIHdpdGggY3VzdG9tIHdyaXRlTWVzc2FnZT9cbiAgICB9XG4gICAgdmFyIGNvb3JkcyA9IFtdO1xuICAgIGZvciAoaSA9IDA7IGkgPCBsZW47IGkrKykgcG9wdWxhdGVMaW5lKGNvb3JkcywgbGluZXNbaV0pO1xuICAgIHBiZi53cml0ZVBhY2tlZFNWYXJpbnQoMywgY29vcmRzKTtcbn1cblxuZnVuY3Rpb24gd3JpdGVNdWx0aVBvbHlnb24ocG9seWdvbnMsIHBiZikge1xuICAgIHZhciBsZW4gPSBwb2x5Z29ucy5sZW5ndGgsXG4gICAgICAgIGksIGo7XG4gICAgaWYgKGxlbiAhPT0gMSB8fCBwb2x5Z29uc1swXS5sZW5ndGggIT09IDEgfHwgcG9seWdvbnNbMF1bMF0ubGVuZ3RoICE9PSAxKSB7XG4gICAgICAgIHZhciBsZW5ndGhzID0gW2xlbl07XG4gICAgICAgIGZvciAoaSA9IDA7IGkgPCBsZW47IGkrKykge1xuICAgICAgICAgICAgbGVuZ3Rocy5wdXNoKHBvbHlnb25zW2ldLmxlbmd0aCk7XG4gICAgICAgICAgICBmb3IgKGogPSAwOyBqIDwgcG9seWdvbnNbaV0ubGVuZ3RoOyBqKyspIGxlbmd0aHMucHVzaChwb2x5Z29uc1tpXVtqXS5sZW5ndGgpO1xuICAgICAgICB9XG4gICAgICAgIHBiZi53cml0ZVBhY2tlZFZhcmludCgyLCBsZW5ndGhzKTtcbiAgICB9XG5cbiAgICB2YXIgY29vcmRzID0gW107XG4gICAgZm9yIChpID0gMDsgaSA8IGxlbjsgaSsrKSB7XG4gICAgICAgIGZvciAoaiA9IDA7IGogPCBwb2x5Z29uc1tpXS5sZW5ndGg7IGorKykgcG9wdWxhdGVMaW5lKGNvb3JkcywgcG9seWdvbnNbaV1bal0pO1xuICAgIH1cbiAgICBwYmYud3JpdGVQYWNrZWRTVmFyaW50KDMsIGNvb3Jkcyk7XG59XG5cbmZ1bmN0aW9uIHBvcHVsYXRlTGluZShjb29yZHMsIGxpbmUsIGlzTXVsdGlQb2ludCkge1xuICAgIHZhciBpLCBqO1xuICAgIGZvciAoaSA9IDA7IGkgPCBsaW5lLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIGlmIChpc1RvcG8gJiYgIWlzTXVsdGlQb2ludCkgY29vcmRzLnB1c2goaSA/IGxpbmVbaV0gLSBsaW5lW2kgLSAxXSA6IGxpbmVbaV0pO1xuICAgICAgICBlbHNlIGZvciAoaiA9IDA7IGogPCBkaW07IGorKykgY29vcmRzLnB1c2godHJhbnNmb3JtQ29vcmQobGluZVtpXVtqXSAtIChpID8gbGluZVtpIC0gMV1bal0gOiAwKSkpO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gdHJhbnNmb3JtQ29vcmQoeCkge1xuICAgIHJldHVybiB0cmFuc2Zvcm1lZCA/IHggOiBNYXRoLnJvdW5kKHggKiBlKTtcbn1cblxuZnVuY3Rpb24gd3JpdGVUcmFuc2Zvcm0odHIsIHBiZikge1xuICAgIHBiZi53cml0ZURvdWJsZUZpZWxkKDEsIHRyLnNjYWxlWzBdKTtcbiAgICBwYmYud3JpdGVEb3VibGVGaWVsZCgyLCB0ci5zY2FsZVsxXSk7XG4gICAgcGJmLndyaXRlRG91YmxlRmllbGQoMywgdHIudHJhbnNsYXRlWzBdKTtcbiAgICBwYmYud3JpdGVEb3VibGVGaWVsZCg0LCB0ci50cmFuc2xhdGVbMV0pO1xufVxuIiwiJ3VzZSBzdHJpY3QnO1xuXG5leHBvcnRzLmVuY29kZSA9IHJlcXVpcmUoJy4vZW5jb2RlJyk7XG5leHBvcnRzLmRlY29kZSA9IHJlcXVpcmUoJy4vZGVjb2RlJyk7XG4iXX0=
