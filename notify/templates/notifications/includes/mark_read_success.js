var markReadSuccess = function (response, notification) {
    //console.log(response);
    var mkClass = readNotificationClass;
    var rmClass = unreadNotificationClass;
    // console.log(notification.closest(nfClassSelector));
    notification.closest(nfSelector).removeClass(rmClass).addClass(mkClass);

    toggle_text = notification.attr('data-toggle-text') || '';
    notification.attr('data-toggle-text', notification.html());
    notification.html(toggle_text);

    if (response.status === 200) {
      $('.notification-badge').each(function() {
        notificationCount = parseInt($(this).text()) - 1;
        $(this).text(notificationCount);
      });
    }

    $('[data-nf-id='+notification.attr('data-id')+']').css({'color': '#e0e0e0'});
    $(markNotificationSelector+'[data-id='+notification.attr('data-id')+']').css({'color': '#e0e0e0'});
    $(markLinkNotificationSelector+'[data-id='+notification.attr('data-id')+']').css({'opacity': '0.6'});
};
