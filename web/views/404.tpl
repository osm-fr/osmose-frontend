%rebase('layout.tpl', title="Error: 404 Not Found")
<h1>Error: 404 Not Found</h1>
<p>File does not exist.</p>
<ul>
%import bottle, urllib, modules.osmose_bottle
%for prefixes, route in modules.osmose_bottle.inspect_routes(bottle.default_app()):
  <li>
    <a href="{{urllib.quote('/'.join(prefixes).rstrip('/') + route.rule)}}">
      {{'/'.join(prefixes).rstrip('/')}}{{route.rule}}
    </a>
  </li>
%end
<ul>
