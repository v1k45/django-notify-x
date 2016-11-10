var deleteSuccess = function (response, notification) {
    //console.log(response);
    var $selected_notification = $('[data-nf-id='+notification.attr('data-id')+']');

    if (response.status === 200) {
      $('.notification-badge').each(function() {
        notificationCount = parseInt($(this).text()) - response.read;
        $(this).text(notificationCount);
      });
    }

    $selected_notification.parent().remove()
};
