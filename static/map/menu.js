function setCookie(c_name, value, exdays) {
  var exdate = new Date();
  exdate.setDate(exdate.getDate() + exdays);
  var c_value = escape(value) + ((exdays == null) ? "" : "; path=/; expires=" + exdate.toUTCString());
  document.cookie = c_name + "=" + c_value;
}

function set_lang(select) {
  var lang = $(select).val();
  window.location.href = "../" + lang + "/map/" + window.location.search;
}

function getUrlVars() {
  var vars = {},
    hash;
  if (window.location.href.indexOf('#') >= 0) {
    var hashes = window.location.href.slice(window.location.href.indexOf('#') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
      hash = hashes[i].split('=');
      vars[hash[0]] = hash[1];
    }
  }
  return vars;
}
