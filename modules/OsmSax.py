import bz2
import gzip
import io
import re
from xml.sax import handler, make_parser
from xml.sax.saxutils import XMLGenerator, quoteattr

###########################################################################


class dummylog:
    def log(self, text):
        return


class dummyout:
    def __init__(self):
        self._n = 0
        self._w = 0
        self._r = 0

    def NodeCreate(self, data):
        self._n += 1
        return

    def WayCreate(self, data):
        self._w += 1
        return

    def RelationCreate(self, data):
        self._r += 1
        return

    def __del__(self):
        print(self._n, self._w, self._r)


###########################################################################


class OsmSaxNotXMLFile(Exception):
    pass


class OsmSaxReader(handler.ContentHandler):
    def log(self, txt):
        self._logger.log(txt)

    def __init__(self, filename, logger=dummylog()):
        self._filename = filename
        self._logger = logger

        # check if file begins with an xml tag
        f = self._GetFile()
        line = f.readline()
        if not line.startswith("<?xml"):
            raise OsmSaxNotXMLFile("File %s is not XML" % filename)

    def _GetFile(self):
        if isinstance(self._filename, str):
            if self._filename.endswith(".bz2"):
                return bz2.BZ2File(self._filename)
            elif self._filename.endswith(".gz"):
                return gzip.open(self._filename)
            else:
                return open(self._filename)
        else:
            return self._filename

    def CopyTo(self, output):
        self._debug_in_way = False
        self._debug_in_relation = False
        self.log("starting nodes")
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(self._GetFile())

    def startElement(self, name, attrs):
        attrs = attrs._attrs
        if name == "changeset":
            self._tags = {}
        elif name == "node":
            attrs["id"] = int(attrs["id"])
            attrs["lat"] = float(attrs["lat"])
            attrs["lon"] = float(attrs["lon"])
            if "version" in attrs:
                attrs["version"] = int(attrs["version"])
            if "user" in attrs:
                attrs["user"] = str(attrs["user"])
            self._data = attrs
            self._tags = {}
        elif name == "way":
            if not self._debug_in_way:
                self._debug_in_way = True
                self.log("starting ways")
            attrs["id"] = int(attrs["id"])
            if "version" in attrs:
                attrs["version"] = int(attrs["version"])
            if "user" in attrs:
                attrs["user"] = str(attrs["user"])
            self._data = attrs
            self._tags = {}
            self._nodes = []
        elif name == "relation":
            if not self._debug_in_relation:
                self._debug_in_relation = True
                self.log("starting relations")
            attrs["id"] = int(attrs["id"])
            if "version" in attrs:
                attrs["version"] = int(attrs["version"])
            if "user" in attrs:
                attrs["user"] = str(attrs["user"])
            self._data = attrs
            self._members = []
            self._tags = {}
        elif name == "nd":
            self._nodes.append(int(attrs["ref"]))
        elif name == "tag":
            self._tags[attrs["k"]] = attrs["v"]
        elif name == "member":
            attrs["type"] = attrs["type"]
            attrs["ref"] = int(attrs["ref"])
            attrs["role"] = attrs["role"]
            self._members.append(attrs)
        elif name == "osm":
            self._output.begin()

    def endElement(self, name):
        if name == "node":
            self._data["tag"] = self._tags
            try:
                self._output.NodeCreate(self._data)
            except:
                print(self._data)
                raise
        elif name == "way":
            self._data["tag"] = self._tags
            self._data["nd"] = self._nodes
            try:
                self._output.WayCreate(self._data)
            except:
                print(self._data)
                raise
        elif name == "relation":
            self._data["tag"] = self._tags
            self._data["member"] = self._members
            try:
                self._output.RelationCreate(self._data)
            except:
                print(self._data)
                raise
        elif name == "osm":
            self._output.end()


###########################################################################


class OsmTextReader:
    def log(self, txt):
        self._logger.log(txt)

    def __init__(self, filename, logger=dummylog()):
        self._filename = filename
        self._logger = logger

    def _GetFile(self):
        if type(self._filename) == file:
            return self._filename
        elif self._filename.endswith(".bz2"):
            return bz2.BZ2File(self._filename)
        elif self._filename.endswith(".gz"):
            return gzip.open(self._filename)
        else:
            return open(self._filename)

    def CopyTo(self, output):

        _re_eid = re.compile(" id=['\"](.+?)['\"]")
        _re_lat = re.compile(" lat=['\"](.+?)['\"]")
        _re_lon = re.compile(" lon=['\"](.+?)['\"]")
        _re_usr = re.compile(" user=['\"](.+?)['\"]")
        _re_tag = re.compile(" k=['\"](.+?)['\"] v=['\"](.+?)['\"]")

        f = self._GetFile()
        l = f.readline()
        while l:

            if "<node" in l:

                _dat = {}
                _dat["id"] = int(_re_eid.findall(l)[0])
                _dat["lat"] = float(_re_lat.findall(l)[0])
                _dat["lon"] = float(_re_lon.findall(l)[0])
                _usr = _re_lon.findall(l)
                if _usr:
                    _dat["lon"] = _usr[0].decode("utf8")
                _dat["tag"] = {}

                if "/>" in l:
                    output.NodeCreate(_dat)
                    l = f.readline()
                    continue

                l = f.readline()
                while "</node>" not in l:
                    _tag = _re_tag.findall(l)[0]
                    _dat["tag"][_tag[0].decode("utf8")] = _tag[1].decode("utf8")
                    l = f.readline()

                output.NodeCreate(_dat)
                l = f.readline()
                continue

            if "<way" in l:

                _dat = {}
                _dat["id"] = int(_re_eid.findall(l)[0])
                _usr = _re_lon.findall(l)
                if _usr:
                    _dat["lon"] = _usr[0].decode("utf8")
                _dat["tag"] = {}
                _dat["nd"] = []

                l = f.readline()
                while "</way>" not in l:
                    if "<nd" in l:
                        _dat["nd"].append(int(_re_nod.findall(l)[0]))
                        continue
                    _tag = _re_tag.findall(l)[0]
                    _dat["tag"][_tag[0].decode("utf8")] = _tag[1].decode("utf8")
                    l = f.readline()

                output.WayCreate(_dat)
                l = f.readline()
                continue

            if "<relation" in l:
                l = f.readline()
                continue

            l = f.readline()


###########################################################################


class OscSaxReader(handler.ContentHandler):
    def log(self, txt):
        self._logger.log(txt)

    def __init__(self, filename, logger=dummylog()):
        self._filename = filename
        self._logger = logger

    def _GetFile(self):
        if type(self._filename) == file:
            return self._filename
        elif self._filename.endswith(".bz2"):
            return bz2.BZ2File(self._filename)
        elif self._filename.endswith(".gz"):
            return gzip.open(self._filename)
        else:
            return open(self._filename)

    def CopyTo(self, output):
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(self._GetFile())

    def startElement(self, name, attrs):
        attrs = attrs._attrs
        if name == "create":
            self._action = name
        elif name == "modify":
            self._action = name
        elif name == "delete":
            self._action = name
        elif name == "node":
            attrs["id"] = int(attrs["id"])
            attrs["lat"] = float(attrs["lat"])
            attrs["lon"] = float(attrs["lon"])
            attrs["version"] = int(attrs["version"])
            self._data = attrs
            self._tags = {}
        elif name == "way":
            attrs["id"] = int(attrs["id"])
            attrs["version"] = int(attrs["version"])
            self._data = attrs
            self._tags = {}
            self._nodes = []
        elif name == "relation":
            attrs["id"] = int(attrs["id"])
            attrs["version"] = int(attrs["version"])
            self._data = attrs
            self._members = []
            self._tags = {}
        elif name == "nd":
            self._nodes.append(int(attrs["ref"]))
        elif name == "tag":
            self._tags[attrs["k"]] = attrs["v"]
        elif name == "member":
            attrs["ref"] = int(attrs["ref"])
            self._members.append(attrs)

    def endElement(self, name):
        if name == "node":
            self._data["tag"] = self._tags
            if self._action == "create":
                self._output.NodeCreate(self._data)
            elif self._action == "modify":
                self._output.NodeUpdate(self._data)
            elif self._action == "delete":
                self._output.NodeDelete(self._data)
        elif name == "way":
            self._data["tag"] = self._tags
            self._data["nd"] = self._nodes
            if self._action == "create":
                self._output.WayCreate(self._data)
            elif self._action == "modify":
                self._output.WayUpdate(self._data)
            elif self._action == "delete":
                self._output.WayDelete(self._data)
        elif name == "relation":
            self._data["tag"] = self._tags
            self._data["member"] = self._members
            if self._action == "create":
                self._output.RelationCreate(self._data)
            elif self._action == "modify":
                self._output.RelationUpdate(self._data)
            elif self._action == "delete":
                self._output.RelationDelete(self._data)
            return


###########################################################################


def _formatData(data):
    data = dict(data)
    if "tag" in data:
        data.pop("tag")
    if "nd" in data:
        data.pop("nd")
    if "member" in data:
        data.pop("member")
    if "visible" in data:
        data["visible"] = str(data["visible"]).lower()
    if "id" in data:
        data["id"] = str(data["id"])
    if "lat" in data:
        data["lat"] = str(data["lat"])
    if "lon" in data:
        data["lon"] = str(data["lon"])
    if "changeset" in data:
        data["changeset"] = str(data["changeset"])
    if "version" in data:
        data["version"] = str(data["version"])
    if "uid" in data:
        data["uid"] = str(data["uid"])
    return data


class OsmSaxWriter(XMLGenerator):
    def __init__(self, out, enc):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)

    def startElement(self, name, attrs):
        self._write("<" + name)
        for (name, value) in attrs.items():
            self._write(" %s=%s" % (name, quoteattr(value)))
        self._write(">\n")

    def endElement(self, name):
        self._write("</%s>\n" % name)

    def Element(self, name, attrs):
        self._write("<" + name)
        for (name, value) in attrs.items():
            self._write(" %s=%s" % (name, quoteattr(value)))
        self._write(" />\n")

    def begin(self):
        self.startElement("osm", {"version": "0.6", "generator": "OsmSax"})

    def end(self):
        self.endElement("osm")

    def NodeCreate(self, data):
        if not data:
            return
        if data["tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data["tag"].items():
                self.Element("tag", {"k": k, "v": v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))

    def WayCreate(self, data):
        if not data:
            return
        self.startElement("way", _formatData(data))
        for (k, v) in data["tag"].items():
            self.Element("tag", {"k": k, "v": v})
        for n in data["nd"]:
            self.Element("nd", {"ref": str(n)})
        self.endElement("way")

    def RelationCreate(self, data):
        if not data:
            return
        self.startElement("relation", _formatData(data))
        for (k, v) in data["tag"].items():
            self.Element("tag", {"k": k, "v": v})
        for m in data["member"]:
            m["ref"] = str(m["ref"])
            self.Element("member", m)
        self.endElement("relation")


class OsmDictWriter:
    def __init__(self):
        self.data = {"node": [], "way": [], "relation": []}

    def begin(self):
        pass

    def end(self):
        pass

    def NodeCreate(self, data):
        if data:
            self.data["node"].append(data)

    def WayCreate(self, data):
        if data:
            self.data["way"].append(data)

    def RelationCreate(self, data):
        if data:
            self.data["relation"].append(data)


def NodeToXml(data, full=False):
    o = io.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {"version": "0.6"})
    if data:
        w.NodeCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()


def WayToXml(data, full=False):
    o = io.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {"version": "0.6"})
    if data:
        w.WayCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()


def RelationToXml(data, full=False):
    o = io.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {"version": "0.6"})
    if data:
        w.RelationCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()


###########################################################################
import unittest


class TestCountObjects:
    def __init__(self):
        self.num_nodes = 0
        self.num_ways = 0
        self.num_rels = 0

    def begin(self):
        pass

    def end(self):
        pass

    def NodeCreate(self, data):
        self.num_nodes += 1

    def WayCreate(self, data):
        self.num_ways += 1

    def RelationCreate(self, data):
        self.num_rels += 1


class Test(unittest.TestCase):
    def test1(self):
        i1 = OsmSaxReader("tests/saint_barthelemy.osm.bz2")
        o1 = TestCountObjects()
        i1.CopyTo(o1)
        self.assertEquals(o1.num_nodes, 8076)
        self.assertEquals(o1.num_ways, 625)
        self.assertEquals(o1.num_rels, 16)

    def test2(self):
        i1 = OsmSaxReader("tests/saint_barthelemy.osm.gz")
        o1 = TestCountObjects()
        i1.CopyTo(o1)
        self.assertEquals(o1.num_nodes, 8076)
        self.assertEquals(o1.num_ways, 625)
        self.assertEquals(o1.num_rels, 16)
