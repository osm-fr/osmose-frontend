<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
%if 'translate' in vars():
<html lang="{{translate.languages[0]}}" dir="{{translate.direction}}">
%else:
<html>
%end
<head>
  <title>Osmose - {{title or ''}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
%from web.assets import assets
%from web.app import app
  <script type="text/javascript" src="{{app.get_url('static', filename=assets['static'][0])}}"></script>
%if not 'favicon' in locals() or not favicon:
%    favicon = app.get_url('static', filename='favicon.png')
%end
  <link rel="icon" type="image/png" href="{{favicon}}">
%if 'rss' in locals() and rss:
  <link href="{{rss}}" rel="alternate" type="application/rss+xml" title="Osmose - {{title or ''}}">
%end
</head>
<body>
%include
</body>
</html>
