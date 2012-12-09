%rebase layout title="Error: 404 Not Found"
<h1>Error: 404 Not Found</h1>
<p>File does not exist.</p>
<ul>
%import bottle, urllib, cgi
% routes = bottle.default_app().router.rules.keys()
% routes.sort()
%for rule in routes:
    <li><a href="{{bottle.default_app().get_url('root')[0:-1]+urllib.quote(rule)}}">{{rule}}</a></li>
%end
<ul>
