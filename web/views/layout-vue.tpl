<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
%if 'translate' in vars():
<html lang="{{translate.languages[0]}}" dir="{{translate.direction}}">
%else:
<html>
%end
<head>
  <title>Osmose</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
%from web.assets import assets
%from web.app import app
  <script type="text/javascript" src="{{app.get_url('static', filename='dist/' + assets['app'])}}"></script>
  <link rel="icon" id="favicon" type="image/png" href="{{app.get_url('static', filename='favicon.png')}}">
</head>
<body>
<div id="app">Loading...</div>
</body>
</html>
