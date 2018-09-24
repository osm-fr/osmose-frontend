$(document).ready(() => {
  $('a.err_delete').click(function () {
    $('#load').fadeIn();
    const Container = $(this).parent();
    const id = $(this).attr('id').split('=');
    const verb = id[0];
    const path = id[1];

    $.ajax({
      type: verb,
      url: `../api/0.2/${path}`,
      cache: false,
      beforeSend() {
        Container.parent().css({ backgroundColor: 'red' });
      },
      success(response) {
        Container.parent().find('td')
          .wrapInner('<div style="display: block;" />')
          .parent()
          .find('td > div')
          .slideUp(700, () => {
            $(this).parent().parent().remove();
          });
      },
      error(xhr, ajaxOptions, thrownError) {
        Container.parent().css({ backgroundColor: '' });
      },
    });

    return false;
  });
});
