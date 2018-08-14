function err_delete(type, id) {
    var b = $("div#popup-" + marker_id).parent().parent().parent();
    b.hide();
}

$(document).ready(function() {
  $("a.err_delete").click(function() {
    $('#load').fadeIn();
    var Container = $(this).parent();
    var id = $(this).attr("id").split("=");
    verb = id[0];
    path = id[1];

    $.ajax({
      type: verb,
      url: "../api/0.2/" + path,
      cache: false,
      beforeSend: function() {
        Container.parent().css({"backgroundColor":"red"})
      },
      success: function(response){
        Container.parent().find('td')
          .wrapInner('<div style="display: block;" />')
          .parent()
          .find('td > div')
          .slideUp(700, function(){
              $(this).parent().parent().remove();
          })
      },
      error: function (xhr, ajaxOptions, thrownError) {
        Container.parent().css({"backgroundColor":""});
      }
    });

    return false;
  });
});
