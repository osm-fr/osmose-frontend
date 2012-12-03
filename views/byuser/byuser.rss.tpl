<?xml version="1.0" encoding="UTF-8"?>
%from tools import utils
%from datetime import datetime
<rss version="2.0">
<channel>
    <title>Osmose - {{username}}</title>
    <description>{{_("Statistics for user %s") % username}}.
%if count < 500:
    {{_("Number of found errors: %d") % count}}.
%else:
    {{_("Number of found errors: more than %d") % count}}.
%end
    </description>
    <lastBuildDate>\\
%if len(results) > 0:
{{results[0]["timestamp"].ctime()}}\\
%end
</lastBuildDate>
    <link>http://{{utils.website}}/byuser/{{username}}</link>
%for res in results:
    <item>
        <title>{{translate.select(res["title"])}}</title>
        <description>
%    if res["subtitle"]:
        {{translate.select(res["subtitle"])}}
%    end
        item={{res["item"]}}, class={{res["class"]}}, level={{res["level"]}}
        {{'<a href="http://%s/error/%s">E</a>' % (utils.website, res['id'])}}
%    lat = float(res["lat"])/1000000.
%    lon = float(res["lon"])/1000000.
%    minlat = lat - 0.002
%    maxlat = lat + 0.002
%    minlon = lon - 0.002
%    maxlon = lon + 0.002
        {{'<a href="http://localhost:8111/load_and_zoom?left=%s&amp;bottom=%s&amp;right=%s&amp;top=%s">josm</a>' % (minlon, minlat, maxlon, maxlat)}}
        </description>
        <category>{{res["item"]}}</category>
%    cl = res["class"]
%    source = res["source"]
%    item = res["item"]
%    level = res["level"]
%    lat_s = "%.2f" % lat
%    lon_s = "%.2f" % lon
        <link>http://{{utils.website}}/map/?zoom=16&amp;lat={{lat}}&amp;lon={{lon}}&amp;item={{item}}&amp;level={{level}}</link>
    </item>
%end
</channel>
</rss>
