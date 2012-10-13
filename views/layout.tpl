<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>Osmose - {{title or ''}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='css/style.css')}}">
  <script src="{{get_url('static', filename='js/sorttable.js')}}" type="text/javascript"></script>
%if 'css' in locals() and css:
  <link rel="stylesheet" href="{{get_url('static', filename=css)}}" type="text/css" />
%end
</head>
%include
<body>
</body>
</html>
