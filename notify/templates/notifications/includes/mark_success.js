var markSuccess = function (response, notification) {
    //console.log(response);
    if (response.action == 'read') {
        var mkClass = readNotificationClass;
        var rmClass = unreadNotificationClass;
        var action = 'unread';
    } else {
        mkClass = unreadNotificationClass;
        rmClass = readNotificationClass;
        action = 'read';
    }
    console.log(notification.closest(nfClassSelector));
    notification.closest(nfSelector).removeClass(rmClass).addClass(mkClass);
    notification.attr('data-mark-action', action);
    notification.html('Mark as '+ action);
};