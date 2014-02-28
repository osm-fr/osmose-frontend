<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Osmose - {{username}}</title>
    <description>{{_("Statistics for user %s") % username}}</description>
    <lastBuildDate></lastBuildDate>
    <link>http://{{website}}/byuser/{{username}}</link>
    <item>
        <title>{{_("Number of level 1 errors: %d") % count[1]}}</title>
    </item>
    <item>
        <title>{{_("Number of level 2 errors: %d") % count[2]}}</title>
    </item>
    <item>
        <title>{{_("Number of level 3 errors: %d") % count[3]}}</title>
    </item>
</channel>
</rss>
