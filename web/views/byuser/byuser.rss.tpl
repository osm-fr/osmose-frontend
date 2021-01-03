<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
%rss="https://"+website+"/byuser/"+username+".rss"
    <atom:link href="{{rss}}" rel="self" type="application/rss+xml" />
    <title>Osmose - {{", ".join(users)}}</title>
    <description>{{_("Statistics for user %s") % ", ".join(users)}}.
%if count < 500:
    {{_("Number of found issues: %d") % count}}.
%else:
    {{_("Number of found issues: more than %d") % count}}.
%end
    </description>
%if len(errors) > 0:
%time = errors[0]["timestamp"]
%ctime = time.ctime()
%rfc822 = '{0}, {1:02d} {2}'.format(ctime[0:3], time.day, ctime[4:7]) + time.strftime(' %Y %H:%M:%S %z')
    <lastBuildDate>{{rfc822}}</lastBuildDate>
%end
    <link>http://{{website}}/byuser/{{username}}</link>
%for res in errors:
    <item>
        <title>{{res["title"]}}</title>
        <description>
%    if res["subtitle"]:
        {{res["subtitle"]}}
%    end
        item={{res["item"]}}, class={{res["class"]}}, level={{res["level"]}}
        {{'<a href="http://%s/error/%s">E</a>' % (website, res['uuid'])}}
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
%    source = res["source_id"]
%    item = res["item"]
%    level = res["level"]
%    lat_s = "%.2f" % lat
%    lon_s = "%.2f" % lon
%    url = 'http://%s/map/#zoom=16&lat=%s&lon=%s&item=%s&level=%s&issue_uuid=%s' % (website, lat, lon, item, level, res["uuid"])
        <link>{{url}}</link>
        <guid>http://{{website}}/error/{{res['uuid']}}</guid>
    </item>
%end
</channel>
</rss>
