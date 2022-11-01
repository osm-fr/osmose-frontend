# https://trac.openstreetmap.org/browser/subversion/applications/editors/josm/plugins/tag2link/resources/tag2link_sources.xml?rev=30720&format=txt

import re
import xml.sax


class Exact(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.rules = []
        self.val = re.compile("(%[^%]+%|\{[^}]+})")  # noqa

    def unposix(self, regex):
        regex = regex.replace("\p{Lower}", "[a-z]")  # noqa
        regex = regex.replace("\p{Upper}", "[A-Z]")  # noqa
        regex = regex.replace("\p{Digit}", "[0-9]")  # noqa
        return regex

    def startElement(self, name, attrs):
        if name == "rule":
            self.rules.append({"conditions": [], "link": None})
        elif name == "condition":
            self.rules[-1]["conditions"].append(
                {
                    "kk": attrs["k"],
                    "k": re.compile("^" + self.unposix(attrs["k"]) + "$"),
                    "v": re.compile("^" + self.unposix(attrs["v"]) + "$")
                    if "v" in attrs
                    else None,
                    "id": attrs["id"] if "id" in attrs else None,
                }
            )
        elif name == "link":
            link = attrs["href"]
            subs = []
            if "%" in link or "{" in link:
                for valmatch in self.val.finditer(link):
                    sub = []
                    v = valmatch.group(1)
                    link = link.replace(v, "%s", 1)
                    var = v[1:-1].split(":")
                    for ll in var:
                        if "." not in ll and ll != "v" and ll != "k":
                            vv = ll
                        else:
                            vv = ll.split(".")
                            if vv[0] in ("k", "v"):
                                vv = [None] + vv
                            if len(vv) == 2:
                                vv.append(0)
                            else:
                                vv[2] = int(vv[2])
                        sub.append(vv)
                    subs.append(sub)
            self.rules[-1]["link"] = {"url": link, "subs": subs}


class tag2link:
    def __init__(self, rulesFiles):
        parser = xml.sax.make_parser()
        handler = Exact()
        parser.setContentHandler(handler)
        parser.parse(open(rulesFiles, "r", encoding="utf-8"))
        self.rules = handler.rules
        self.all = re.compile(".*")

    def checkTags(self, tags):
        try:
            urls = {}
            for rule in self.rules:
                valid = True
                id = {}
                for condition in rule["conditions"]:
                    match = False
                    for key in tags.keys():
                        kmatch = condition["k"].match(key)
                        if kmatch:
                            id[condition["id"]] = {"k": kmatch}
                            if condition["v"] is None:
                                vmatch = self.all.match(tags[key])
                                id[condition["id"]]["v"] = vmatch
                                match = True
                                break
                            else:
                                vmatch = condition["v"].match(tags[key])
                                if vmatch:
                                    id[condition["id"]]["v"] = vmatch
                                    match = True
                                    break
                    if not match:
                        valid = False
                        break
                if valid:
                    replace = []
                    for sub in rule["link"]["subs"]:
                        for v in sub:
                            if isinstance(v, str):
                                replace.append(v)
                                break
                            else:
                                val = id[v[0]][v[1]].group(v[2])
                                if val:
                                    replace.append(val)
                                    break
                    ret = rule["link"]["url"] % tuple(replace)
                    if "://" not in ret:
                        ret = "http://" + ret
                    urls[id[rule["link"]["subs"][0][0][0]]["k"].group(0)] = ret
            return urls
        except Exception:
            return {}


if __name__ == "__main__":
    t2l = tag2link("tag2link_sources.xml")
    print(t2l.checkTags({"oneway": "yes"}))
    print(t2l.checkTags({"url": "plop.com"}))
    print(t2l.checkTags({"url": "http://plop.com"}))
    print(t2l.checkTags({"ref:UAI": "123"}))
    print(
        t2l.checkTags(
            {"man_made": "survey_point", "source": "©IGN 2012", "ref": "1234567 - A"}
        )
    )
    print(
        t2l.checkTags(
            {
                "url": "span://bad",
                "man_made": "survey_point",
                "source": "©IGN 2012",
                "ref": "1234567 - A",
            }
        )
    )
    print(t2l.checkTags({"wikipedia:fr": "toto"}))
    print(t2l.checkTags({"wikipedia": "fr:toto"}))
    print(t2l.checkTags({"wikipedia": "toto"}))
    print(t2l.checkTags({"source": "source", "source:url": "http://example.com"}))
