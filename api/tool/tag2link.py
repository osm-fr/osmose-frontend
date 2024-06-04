# https://raw.githubusercontent.com/JOSM/tag2link/master/index.json

import json
from typing import Dict, List


class tag2link:
    def __init__(self, rulesFiles: str):
        rules_json = json.load(open(rulesFiles, "r", encoding="utf-8"))
        self.rules: Dict[str, str] = dict(
            map(
                lambda rule: [
                    rule["key"][4:],
                    rule["url"],
                ],
                filter(lambda rule: rule["key"].startswith("Key:"), rules_json),
            )
        )

    def addLinks(self, tags: Dict[str, str]) -> List[Dict[str, str]]:
        links = []
        for key, value in tags.items():
            links.append({"k": key, "v": value})
            if key in self.rules:
                links[-1]["vlink"] = self.rules[key].replace("$1", tags[key])
        return links


if __name__ == "__main__":
    t2l = tag2link("tag2link_sources.json")
    print(t2l.addLinks({"oneway": "yes"}))
    print(t2l.addLinks({"url": "plop.com"}))
    print(t2l.addLinks({"url": "http://plop.com"}))
    print(t2l.addLinks({"ref:UAI": "123"}))
    print(
        t2l.addLinks(
            {"man_made": "survey_point", "source": "©IGN 2012", "ref": "1234567 - A"}
        )
    )
    print(
        t2l.addLinks(
            {
                "url": "span://bad",
                "man_made": "survey_point",
                "source": "©IGN 2012",
                "ref": "1234567 - A",
            }
        )
    )
    print(t2l.addLinks({"wikipedia:fr": "toto"}))
    print(t2l.addLinks({"wikipedia": "fr:toto"}))
    print(t2l.addLinks({"wikipedia": "toto"}))
    print(t2l.addLinks({"source": "source", "source:url": "http://example.com"}))
