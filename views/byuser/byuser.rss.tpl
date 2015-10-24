<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Osmose - {{", ".join(users)}}</title>
    <description>{{_("Statistics for user %s") % ", ".join(users)}}.
%if count < 500:
    {{_("Number of found issues: %d") % count}}.
%else:
    {{_("Number of found issues: more than %d") % count}}.
%end
    </description>
    <lastBuildDate>\\
%if len(errors) > 0:
{{errors[0]["timestamp"].ctime()}}\\
%end
</lastBuildDate>
    <link>http://{{website}}/byuser/{{username}}</link>
%for res in errors:
    <item>
        <title>{{translate.select(res["title"])}}</title>
        <description>
%    if res["subtitle"]:
        {{translate.select(res["subtitle"])}}
%    end
        item={{res["item"]}}, class={{res["class"]}}, level={{res["level"]}}
        {{'<a href="http://%s/error/%s">E</a>' % (website, res['id'])}}
%    lat = res["lat"]
%    lon = res["lon"]
%    minlat = float(lat) - 0.002
%    maxlat = float(lat) + 0.002
%    minlon = float(lon) - 0.002
%    maxlon = float(lon) + 0.002
        {{'<a href="http://localhost:8111/load_and_zoom?left=%s&amp;bottom=%s&amp;right=%s&amp;top=%s">josm</a>' % (minlon, minlat, maxlon, maxlat)}}
        </description>
        <category>{{res["item"]}}</category>
%    cl = res["class"]
%    source = res["source"]
%    item = res["item"]
%    level = res["level"]
%    lat_s = "%.2f" % lat
%    lon_s = "%.2f" % lon
%    url = 'http://%s/map/#zoom=16&amp;lat=%s&amp;lon=%s&amp;item=%s&amp;level=%s' % (website, lat, lon, item, level)
        <link>{{url}}</link>
        <guid>{{url}}</guid>
    </item>
%end
</channel>
</rss>
