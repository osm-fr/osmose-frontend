<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="/map/style.css">
  
  <style type="text/css">
    .div_text {
      border-width: 1px 1px 1px 1px;
      border-style: solid;
      border-collapse: collapse;
      width: 280px;
      height: 360px;
      float: left;
      }
  </style>			    

  <script type="text/javascript">

    var pois = {
      loadText : function () {
      }
    };

    function iFrameLoad(url) {
      document.getElementById('incFrame').src = url;
      document.getElementById('incFrame').style.visibility = null;
      document.getElementById('incFrameBt').style.visibility = null;
      document.getElementById('incFrameBg').style.visibility = null;
    }
    
    function iFrameClose(url) {
      document.getElementById('incFrame').style.visibility   = 'hidden';
      document.getElementById('incFrameBt').style.visibility = 'hidden';
      document.getElementById('incFrameBg').style.visibility = 'hidden';
    }
    
  </script>
  
</head>

<body>

<iframe style="display:none" id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg" style="opacity:0.75;visibility:hidden;position:absolute;top:0;bottom:0;left:0;right:0;background-color:#000000;z-index:1199;"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" style="position:absolute;z-index:1200;top:10;left:10;visibility:hidden;" frameborder="1" ></iframe>
<img id="incFrameBt" src="http://osmose.openstreetmap.fr/map/close.png" style="visibility:hidden;border:0px;position:absolute;z-index:1201;top:10;left:772;" onclick="iFrameClose();">
<a accesskey="w" style="visibility:hidden;" href="javascript:iFrameClose();">iframeclose</a>

#data#

</body>
</html>
