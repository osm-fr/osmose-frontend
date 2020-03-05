$(document).ready(() => {
  $('a.err_delete').click((event) => {
    $('#load').fadeIn();
    const Container = $(event.currentTarget).parent();
    const id = $(event.currentTarget).attr('id').split('=');
    const verb = id[0];
    const path = id[1];

    $.ajax({
      type: verb,
      url: `../api/0.3beta/${path}`,
      cache: false,
      beforeSend() {
        Container.parent().css({ backgroundColor: 'red' });
      },
      success: (response) => {
        Container.parent().find('td')
          .wrapInner('<div style="display: block;" />')
          .parent()
          .find('td > div')
          .slideUp(700, () => $(event.currentTarget).parent().parent().remove());
      },
      error: (xhr, ajaxOptions, thrownError) => {
        Container.parent().css({ backgroundColor: '' });
      },
    });

    return false;
  });
});
