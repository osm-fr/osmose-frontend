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
