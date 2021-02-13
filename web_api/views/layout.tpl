<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
%if 'translate' in vars():
<html lang="{{translate.languages[0]}}" dir="{{translate.direction}}">
%else:
<html>
%end
<head>
  <title>Osmose</title>
  <meta name="description" id="description">
  <meta name="viewport" id="viewport">
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
%from web_api.assets import assets
%from web_api.app import app
  <script type="text/javascript" src="{{app.get_url('static', filename='assets/' + assets['app'])}}"></script>
  <link rel="icon" id="favicon" type="image/png" href="{{app.get_url('static', filename='favicon.png')}}">
</head>
<body>
<div id="app">Loading...</div>
</body>
</html>
