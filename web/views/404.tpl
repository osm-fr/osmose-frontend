%rebase('layout.tpl', title="Error: 404 Not Found")
<h1>Error: 404 Not Found</h1>
<p>File does not exist.</p>
<ul>
%import bottle, urllib
% routes = [i[0] for i in bottle.default_app().router.dyna_routes.get("GET", [])]
% routes.extend(bottle.default_app().router.static.get("GET", []))
% routes.sort()
%for rule in routes:
    <li><a href="{{bottle.default_app().get_url('root')[0:-1]+urllib.quote(rule)}}">{{rule}}</a></li>
%end
<ul>
